# Standing on Shoulders: The Inspirations Behind Wheelwright

*"We aren't reinventing the wheel — we're evolving it faster than one person ever could."*

Wheelwright AI (WAI) is built upon the brilliant ideas of the AI engineering community. We gratefully acknowledge these sources of inspiration and aim to serve as a foundational layer for them.

## Core Philosophies

### 1. Colony Architecture (Steve Yegge)
*   **Source:** [The Future of Coding Agents](https://steve-yegge.medium.com/the-future-of-coding-agents-e9451a84207c)
*   **The Insight:** "Nature prefers colonies." Instead of one "super-ant" (a massive context window agent), we need many specialized agents working in coordination.
*   **WAI Implementation:** The Hub-and-Spoke model serves as the "Village Brain" or shared memory for these agent colonies.

### 2. Git-Backed Task Graphs (Beads)
*   **Source:** [Beads Project](https://github.com/steveyegge/beads)
*   **The Insight:** Agent memory should be structured, persistent, and version-controlled. Hash-based IDs allow collision-free distributed work.
*   **WAI Implementation:** The `WAI-Lugs.jsonl` system directly adopts the schema and `wai ready` logic from Beads to provide agents with unblocked work.

### 3. Automated Backpressure (Banay.me)
*   **Source:** [Don't Waste Your Backpressure](https://banay.me/dont-waste-your-backpressure/)
*   **The Insight:** Agents need automated feedback loops (compilers, linters, tests) to self-correct without human intervention.
*   **WAI Implementation:** `WAI-Backpressure.yaml` and `wai check` allow agents to autonomously verify their work before asking for human review.

### 4. Intentional Systems (Focused Chaos)
*   **Source:** [Vibe Coding Without System Design Is A Trap](https://www.focusedchaos.co/p/vibe-coding-without-system-design-is-a-trap)
*   **The Insight:** "Accidental architecture" kills projects. We must force basic design questions before generating code.
*   **WAI Implementation:** The "System Sketch" section in `WAI-Guide.md` forces agents to answer 5 critical design questions before implementation.

### 5. Context-Driven Development (Google Conductor)
*   **Source:** Google Conductor / Gemini CLI
*   **The Insight:** Features need persistent specs (`SPEC.md`, `PLAN.md`) that survive the implementation chat.
*   **WAI Implementation:** The `WAI-Features/` directory structure ensures "Why we built this" is preserved alongside the code.

## Providing the Foundation

WAI does not compete with these tools; it supports them.
- We provide the **persistence layer** for Gas Town colonies.
- We provide the **cross-project memory** for Beads graphs.
- We provide the **configuration automation** for IDEs.

We are the wheelwrights ensuring the wheels keep rolling.
