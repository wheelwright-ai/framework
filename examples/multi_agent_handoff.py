
"""
Multi-Agent Handoff Demo
========================

This script demonstrates how WAI Hub acts as a "Shared Brain" for a multi-agent colony.
It simulates two distinct agents operating on the same project state:

1. "The Architect" (Planning Role): Defines the high-level Epic and System Sketch.
2. "The Builder" (Coding Role): Discovers the ready work and creates implementation tasks.

This utilizes the new `agent_id` and `agent_role` tracking in `wai_cli.lugs`.
"""

import sys
import os
import shutil
import time
from pathlib import Path
from datetime import datetime

# Add framework to path
sys.path.insert(0, os.getcwd())

from wai_cli.lugs import LugManager

DEMO_DIR = Path("examples/demo_spoke")

def setup_demo_env():
    """Create a fresh spoke for the demo."""
    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
    DEMO_DIR.mkdir(parents=True)
    print(f"--- Environment Setup: {DEMO_DIR} ---")

def print_header(agent_name, role, action):
    print(f"\n\n{'='*60}")
    print(f"🤖 AGENT ACTIVE: {agent_name}")
    print(f"🎭 ROLE: {role}")
    print(f"⚡ ACTION: {action}")
    print(f"{'='*60}\n")

def run_architect_phase(lm: LugManager):
    print_header("ARCHITECT-01", "planning", "Defining System Architecture")
    
    # 1. Start Session
    session = lm.create_session(
        session_id="session_arch_01",
        who="Claude 3.7 Sonnet",
        ide="Claude Code",
        mode="PLANNING",
        agent_id="architect-01",
        agent_role="planning"
    )
    print(f"✅ Session Started: {session.session_id} (Role: {session.agent_role})")
    
    # 2. Define Epic
    epic = lm.create_lug(
        title="Multi-Database Support",
        lug_type="epic",
        priority="high",
        impact="large",
        value=8,
        session_id=session.session_id,
        justification="Client requires PostgreSQL support alongside SQLite"
    )
    print(f"📝 Created Epic: [{epic.id[:8]}] {epic.title}")
    
    # 3. Add System Sketch (simulated by adding notes/tasks)
    sketch_task = lm.create_lug(
        title="Define DB Abstraction Layer (System Sketch)",
        lug_type="task",
        priority="high",
        deps=[epic.id], # Child of epic roughly
        session_id=session.session_id,
        extras={"type": "system_sketch", "questions_answered": 5}
    )
    print(f"📐 Defined Sketch: [{sketch_task.id[:8]}] {sketch_task.title}")
    
    print("\n... Architect thinking ...\n")
    time.sleep(1) # Dramatic pause
    
    print("✅ Architect Phase Complete. Context saved to Hub.")

def run_builder_phase(lm: LugManager):
    print_header("BUILDER-X9", "coding", "Implementing Features")
    
    # 1. Start Session
    session = lm.create_session(
        session_id="session_build_99",
        who="Cline v2.0",
        ide="VS Code",
        mode="EXECUTION",
        agent_id="builder-x9",
        agent_role="coding"
    )
    print(f"✅ Session Started: {session.session_id} (Role: {session.agent_role})")
    
    # 2. Discover Ready Work (Simulation of 'wai ready')
    # In a real app, we'd use lm.get_ready_lugs()
    print("🔎 Scanning Hub for HIGH priority planning output...")
    open_lugs = lm.get_open_lugs()
    epics = [l for l in open_lugs if l.type == "epic"]
    
    if not epics:
        print("❌ No work found!")
        return
        
    target_epic = epics[0]
    print(f"🎯 Found Target: [{target_epic.id[:8]}] {target_epic.title}")
    print(f"   > Justification: {target_epic.justification}")
    
    # 3. Create Implementation Tasks
    print("\n... Builder decomposing work ...\n")
    
    task1 = lm.create_lug(
        title="Implement SQLAlchemy Adapter",
        lug_type="task",
        priority="high",
        deps=[target_epic.id], # Depends on epic
        session_id=session.session_id,
        agent_id="builder-x9" # Optional direct attribution
    )
    print(f"🔨 Created Task: [{task1.id[:8]}] {task1.title}")
    
    task2 = lm.create_lug(
        title="Migration Script Generator",
        lug_type="task",
        priority="medium",
        deps=[target_epic.id],
        session_id=session.session_id
    )
    print(f"🔨 Created Task: [{task2.id[:8]}] {task2.title}")

    print("✅ Builder Phase Complete. Worklog updated.")

def inspect_history(lm: LugManager):
    print("\n\n")
    print("🧐 MANAGER VIEW: Inspecting Agent History")
    print("-" * 40)
    
    # Reload sessions to be sure
    # (In this in-memory same-process demo, lm.sessions is up to date, 
    # but let's iterate what we have)
    
    sorted_sessions = sorted(lm.sessions.values(), key=lambda s: s.timestamp_start)
    
    for sess in sorted_sessions:
        print(f"SESSION: {sess.timestamp_start}")
        print(f"  > ID:    {sess.session_id}")
        print(f"  > AGENT: {sess.agent_id} ({sess.agent_role})")
        print(f"  > IDE:   {sess.ide}")
        print("")

def main():
    setup_demo_env()
    lm = LugManager(DEMO_DIR)
    
    run_architect_phase(lm)
    run_builder_phase(lm)
    inspect_history(lm)
    
    # Cleanup
    # shutil.rmtree(DEMO_DIR)
    print(f"\nDemo complete. Artifacts in {DEMO_DIR}")

if __name__ == "__main__":
    main()
