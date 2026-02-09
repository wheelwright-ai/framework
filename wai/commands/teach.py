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
from ..upgrade_adoption import UpgradeAdoptionPlanBuilder, sign_upgrade_plan, save_upgrade_plan
from ..utils.input import print_info, print_success, print_error, print_warning
from ..core import FRAMEWORK_VERSION
from ..observation import get_logger, log_observation


def teach_command(spoke_path: Path, hub_path: Optional[Path], framework_path: Path) -> bool:
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
    
    # Log plan generation start
    log_observation(
        logger=logger,
        action_id="teach.plan",
        action_category="framework",
        description="Generate upgrade adoption plan",
        session_id=session_id,
        agent="TeachCommand",
        tags=["teaching"]
    )
    
    wai_spoke_templates_dir = framework_path / 'templates' / 'WAI-Spoke'
    wai_hub_templates_dir = framework_path / 'templates' / 'HUB'
    
    if not wai_spoke_templates_dir.exists():
        print_error(f"  Framework templates not found at {wai_spoke_templates_dir}")
        return False
    
    # Determine if hub is being taught (has WAI-Spoke/ structure)
    is_hub_target = hub_path and (hub_path / 'WAI-Spoke').exists() if hub_path else False
    
    print_info("  Generating Upgrade Adoption Plan...")
    if is_hub_target:
        print_info(f"  Teaching both spoke ({spoke_path.name}) and hub ({hub_path.name})")
    
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
    plan = builder.build()
    
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
    log_observation(
        logger=logger,
        action_id="teach.distribute",
        action_category="framework",
        description="Distribute files to spoke/hub",
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
    
    # Distribute spoke files
    for file_config in spoke_files:
        src_path = wai_spoke_templates_dir / file_config['name']
        if src_path.exists():
            try:
                dst = teach_manager.ingest_dir / f"{file_config['name']}.teaching"
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
    
    # Distribute any waiting lugs from hub/outbound/[spoke-id]/
    lugs_distributed = 0
    if hub_path:
        try:
            # Get spoke_id from WAI-State.json if available
            spoke_state_path = spoke_path / 'WAI-Spoke' / 'WAI-State.json'
            spoke_id = spoke_path.name  # fallback
            if spoke_state_path.exists():
                try:
                    state = json.loads(spoke_state_path.read_text(encoding='utf-8'))
                    spoke_id = state.get('_spoke_id', spoke_path.name)
                except Exception:
                    pass
            
            outbound_spoke_dir = hub_path / 'WAI-Hub' / 'outbound' / spoke_id
            if outbound_spoke_dir.exists() and outbound_spoke_dir.is_dir():
                ingest_dir = teach_manager.ingest_dir
                lug_files = list(outbound_spoke_dir.glob('*.jsonl'))
                
                if lug_files:
                    print_info("\n  Distributing Lugs from Hub...")
                    for lug_file in lug_files:
                        try:
                            dst = ingest_dir / lug_file.name
                            shutil.copy2(lug_file, dst)
                            print_success(f"    [OK] {lug_file.name} (lug) → /seed/ingest/")
                            lugs_distributed += 1
                            # Remove from outbound after successful distribution
                            lug_file.unlink()
                        except Exception as e:
                            print_warning(f"    Failed to distribute lug {lug_file.name}: {e}")
        except Exception as e:
            print_warning(f"  Warning: Could not process hub lugs: {e}")
    
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
    log_observation(
        logger=logger,
        action_id="teach.complete",
        action_category="framework",
        description="Teaching complete",
        status="✓ COMPLETE",
        session_id=session_id,
        agent="TeachCommand",
        tags=["teaching"]
    )
    
    print_success(f"\n  [OK] Observations logged for session: {session_id}")
    return True

