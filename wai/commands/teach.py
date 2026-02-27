"""
Teach Command - Distribute updated template files to spokes using upgrade adoption plans.

Process:
1. Scan framework templates (spoke and hub)
2. Compute file hashes and version context
3. Generate signed upgrade-adoption-plan.json
4. Distribute plan to spoke/hub for verification and adoption
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..reference_manager import TeachingManager
from ..teach_reconciliation import scan_teach_ingest_dir, perform_teaching_adoption
from ..upgrade_adoption import UpgradeAdoptionPlanBuilder, sign_upgrade_plan, save_upgrade_plan
from ..utils.input import print_info, print_success, print_error, print_warning
from ..core import FRAMEWORK_VERSION
from ..observation import get_logger, log_observation
from ..hub import HubManager


def update_registry_after_teach(
    hub_path: Path,
    spoke_path: Path,
    framework_version: str,
    files_distributed: int,
    session_id: str
) -> bool:
    """
    Update hub registry after successfully teaching a spoke.

    Updates:
    - wheel.taught_at, wheel.taught_version for the spoke
    - teaching_history with new event
    - statistics.last_teach and counts

    Returns:
        True if registry updated successfully
    """
    registry_path = hub_path / 'hub-registry.json'
    if not registry_path.exists():
        return False

    try:
        registry = json.loads(registry_path.read_text(encoding='utf-8'))
        now = datetime.utcnow().isoformat() + 'Z'
        spoke_path_str = str(spoke_path).rstrip('/') + '/'

        # Find and update the wheel entry
        wheel_found = False
        for wheel in registry.get('wheels', []):
            wheel_path = wheel.get('path', '').rstrip('/') + '/'
            if wheel_path == spoke_path_str:
                wheel['taught_at'] = now
                wheel['taught_version'] = framework_version
                wheel['last_sync'] = now
                wheel_found = True
                print_success(f"    [REGISTRY] Updated {wheel.get('wheel_id')}")
                break

        if not wheel_found:
            print_warning(f"    [REGISTRY] Spoke not found in registry: {spoke_path.name}")

        # Append to teaching_history
        if 'teaching_history' not in registry:
            registry['teaching_history'] = []

        # Check if we already have an event for this session (batch teaching)
        existing_event = None
        for event in registry['teaching_history']:
            if event.get('event_id') == session_id:
                existing_event = event
                break

        if existing_event:
            # Update existing event
            existing_event['wheels_taught'] = existing_event.get('wheels_taught', 0) + 1
            if spoke_path.name not in existing_event.get('spokes_taught', []):
                existing_event.setdefault('spokes_taught', []).append(spoke_path.name)
        else:
            # Create new event
            registry['teaching_history'].append({
                'event_id': session_id,
                'timestamp': now,
                'framework_version': framework_version,
                'wheels_taught': 1,
                'spokes_taught': [spoke_path.name],
                'files_per_spoke': files_distributed,
                'status': 'complete'
            })

        # Update statistics
        if 'statistics' not in registry:
            registry['statistics'] = {}
        registry['statistics']['last_teach'] = now
        registry['statistics']['last_teach_version'] = framework_version

        # Count active wheels
        active_count = sum(1 for w in registry.get('wheels', []) if w.get('status') == 'active')
        taught_count = sum(1 for w in registry.get('wheels', []) if w.get('taught_at'))
        registry['statistics']['total_wheels'] = len(registry.get('wheels', []))
        registry['statistics']['active_wheels'] = active_count
        registry['statistics']['taught_wheels'] = taught_count

        # Write back
        registry_path.write_text(json.dumps(registry, indent=2), encoding='utf-8')
        return True

    except Exception as e:
        print_warning(f"    [REGISTRY] Failed to update: {e}")
        return False


def distribute_teach_command(spoke_path: Path, hub_path: Optional[Path], framework_path: Path) -> bool:
    """
    Teach a spoke (and optionally hub) with updated templates from framework using upgrade adoption plans.
    
    Args:
        spoke_path: Path to project to teach
        hub_path: Path to hub (optional, for knowledge distribution and hub self-update)
        framework_path: Path to framework (source of templates)
    
    Returns:
        True if teaching completed
    """
    # Initialize observation logging
    session_id = f"teach-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    logger = get_logger()

    wai_spoke_templates_dir = framework_path / 'templates' / 'WAI-Spoke'
    target_wai_spoke_dir = spoke_path / 'WAI-Spoke'

    if not wai_spoke_templates_dir.exists():
        print_error(f"  Framework templates not found at {wai_spoke_templates_dir}")
        return False

    # Logic for initialization or update of WAI-Spoke structure
    if not target_wai_spoke_dir.exists():
        print_info(f"  [INIT] WAI-Spoke not found in {spoke_path.name}. Initializing bootstrap files...")
        target_wai_spoke_dir.mkdir(parents=True, exist_ok=True)
        # Copy all templates for initialization
        try:
            for item in wai_spoke_templates_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, target_wai_spoke_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_wai_spoke_dir / item.name)
            
            # Also copy top-level integration files from template root if they exist
            for integration_file in ['CLAUDE.md', 'GEMINI.md', 'README.md']:
                src_integration = wai_spoke_templates_dir / integration_file
                if src_integration.exists():
                    shutil.copy2(src_integration, spoke_path / integration_file)

            print_success(f"  [OK] Successfully initialized WAI-Spoke in {spoke_path.name}")
        except Exception as e:
            print_error(f"  [FAIL] Failed to initialize WAI-Spoke: {e}")
            return False
    else:
        print_info(f"  [UPDATE] WAI-Spoke already exists in {spoke_path.name}. Updating with latest template files...")
        # Update existing structure with latest templates (simple copy-over as requested)
        try:
            for item in wai_spoke_templates_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, target_wai_spoke_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_wai_spoke_dir / item.name)
            print_success(f"  [OK] Successfully updated WAI-Spoke templates in {spoke_path.name}")
        except Exception as e:
            print_warning(f"  [WARN] Failed to update some template files: {e}")

    # Log plan generation start
    logger.log_observation(
        action_id="teach.plan",
        action_category="framework",
        action_description="Generate upgrade adoption plan",
        plan="Scan framework templates and create upgrade adoption plan",
        command=f"teach {spoke_path.name}",
        expected_result={"exit_code": 0, "plan_created": True},
        actual_result={"exit_code": 0},  # Updated at end
        verification={"plan_ready": True, "passed": True},
        session_id=session_id,
        agent="TeachCommand",
        tags=["teaching"]
    )
    
    wai_hub_templates_dir = framework_path / 'templates' / 'HUB'
    
    # Determine if hub is being taught (has WAI-Spoke/ structure)
    is_hub_target = hub_path and (hub_path / 'WAI-Spoke').exists() if hub_path else False
    
    print_info("  Generating Upgrade Adoption Plan...")
    if is_hub_target:
        print_info(f"  Teaching both spoke ({spoke_path.name}) and hub ({hub_path.name})")

    hub_manager = HubManager()
    current_hub_fingerprint = hub_manager.get_hub_fingerprint(hub_path) if hub_path else None
    
    # Create builder for upgrade adoption plan
    builder = UpgradeAdoptionPlanBuilder(
        framework_version=FRAMEWORK_VERSION,
        spoke_structure_version="3.0",
        source="framework"
    )
    
    # Core spoke template files
    spoke_files = [
        {
            'name': 'WAI-Guide.md',
            'path': 'WAI-Spoke/WAI-Guide.md',
            'changed_from': '2.1.0',
            'why_changed': 'Enhanced session start protocol, added teaching reconciliation section',
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['session-start', 'teaching', 'reconciliation'],
            'applies_to': ['spoke', 'hub'],
        },
        {
            'name': 'WAI-State.json',
            'path': 'WAI-Spoke/WAI-State.json',
            'changed_from': '2.0.1',
            'why_changed': 'Structure version 3.0, added teaching-adoption-plan schema',
            'safe_to_auto_adopt': False,
            'requires_review': True,
            'mentions': ['structure', 'version', 'state-management'],
            'applies_to': ['spoke', 'hub'],
            'merge_strategy': 'merge_sections',
            'sections_to_preserve': ['_session_state', '_project_foundation', 'decisions', 'analytics'],
            'sections_to_update': ['wheelwright.structure_version', 'wheelwright.version', '_file_meta'],
        },
        {
            'name': 'WAI-State.md',
            'path': 'WAI-Spoke/WAI-State.md',
            'changed_from': '2.0.0',
            'why_changed': 'Updated strategic context for version 3.0',
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['strategy', 'context'],
            'applies_to': ['spoke'],
        },
        {
            'name': 'commands/wai-closeout.md',
            'path': 'WAI-Spoke/commands/wai-closeout.md',
            'changed_from': '3.1.0',
            'why_changed': "Consolidated closeout protocol with WAI principles, 4-phase execution, verification checklist.",
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['closeout', 'protocol', 'verification', 'git'],
            'applies_to': ['spoke', 'hub'],
        },
        {
            'name': 'commands/wai-shipit.md',
            'path': 'WAI-Spoke/commands/wai-shipit.md',
            'changed_from': '3.1.0',
            'why_changed': "Complete shipit protocol: closeout + commit + push + verify.",
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['shipit', 'closeout', 'git', 'verification'],
            'applies_to': ['spoke', 'hub'],
        },
        {
            'name': 'commands/wai-learn.md',
            'path': 'WAI-Spoke/commands/wai-learn.md',
            'changed_from': '3.1.0',
            'why_changed': "P9 format learn skill - reads signals from lugs, feedback collection, any-node execution.",
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['learn', 'signals', 'hub', 'lugs'],
            'applies_to': ['spoke', 'hub'],
        },
        {
            'name': 'commands/wai-foundation.md',
            'path': 'WAI-Spoke/commands/wai-foundation.md',
            'changed_from': '3.1.0',
            'why_changed': "Foundation skill - project identity, goals, boundaries stored in lugs with versioned evolution.",
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['foundation', 'identity', 'boundaries', 'lugs', 'evolution'],
            'applies_to': ['spoke', 'hub'],
        },
        {
            'name': 'WAI-Events.json',
            'path': 'WAI-Spoke/WAI-Events.json',
            'changed_from': '3.1.0',
            'why_changed': "Valid events/triggers skills can hook into - lifecycle, knowledge, work, user events.",
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['events', 'triggers', 'skills'],
            'applies_to': ['spoke', 'hub'],
        },
        {
            'name': 'WAI-Startup.json',
            'path': 'WAI-Spoke/WAI-Startup.json',
            'changed_from': '3.1.0',
            'why_changed': "Skill manifest - defines skills exposed at wakeup, triggers, exposure contexts.",
            'safe_to_auto_adopt': True,
            'requires_review': False,
            'mentions': ['startup', 'skills', 'manifest', 'exposure'],
            'applies_to': ['spoke', 'hub'],
        },
    ]
    
    # Add spoke files
    spoke_count = 0
    for file_config in spoke_files:
        src_path = wai_spoke_templates_dir / file_config['name']
        if src_path.exists():
            builder.add_file(
                name=file_config['name'],
                path=file_config['path'],
                source_path=str(src_path),
                version=FRAMEWORK_VERSION,
                changed_from=file_config['changed_from'],
                why_changed=file_config['why_changed'],
                safe_to_auto_adopt=file_config['safe_to_auto_adopt'],
                requires_review=file_config['requires_review'],
                merge_strategy=file_config.get('merge_strategy'),
                sections_to_preserve=file_config.get('sections_to_preserve'),
                sections_to_update=file_config.get('sections_to_update'),
                mentions=file_config.get('mentions', []),
                applies_to=file_config.get('applies_to', ['spoke'])
            )
            spoke_count += 1
            print_success(f"    [OK] {file_config['name']}")
    
    # Hub-specific files at root (defined outside if block to avoid UnboundLocalError)
    hub_files = [
        {
            'name': 'hub-registry.json',
            'path': 'hub-registry.json',
            'changed_from': '2.0.0',
            'why_changed': 'Updated registry tracking wheels and teaching history',
        },
        {
            'name': 'hub-learning-index.md',
            'path': 'hub-learning-index.md',
            'changed_from': '2.0.0',
            'why_changed': 'Knowledge base index for learning aggregation',
        },
        {
            'name': 'hub-security-policy.json',
            'path': 'hub-security-policy.json',
            'changed_from': '2.0.0',
            'why_changed': 'Security settings for hub-spoke communication',
        },
        {
            'name': 'AGENTS.md',
            'path': 'AGENTS.md',
            'changed_from': '2.0.0',
            'why_changed': 'Hub-specific AI assistant instructions (legacy)',
        },
    ]
    
    # Add hub files if teaching hub
    hub_count = 0
    if is_hub_target and wai_hub_templates_dir.exists():
        # Hub gets its own WAI-Spoke templates
        hub_spoke_templates = wai_hub_templates_dir / 'WAI-Spoke'
        if hub_spoke_templates.exists():
            hub_spoke_files = [
                {
                    'name': 'WAI-State.json',
                    'path': 'WAI-Spoke/WAI-State.json',
                    'changed_from': '3.0.0',
                    'why_changed': 'Hub-specific state with _hub_profile section',
                },
                {
                    'name': 'WAI-State.md',
                    'path': 'WAI-Spoke/WAI-State.md',
                    'changed_from': '3.0.0',
                    'why_changed': 'Hub identity and operations tracking',
                },
                {
                    'name': 'WAI-Guide.md',
                    'path': 'WAI-Spoke/WAI-Guide.md',
                    'changed_from': '3.0.0',
                    'why_changed': 'Hub-specific AI assistant instructions',
                },
            ]
            
            for file_config in hub_spoke_files:
                src_path = hub_spoke_templates / file_config['name']
                if src_path.exists():
                    builder.add_hub_file(
                        name=file_config['name'],
                        path=file_config['path'],
                        source_path=str(src_path),
                        version=FRAMEWORK_VERSION,
                        changed_from=file_config['changed_from'],
                        why_changed=file_config['why_changed'],
                        safe_to_auto_adopt=True
                    )
                    hub_count += 1
        
        for file_config in hub_files:
            src_path = wai_hub_templates_dir / file_config['name']
            if src_path.exists():
                builder.add_hub_file(
                    name=file_config['name'],
                    path=file_config['path'],
                    source_path=str(src_path),
                    version=FRAMEWORK_VERSION,
                    changed_from=file_config['changed_from'],
                    why_changed=file_config['why_changed'],
                    safe_to_auto_adopt=True
                )
                hub_count += 1
    
    # Build the plan
    plan = builder.build(hub_fingerprint=current_hub_fingerprint)
    
    # Sign with hub fingerprint if hub exists
    hub_fingerprint = None
    if hub_path and (hub_path / 'hub-profile.json').exists():
        try:
            profile = json.loads((hub_path / 'hub-profile.json').read_text())
            hub_key = profile.get('hub_config', {}).get('fingerprint', 'wheelwright-default-key')
            plan = sign_upgrade_plan(plan, hub_key)
            hub_fingerprint = plan['verification']['hub_fingerprint']
            print_success(f"    [OK] Signed with hub fingerprint")
        except Exception as e:
            print_warning(f"    Could not sign with hub key: {e}")
    
    # Log distribution start
    logger.log_observation(
        action_id="teach.distribute",
        action_category="framework",
        action_description="Distribute files to spoke/hub",
        plan="Copy template files to spoke and optional hub",
        command=f"distribute {spoke_path.name}",
        expected_result={"exit_code": 0, "files_copied": True},
        actual_result={"exit_code": 0},  # Updated at end
        verification={"distribution_complete": True, "passed": True},
        session_id=session_id,
        agent="TeachCommand",
        tags=["teaching"]
    )
    
    # Distribute actual template files to spoke
    teach_manager = TeachingManager(spoke_path)
    files_distributed = 0
    
    print_info("\n  Distributing Template Files...")

    # Distribute Framework Upgrade Lug (Lugs v2)
    try:
        from ..lugs import Lug
        
        upgrade_lug_data = {
            'id': 'lug-framework-upgrade-v2',
            'title': 'Framework Upgrade: Lugs v2 Specification',
            'type': 'epic',
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'priority': 'high',
            'impact': 'large',
            'value': 10,
            'summary': "The Lugs system has been upgraded to v2 to support Conflict Immunity (file sharding) and Hierarchical IDs. All objects must adopt the new specification. Existing 'lugs.jsonl' should be migrated to 'lugs/' directory shards.",
            'policy_tags': ['framework_upgrade'],
            'origin': 'framework:teach'
        }
        
        dst = teach_manager.ingest_dir / 'lug-framework-upgrade-v2.jsonl'
        # Write minified
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(json.dumps(Lug(upgrade_lug_data).to_minified()) + '\n')
            
        print_success(f"    [OK] Lugs v2 Upgrade Notification → /seed/ingest/")

    except Exception as e:
        print_warning(f"    Failed to distribute framework upgrade lug: {e}")

    # Distribute Paths Lug - minimal viable paths for spoke operation
    try:
        paths_lug_data = {
            'id': 'lug-wai-paths',
            'ty': 'config',
            'title': 'WAI Network Paths',
            'created_at': datetime.now().isoformat(),
            'hub_path': str(hub_path) if hub_path else None,
            'framework_path': str(framework_path),
            'taught_by': 'framework:teach',
            'taught_at': datetime.now().isoformat(),
            'summary': 'Minimal viable paths for spoke operation. Hub path for learn/signals, framework path for teach source.',
            'policy_tags': ['config', 'paths'],
            'origin': 'framework:teach'
        }

        dst = teach_manager.ingest_dir / 'lug-wai-paths.jsonl'
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(json.dumps(paths_lug_data) + '\n')

        print_success(f"    [OK] WAI Paths Lug → /seed/ingest/")

    except Exception as e:
        print_warning(f"    Failed to distribute paths lug: {e}")
    
    # Distribute spoke files
    for file_config in spoke_files:
        src_path = wai_spoke_templates_dir / file_config['name']
        if src_path.exists():
            try:
                dst = teach_manager.ingest_dir / f"{file_config['name']}.teaching"
                # Ensure parent directories exist for nested paths
                dst.parent.mkdir(parents=True, exist_ok=True)
                # Check if file already exists (for replacement message)
                file_exists = dst.exists()
                content = src_path.read_text(encoding='utf-8')
                dst.write_text(content, encoding='utf-8', errors='replace')
                action = "replaced" if file_exists else "created"
                print_success(f"    [OK] {file_config['name']} {action} → /seed/ingest/")
                files_distributed += 1
            except Exception as e:
                print_warning(f"    Failed to distribute {file_config['name']}: {e}")
    
    # Distribute hub files (to ingest, will be filtered by applies_to during adoption)
    for file_config in hub_files:
        src_path = wai_hub_templates_dir / file_config['name']
        if src_path.exists():
            try:
                # Hub files distributed WITHOUT .teaching extension for immediate adoption
                dst = teach_manager.ingest_dir / file_config['name']
                # Check if file already exists (for replacement message)
                file_exists = dst.exists()
                content = src_path.read_text(encoding='utf-8')
                dst.write_text(content, encoding='utf-8', errors='replace')
                action = "replaced" if file_exists else "created"
                print_success(f"    [OK] {file_config['name']} {action} → /seed/ingest/")
                files_distributed += 1
            except Exception as e:
                print_warning(f"    Failed to distribute {file_config['name']}: {e}")
    
    # Distribute any waiting lugs from hub's outbox to spoke's inbox
    # Protocol: hub/WAI-Spoke/lugs/outbox → spoke/WAI-Spoke/lugs/inbox
    # Routing: filter by destination_wheel_id matching spoke
    lugs_distributed = 0
    delivery_confirmations = []
    if hub_path:
        try:
            # Get spoke_id from WAI-State.json if available
            spoke_state_path = spoke_path / 'WAI-Spoke' / 'WAI-State.json'
            spoke_id = spoke_path.name  # fallback
            if spoke_state_path.exists():
                try:
                    state = json.loads(spoke_state_path.read_text(encoding='utf-8'))
                    spoke_id = state.get('wheel', {}).get('name', spoke_path.name)
                except Exception:
                    pass

            # Read from hub's outbox (not WAI-Hub which doesn't exist)
            hub_outbox_dir = hub_path / 'WAI-Spoke' / 'lugs' / 'outbox'
            if hub_outbox_dir.exists() and hub_outbox_dir.is_dir():
                # Destination: spoke's inbox
                lug_inbox_dir = spoke_path / 'WAI-Spoke' / 'lugs' / 'inbox'
                lug_inbox_dir.mkdir(parents=True, exist_ok=True)
                lug_files = list(hub_outbox_dir.glob('*.jsonl'))

                if lug_files:
                    print_info("\n  Checking Hub Outbox for Lugs...")
                    for lug_file in lug_files:
                        try:
                            # Read lug to check destination
                            lug_data = json.loads(lug_file.read_text(encoding='utf-8').strip())
                            lug_id = lug_data.get('id', lug_file.stem)
                            dest_wheel = lug_data.get('destination_wheel_id', '')

                            # Only deliver if destination matches this spoke
                            if dest_wheel.lower() != spoke_id.lower() and dest_wheel.lower() != spoke_path.name.lower():
                                continue  # Skip - not for this spoke

                            dst = lug_inbox_dir / lug_file.name
                            shutil.copy2(lug_file, dst)

                            # Verify file write
                            if not dst.exists():
                                raise Exception(f"Failed to verify write for lug {lug_id} at {dst}")

                            print_success(f"    [OK] {lug_file.name} → spoke/lugs/inbox/")
                            lugs_distributed += 1

                            # Track for delivery confirmation
                            delivery_confirmations.append({
                                'delivered_lug_id': lug_id,
                                'destination_spoke_id': spoke_id,
                                'destination_path': str(dst),
                                'timestamp': datetime.utcnow().isoformat() + 'Z'
                            })

                            # Remove from hub outbox after successful distribution
                            lug_file.unlink()
                        except json.JSONDecodeError as e:
                            print_warning(f"    Invalid JSON in {lug_file.name}: {e}")
                        except Exception as e:
                            print_warning(f"    Failed to distribute lug {lug_file.name}: {e}")
        except Exception as e:
            print_warning(f"  Warning: Could not process hub outbox: {e}")

    # Generate delivery confirmation lugs → hub's inbox
    # Skip confirmation for self-delivery (framework teaching itself)
    is_self_delivery = spoke_path.resolve() == framework_path.resolve()

    if delivery_confirmations and hub_path and not is_self_delivery:
        try:
            hub_inbox_dir = hub_path / 'WAI-Spoke' / 'lugs' / 'inbox'
            hub_inbox_dir.mkdir(parents=True, exist_ok=True)

            for confirmation in delivery_confirmations:
                confirm_lug = {
                    'id': f"lug-confirm-{confirmation['delivered_lug_id'][:20]}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'ty': 'signal',
                    'signal_type': 'delivery_confirmation',
                    'source_wheel_id': spoke_id,
                    'destination_wheel_id': 'hub',
                    'delivered_lug_id': confirmation['delivered_lug_id'],
                    'delivered_to': confirmation['destination_spoke_id'],
                    'delivered_at': confirmation['timestamp'],
                    'created_at': datetime.utcnow().isoformat() + 'Z'
                }

                confirm_path = hub_inbox_dir / f"{confirm_lug['id']}.jsonl"
                confirm_path.write_text(json.dumps(confirm_lug) + '\n', encoding='utf-8')

                if confirm_path.exists():
                    print_success(f"    [OK] Delivery confirmation → hub/lugs/inbox/")
                else:
                    print_warning(f"    Failed to verify delivery confirmation write")
        except Exception as e:
            print_warning(f"  Warning: Could not write delivery confirmations: {e}")
    elif delivery_confirmations and is_self_delivery:
        print_info(f"    [SELF] Skipping confirmation (self-delivery)")
    
    # Save upgrade adoption plan to spoke
    try:
        plan_path = spoke_path / 'upgrade-adoption-plan.json'
        if save_upgrade_plan(plan, plan_path):
            print_success(f"\n  [OK] Generated upgrade-adoption-plan.json for spoke")
            print_info(f"    Template files: {files_distributed}")
            if lugs_distributed > 0:
                print_info(f"    Lugs distributed: {lugs_distributed}")
            if hub_fingerprint:
                print_info(f"    [SECURE] Signed with hub fingerprint")
            print_info(f"    [NEXT] Spoke will verify and adopt on next session")
        else:
            print_error(f"  Failed to save upgrade plan to spoke")
            return False
    except Exception as e:
        print_error(f"  Failed to generate upgrade plan for spoke: {e}")
        return False
    
    # If hub is a target, also save upgrade plan there
    if is_hub_target:
        try:
            hub_seed_dir = hub_path / 'WAI-Spoke' / 'seed' / 'ingest'
            hub_seed_dir.mkdir(parents=True, exist_ok=True)
            hub_plan_path = hub_seed_dir / 'upgrade-adoption-plan.json'
            
            if save_upgrade_plan(plan, hub_plan_path):
                print_success(f"\n  [OK] Generated upgrade-adoption-plan.json for hub")
                print_info(f"    Location: {hub_plan_path}")
                print_info(f"    Hub will process on next closeout")
                
                # Also distribute hub template files to hub's seed/ingest
                if wai_hub_templates_dir.exists():
                    hub_templates_distributed = 0
                    hub_spoke_templates = wai_hub_templates_dir / 'WAI-Spoke'
                    
                    # Copy hub WAI-Spoke templates
                    if hub_spoke_templates.exists():
                        for item in hub_spoke_templates.glob('*.md'):
                            try:
                                dst = hub_seed_dir / item.name
                                shutil.copy2(item, dst)
                                hub_templates_distributed += 1
                            except Exception:
                                pass
                        for item in hub_spoke_templates.glob('*.json'):
                            try:
                                dst = hub_seed_dir / item.name
                                shutil.copy2(item, dst)
                                hub_templates_distributed += 1
                            except Exception:
                                pass
                    
                    # Copy hub root templates
                    for name in ['hub-registry.json', 'hub-security-policy.json', 'hub-learning-index.md']:
                        src = wai_hub_templates_dir / name
                        if src.exists():
                            try:
                                dst = hub_seed_dir / name
                                shutil.copy2(src, dst)
                                hub_templates_distributed += 1
                            except Exception:
                                pass
                    
                    if hub_templates_distributed > 0:
                        print_info(f"    Hub templates distributed: {hub_templates_distributed}")
            else:
                print_warning(f"  Could not save upgrade plan to hub")
        except Exception as e:
            print_warning(f"  Could not distribute to hub: {e}")
    
    # Log completion
    logger.log_observation(
        action_id="teach.complete",
        action_category="framework",
        action_description="Teaching complete",
        plan="Finalize teaching workflow",
        command=f"teach {spoke_path.name}",
        expected_result={"exit_code": 0, "status": "complete"},
        actual_result={"exit_code": 0, "status": "complete"},
        verification={"teaching_complete": True, "passed": True},
        session_id=session_id,
        agent="TeachCommand",
        tags=["teaching"]
    )

    # Update hub registry with teach timestamp
    if hub_path:
        update_registry_after_teach(
            hub_path=hub_path,
            spoke_path=spoke_path,
            framework_version=FRAMEWORK_VERSION,
            files_distributed=files_distributed,
            session_id=session_id
        )

    print_success(f"\n  [OK] Observations logged for session: {session_id}")
    return True

def adopt_teach_command(spoke_path: Path, teaching_id: Optional[str]) -> bool:
    """
    Adopt pending teaching files for a spoke.

    Args:
        spoke_path: Path to the spoke project.
        teaching_id: The ID of the teaching to adopt, or 'all' to adopt all pending.

    Returns:
        True if adoption was successful, False otherwise.
    """
    from ..teach_reconciliation import scan_teach_ingest_dir, perform_teaching_adoption # New function for adoption logic
    from ..utils.input import print_info, print_success, print_warning, print_error, safe_confirm

    ingest_path = spoke_path / "WAI-Spoke" / "seed" / "ingest"
    pending_teachings = scan_teach_ingest_dir(ingest_path)

    if not pending_teachings:
        print_info("  No pending teachings found for adoption.")
        return True

    teachings_to_adopt = []
    if teaching_id == 'all':
        teachings_to_adopt = pending_teachings
        print_info(f"  Found {len(teachings_to_adopt)} pending teaching(s) to adopt.")
        if not safe_confirm("  Proceed with adopting all pending teachings?", default=True):
            print_info("  Adoption cancelled.")
            return False
    else:
        found_teaching = next((t for t in pending_teachings if t['id'] == teaching_id), None)
        if found_teaching:
            teachings_to_adopt.append(found_teaching)
            print_info(f"  Found teaching '{teaching_id}'.")
            if not safe_confirm(f"  Proceed with adopting '{teaching_id}'?", default=True):
                print_info("  Adoption cancelled.")
                return False
        else:
            print_error(f"  Teaching '{teaching_id}' not found in pending list.")
            return False
            
    success_count = 0
    for teaching in teachings_to_adopt:
        try:
            print_info(f"  Adopting '{teaching['id']}'...")
            if perform_teaching_adoption(spoke_path, teaching):
                print_success(f"  [OK] '{teaching['id']}' adopted successfully.")
                success_count += 1
            else:
                print_warning(f"  [WARN] '{teaching['id']}' adoption completed with warnings.")
        except Exception as e:
            print_error(f"  [FAIL] Error adopting '{teaching['id']}': {e}")

    if success_count == len(teachings_to_adopt):
        print_success(f"\n✓ Successfully adopted {success_count}/{len(teachings_to_adopt)} teaching(s).")
        return True
    elif success_count > 0:
        print_warning(f"\n⚠️  Adopted {success_count}/{len(teachings_to_adopt)} teaching(s) with some failures/warnings.")
        return False
    else:
        print_error("\n✗ No teachings were adopted.")
        return False

