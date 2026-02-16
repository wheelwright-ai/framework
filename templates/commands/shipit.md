# WAI Shipit Protocol

This document outlines the standard procedure for an AI agent to perform a `shipit` operation. This is an internal directive focused on ensuring quality and documentation alignment before a `closeout`.

**Objective:** To verify the quality, performance, and documentation of the work completed in a session before committing it.

### Shipit Procedure

1.  **Quality Gating (P3, P4):**
    *   Execute the full test suite for the project (e.g., `pytest`). All tests must pass.
    *   Run any available linters and type checkers. The code must be free of errors.

2.  **Benchmark Execution (P5):**
    *   Run the end-to-end benchmarks.
    *   Append a summary of the benchmark findings to a designated log file (e.g., `benchmarks/results.md`).

3.  **Documentation Review & Update (P7, P8):**
    *   Review `README.md` to ensure it is up-to-date with any changes made during the session.
    *   Review `llms-full.txt` (or equivalent master prompt document) and update it to reflect new capabilities, commands, or protocols.

4.  **Execute Closeout:**
    *   After all quality and documentation gates have passed, initiate the `closeout` procedure to commit and finalize the session.

**Success Criteria:**
*   The test suite passes completely.
*   Benchmarks are run and their findings are recorded.
*   Key documentation (`README.md`, `llms-full.txt`) is reviewed and updated.
*   The `closeout` procedure is triggered only after all gates are passed.