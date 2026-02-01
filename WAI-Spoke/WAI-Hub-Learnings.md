# Hub Learnings - 2026-01-31

These patterns were distributed from the hub knowledge base.
Run closeout to integrate these into your WAI-Guide.md

## Architectural_Decision

### SCF to Wheelwright rebrand
Complete framework rebrand from Session Continuity Framework to Wheelwright. New wheel metaphor (hub=memory, spokes=capabilities, wheel=project). WWAI file naming convention. GitHub org wheelwright-ai. Domain wheelwright.ai.

*Impact: 10 | Source: framework-signals*

## Integration_Pattern

### Enforceable CLAUDE.md protocol with priority levels and state tracking
CRITICAL PATTERN for all AI tool integrations: CLAUDE.md must use PRIORITY LEVELS (0=blocking, 1=always-active, 2=optional), inline session start protocol (not delegate to other files), add session state tracking (protocol_completed flag in WWAI-State.json), include enforcement checklist with explicit MUST NOT rules, and provide exception for circular dependency when fixing CLAUDE.md itself. Without this structure, AI tools receive instructions as passive reminders rather than executable directives, causing protocol to never run. This pattern ensures automatic briefing and context loading on every session start.

*Impact: 10 | Source: framework-signals*

## Session_Continuity_Pattern

### JSONL conversation logging with closeout processing
Track every turn in .WAI/session-conversation.jsonl using append-only JSONL format. On closeout: load log line-by-line, extract insights (summary, key topics, files modified), move current_session → last_closeout in WAI-State.json, clear verbose log. CRITICAL: Hub learning cannot proceed until closeout complete and conversation log consumed/cleared. This enables session recovery from disruptions and intelligent session summaries. Use shipit command for closeout + git commit in one operation.

*Impact: 10 | Source: framework-signals*

## Naming_Convention

### Capitalized .WAI/ for pronounced readability
When folder or file names contain 'wai', capitalize to .WAI/ for pronounced readability (W-A-I as distinct letters). Makes WAI visually distinct from common word 'wai'. Applied to directory (.WAI/), CLI tool (WAI), and all documentation. WAI stands for 'Wheelwright AI' (one word, NOT 'Wheel Wright'). Tagline: 'This is the WAI' (Mandalorian reference).

*Impact: 8 | Source: framework-signals*

### Unknown

*Impact: 9 | Source: session-continuity-framework-signals*

## Testing_Pattern

### Comprehensive unit test suite for bash hooks
Created test-session-start.sh with 26 tests covering: exit conditions, briefing generation, decision filtering, next actions, git integration, state updates, error handling. Uses isolated /tmp environment with fixtures. Setup/teardown pattern ensures clean state. Tests both happy paths and edge cases (missing files, minimal state). Run via ./WAI/hooks/test-session-start.sh. All tests must pass before deployment.

*Impact: 8 | Source: framework-signals*

## Quality_Policy

### Dual-layer testing: smoke tests + unit tests
CRITICAL POLICY for all projects: Maintain TWO test layers. (1) Smoke tests - Fast verification of integration points, run before commits, catches breaking changes quickly (framework: 40 tests, spoke: 37 tests). (2) Unit tests - Detailed component coverage with isolated fixtures, ensures reliability (26 tests for session-start hook). Both test suites expand as features are added. Smoke tests verify end-to-end flows, unit tests verify individual components. Run both before shipit. This dual approach caught 3 issues during implementation that would have been production bugs. Template both test suites in hub for reuse across all Wheelwright projects.

*Impact: 10 | Source: framework-signals*

## Optimization_Pattern

### Token Efficiency Protocols - ADAPTIVE workflow prevents 50-80% waste
CRITICAL OPTIMIZATION for all AI projects: Implemented ADAPTIVE workflow mode that automatically assesses task complexity and enforces multi-stage gates (Discussion → READY TO PLAN → PLAN ACCEPTED → Implementation) for complex tasks (multi-file OR >6 steps), while allowing YOLO autonomy for simple tasks. Includes: (1) Standardized plan template with Goal/Assumptions/Steps/Risks/Rollback, (2) Automatic checkpointing every 3-5 steps for large plans (>8 steps OR >5 files), (3) Context hygiene rules (never repeat >500 tokens, use file:line references, capacity warnings at 60%/80%/90%), (4) Compact command for context compression (auto-runs before closeout/shipit), (5) Fallback protocol for blocked implementations, (6) Task scoping guardrails for multi-feature requests, (7) Cross-platform templates (Cursor .cursorrules, VS Code settings.json, Generic AI-INSTRUCTIONS.md). Schema extensions in WAI-State.json: complexity_thresholds (multi_file: 2, step_count: 6, checkpoint_interval: 3), capacity_management (warning: 0.80, critical: 0.90). Smoke tests expanded to 101 total (52 framework, 49 spoke). This prevents premature implementation waste, the #1 token efficiency problem in long-running projects. Template for all Wheelwright hubs and spokes.

*Impact: 10 | Source: framework-signals*

## Pattern

### SPIN methodology for SaaS landing pages
Used SPIN (Situation-Problem-Implication-Need-Payoff) selling framework to restructure entire website. Single-page design with cycling examples, interactive vertical selector, and contact form CTA. Effective for validation-phase products where goal is conversations over conversions.

*Impact: 9 | Source: owners-share-signals*

## Strategic_Recommendation

### Test Infrastructure Strategy vs Individual Test Fixes
When facing 17+ test failures across multiple components (FileSummarizer, PageLayout, Associations, Form), systematic infrastructure improvements (unified test utilities, proper context providers, standardized mocks) prove more effective than chasing individual test failures. Created comprehensive testUtils.jsx with all necessary providers and Material-UI mocks. Pattern: Focus on systematic code review and infrastructure when error count indicates architectural issues rather than individual bugs.

*Impact: 8 | Source: condoshield-crm-signals*

## Development_Best_Practice

### Mandatory Python Virtual Environment + YOLO Mode Pattern
Always create and activate Python virtual environment at start of every project/script execution without exception. Use python3 -m venv <env_path>, activate with source <env_path>/bin/activate (Linux/macOS) or <env_path>\Scripts\activate (Windows). Install ALL dependencies exclusively inside venv to isolate packages and avoid system conflicts. Use pip freeze > requirements.txt for reproducibility. Enable YOLO mode: prioritize efficient, streamlined execution paths for object detection workflows (YOLOv5/YOLOv8), assume non-interactive runs with pre-installed dependencies, automate command arguments and environment configurations.

*Impact: 9 | Source: condoshield-crm-signals*

## Systematic_Cleanup_Methodology

### Systematic Test Infrastructure + Codebase Cleanup Success Pattern
Achieved 94% test failure reduction (18→1) through systematic approach: 1) Created unified test infrastructure (testUtils.jsx) with all providers (MSAL, Material-UI, contexts), 2) Fixed root causes (missing MsalProvider exports, improper breakpoint mocks), 3) Standardized error handling (null checks, optional chaining), 4) Applied systematic fixes across components rather than individual test chasing, 5) Cleaned unused imports via linting. Result: PageLayout 100% passing, Associations 75% improved, FileSummarizer exceptions eliminated. Pattern validates: systematic infrastructure > individual fixes.

*Impact: 9 | Source: condoshield-crm-signals*

## Production_Anti_Pattern

### React Router Fallback Anti-Pattern in Production SPA
CRITICAL: Never use window.location.href as fallback in React Router navigation handlers. Even minor React Router errors trigger fallbacks, causing full page reloads instead of client-side routing in production. Pattern: try { navigate() } catch { window.location.href } breaks SPA behavior. Solution: Remove fallback entirely, use pure React Router with comprehensive event prevention (preventDefault, stopPropagation, stopImmediatePropagation). Also: AG Grid v33+ deprecated suppressMenu→suppressHeaderMenuButton, suppressCellFocus removed entirely. Always test production builds locally to catch environment-specific navigation issues.

*Impact: 8 | Source: condoshield-crm-signals*

## Scf_Architectural_Pattern

### Hash-Pairing System for buildstate.json/.md Cross-Reference
Implemented hash-pairing system to link detailed JSON data in buildstate.json with human explanations in buildstate.md. Each pattern/rule/learning has a unique hash (format: {type}-{shortId}-{timestamp}) stored in BOTH files. Benefits: 1) Traceability - easy to find related entries across files, 2) SCF Hub Learning - Hub can correlate machine-readable data with human context for better learning, 3) Cross-Session Knowledge - Future AIs can reference patterns by stable hash, 4) Audit Trail - track pattern evolution over time, 5) No ambiguity - never wonder 'why is this here' when reading either file. Applied to jsErrorPatterns for JavaScript runtime error learning. Rule: ALL buildstate entries that appear in both .json and .md must have paired hash keys. Example: err-orphaned-code-1734299439 links ReferenceError pattern details in JSON with human explanation in MD.

*Impact: 10 | Source: condoshield-crm-signals*

## Security_Hardening_Methodology

### Phased Security Audit with Utility-First Approach
Successfully completed Phase 1 security hardening using systematic approach: 1) Installed DOMPurify and sanitized ALL 9 XSS vulnerabilities (dangerouslySetInnerHTML), 2) Created reusable safeJson.js utility with validators before migrating unsafe JSON.parse calls, 3) Created logger.js utility for production-safe logging, 4) Applied React.memo to high-traffic components (FilterBar), 5) Documented Phase 2 backlog with effort estimates and ROI. Key insight: Build utilities FIRST, then migrate incrementally. Created 3 comprehensive docs for audit trail and knowledge preservation. Pattern validates: systematic infrastructure + incremental migration > reactive bug fixes.

*Impact: 9 | Source: condoshield-crm-signals*

## Api_Proxy_Pattern

### Azure Functions 500 Empty Body = Authentication Required
When Azure Functions returns HTTP 500 with empty body '{}', the root cause is almost always missing authentication - NOT a proxy issue or data format problem. Key learnings: 1) Frontend azureClient.js skips token acquisition in local dev mode (line 27-29), so requests go to Azure without Authorization header, 2) Server-side Node.js code does NOT need CORS proxies (CORS is browser-only restriction), yet leadAutomationController was using dead Heroku proxy, 3) The fix pattern: Create dedicated server-side endpoint (e.g., /api/associations/create) that gets auth token via /getAuth first, then calls Azure with proper Authorization header, 4) Stream-based proxy forwarding (config.data = req) can fail without Content-Length - buffer JSON bodies first. Resolution: Route frontend through server-side endpoint that handles authentication properly rather than trying to proxy unauthenticated requests directly to Azure.

*Impact: 9 | Source: condoshield-crm-signals*

## Deployment_Pattern

### PHP Reverse Proxy for Node.js-Unavailable Shared Hosting
CRITICAL DEPLOYMENT PATTERN: When deploying React SPA to shared hosting without Node.js support (cPanel without Node.js options, no SSH access), use PHP as a reverse proxy to forward API requests to Azure Functions. Diagnostic journey: 1) API requests returning HTML (index.html) = .htaccess SPA routing redirecting /api/* to index.html - FIX: Add RewriteCond to exclude /api/ from SPA fallback, 2) 404 errors on /api/* = Node.js server not running (not available) - FIX: PHP proxy instead of Node.js, 3) 500 errors from PHP in subdirectory (/api/azure/proxy.php) = PHP execution blocked in subdirectories or .htaccess interference - FIX: Move proxy to document root (azure-proxy.php), 4) Garbled response data (gzip header \u001f\u008b) = Azure Functions returns gzip-compressed responses - FIX: Add CURLOPT_ENCODING => '' to auto-decompress. Solution: Root-level PHP proxy with cURL, .htaccess routing /api/azure/* to /azure-proxy.php?path=$1, gzip auto-decompression. Result: Full CRM functionality without Node.js backend.

*Impact: 10 | Source: condoshield-crm-signals*

## Calculation_Anti_Pattern

### Currency String Concatenation Bug in JavaScript Reduce Operations
CRITICAL ANTI-PATTERN: When summing currency/revenue values with reduce(), string concatenation instead of addition produces astronomically wrong totals (e.g., '$458913875750254613520150060085008008000' instead of '$45,891'). Root cause: Database stores numbers as strings, and (stringValue || 0) still returns the string if truthy. Fix pattern: ALWAYS wrap in Number() - `reduce((sum, a) => sum + (Number(a.monthlyRevenue) || 0), 0)`. Better: Create formatCurrency() helper that parses input as Number and uses Intl.NumberFormat for consistent display. Applied fix: 1) Created formatCurrency(value, decimals=0) helper with Number() parsing, 2) Updated all reduce operations to use Number() conversion, 3) Replaced all $${value.toLocaleString()} with formatCurrency(value). This pattern applies to ANY numeric aggregation where data source may contain strings.

*Impact: 9 | Source: condoshield-crm-signals*

## Visualization_Pattern

### Sales Funnel Cumulative Math for Accurate Pipeline Metrics
Sales funnel visualizations require CUMULATIVE counts, not stage-by-stage counts. Wrong approach: Compare count at Stage N vs count at Stage N-1 (gives meaningless percentages when stages aren't strictly sequential). Correct approach: 1) Calculate cumulative = deals at or past each stage (sum of current stage + all later stages), 2) Stage Conversion = cumulative[N] / cumulative[N-1] (what % progressed), 3) Drop-off = cumulative[N-1] - cumulative[N] (how many filtered out), 4) % Remaining = cumulative[N] / cumulative[0] (overall funnel position). Implementation: const cumulativeCounts = stages.map((_, i) => stages.slice(i).reduce((sum, s) => sum + s.count, 0)). Show 'At Stage' (current count) AND 'Cumulative' (funnel position) for clarity. Separate Closed Lost/Dead as 'Filtered Out' section below main funnel.

*Impact: 8 | Source: condoshield-crm-signals*

## Bundle_Optimization_Pattern

### Dynamic Import for Large Optional Libraries
BUNDLE OPTIMIZATION: When a page uses a large library (Tesseract.js = 2.3MB, PDF.js = 1.5MB, etc.) that's only needed for specific user actions, use dynamic import() instead of static import. Pattern: 1) Remove static import at top of file, 2) Create loader function: const loadLibrary = async () => { const { thing } = await import('library'); return thing; }, 3) Call loader only when feature is triggered. Result: Library loads on-demand, not with initial page load. Even if the page itself is lazy-loaded via React.lazy(), static imports within it still bundle together. Dynamic import() within the component defers loading until actual use. Applied to Tesseract.js OCR - saved 2.3MB from initial FileSummarizer load, OCR still works perfectly when user uploads images. Key insight: React.lazy() for route splitting + dynamic import() for feature-level splitting = optimal bundle.

*Impact: 9 | Source: condoshield-crm-signals*

## Production_Monitoring_Pattern

### PHP Health Check Endpoint for Shared Hosting
PRODUCTION MONITORING: For shared hosting without Node.js, create a PHP health check endpoint that tests all dependencies. Pattern: 1) health-check.php returns JSON with checks array, 2) Each check has status (ok/warning/error), 3) Test PHP, cURL, Azure connectivity with latency, 4) Return HTTP 503 if critical failure, 200 otherwise, 5) Add .htaccess route: RewriteRule ^api/health$ /health-check.php [L], 6) Create React SystemStatus component that fetches /api/health and shows colored chips. Benefits: External monitors can ping /api/health, admins see real-time status, quick diagnosis when issues occur. Key checks: PHP version, cURL extension, Azure Functions connectivity (with latency_ms), proxy file existence, temp directory writable.

*Impact: 8 | Source: condoshield-crm-signals*

## Refactoring_Pattern

### Component Extraction Completion Pattern - Import Don't Duplicate
REFACTORING ANTI-PATTERN: When components/utils are extracted to separate files but the main file still contains inline duplicates, you get zero benefit - just maintenance burden. Pattern discovered: ActionItems.jsx was 5,213 lines despite having ./components/ and ./utils/ folders with extracted code. The main file never imported from these - it had DUPLICATE definitions. Fix: 1) Add imports from extracted modules, 2) Use sed to surgically remove inline definitions while keeping helpers unique to main file (formatProbability, isValidAssociation), 3) Import shared constants (statusPriority) from ./constants.js. Result: 5,213 → 1,772 lines (66% reduction). Key insight: After extracting code, verify the main file ACTUALLY IMPORTS it. Search for 'from ./components' or 'from ./utils' - if missing, extraction was incomplete.

*Impact: 9 | Source: condoshield-crm-signals*

## Self_Hosted_Feedback_System

### Leo AI-Assisted Feedback Collection with Self-Hosted Storage
USER FEEDBACK PATTERN: Integrated feedback system into existing AI assistant widget (Leo) for seamless user experience. When users click Leo, they choose: Report Problem, Make Suggestion, or Chat with Leo. For problems/suggestions, Leo conducts a 2-3 turn conversation asking clarifying follow-up questions, then generates a summary for user confirmation. Auto-captured context (invisible to user): current page, URL, browser info, console errors (last 5 min via getRecentErrors()). Self-hosted JSON storage (server/feedback-submissions.json) with full CRUD API. Admin sees badge count of unprocessed submissions. SCF integration: AI sessions check for pending feedback on startup via directive in buildstate.md. Pattern benefits: Users feel heard, admin gets rich context for debugging, no external dependencies.

*Impact: 9 | Source: condoshield-crm-signals*

## Browser_Debugging_Integration

### Chrome DevTools MCP for Live Browser Debugging
CRITICAL CAPABILITY: Integrate Chrome DevTools Model Context Protocol (MCP) server to give AI assistants direct access to live browser debugging. Pattern: 1) Install chrome-devtools-mcp package via npx, 2) Configure .mcp.json with stdio transport (powershell.exe for WSL compatibility), 3) AI can now browser_navigate, browser_screenshot, browser_console, performance_profile without manual intervention, 4) Works with localhost dev servers AND production sites, 5) No manual browser launch needed - Puppeteer handles it. WSL-specific: Use 'cmd /c' or 'powershell.exe' wrapper for npx commands to avoid UNC path issues. Benefits: AI discovers console errors automatically, captures screenshots for debugging, analyzes network requests, profiles performance - all without user copy-pasting. Available tools: browser_navigate, browser_screenshot, browser_console, browser_click, browser_input, browser_evaluate, performance_profile. Package: chrome-devtools-mcp@latest (NOT @modelcontextprotocol/server-chrome-devtools which doesn't exist). Integration check: claude mcp get chrome-devtools should show Status: ✓ Connected.

*Impact: 10 | Source: condoshield-crm-signals*

## Session_Awareness_Pattern

### IDE-Agnostic Session Start Hooks for AI Context
SESSION AWARENESS: Create universal session-start hook that works across all AI-enabled IDEs (Claude Code, Cursor, VS Code Copilot, Windsurf). Pattern: 1) Create executable bash script in WAI-Spoke/hooks/session-start.sh, 2) Display: WAI Framework status, MCP connection status, pending user feedback count, environment info (WSL/Windows detection), project version, 3) Integration methods: Claude Code (symlink to ~/.claude/hooks/), Cursor (.cursorrules directive), VS Code (tasks.json with runOn: folderOpen), Generic (manual call), 4) Make script IDE-agnostic - no hardcoded paths to specific IDEs. Benefits: AI assistants get instant project context on session start, see pending work (feedback submissions), know available tools (MCP status), understand environment constraints (WSL hybrid mode). Output includes colored terminal output with ✓/⚠/✗ status indicators. Prevents wasted time on 'What's the project state?' questions.

*Impact: 9 | Source: condoshield-crm-signals*

## Debugging_Workflow

### Production Debugging via MCP → Dev Fix → Staging Test Loop
PRODUCTION DEBUGGING WORKFLOW: Use Chrome DevTools MCP to debug live production sites, then fix in dev, test in staging - all within same AI session. Pattern: 1) User reports production issue at https://crm.condoshield.org, 2) AI uses browser_navigate(prod_url) + browser_console() to capture errors, 3) AI uses browser_screenshot() to document issue, 4) AI switches context to dev files, implements fix, 5) AI uses browser_navigate('http://localhost:5173') to test fix locally, 6) (Future) AI deploys to staging, uses browser_navigate(staging_url) to verify, 7) AI provides before/after screenshots + console comparisons. Benefits: No need to manually reproduce issues, AI sees exact production state, fixes validated before deployment, full audit trail with screenshots. Works because MCP server can navigate to ANY URL (localhost, staging, production), not limited to dev server. Multi-tab capability: MCP can inspect multiple tabs (prod vs dev vs staging) in same browser session for direct comparison.

*Impact: 9 | Source: condoshield-crm-signals*

## Pattern_Adaptation

### Browser DevTools MCP Pattern Adapted to CLI/Terminal Monitoring
PATTERN ADAPTATION: The Chrome DevTools MCP pattern (AI auto-discovers errors via browser console) should be adapted for CLI/terminal-based projects. For web apps: AI uses browser_console() to see errors without user copy-paste. For CLI tools (like Wheelwright Framework): AI needs equivalent terminal session monitoring. Proposed pattern: 1) MCP-style server that captures terminal output (stdout/stderr) in real-time, 2) AI can query recent terminal output without user copy-pasting errors, 3) Works for CLI tools, build scripts, deployment pipelines, test runners, 4) Saves time by eliminating 'Here's the error I got: [paste]' → 'Just run it and tell me if you see errors, I'll check the output myself'. Implementation ideas: Terminal multiplexer integration (tmux/screen session sharing), Log file tailing with MCP server, Shell history + output capture, Process output streaming. Key insight: Same benefit as browser MCP (AI auto-discovery) but adapted to different interface (terminal vs browser). User feedback: 'This log awareness is a killer feature and it should be adapted to the application... for instance in my framework project it doesnt have a web interface it has a command line CLI and if you can monitor those terminal sessions it would save me time copying and pasting errors back to you.'

*Impact: 9 | Source: condoshield-crm-signals*

## Ui_Ux_Pattern

### Comprehensive Dark Mode Implementation for React + MUI + AG Grid
COMPREHENSIVE PATTERN: Implemented app-wide dark mode with localStorage persistence, theme context, and component-level adaptations. Key learnings: 1) Create ThemeContext with mode state + localStorage sync, 2) Use theme.palette.mode checks in sx props, not hardcoded colors, 3) AG Grid requires className switch: ag-theme-alpine-dark vs ag-theme-alpine, 4) Use dark grays (not pure black): #1a1a1a for background, #2a2a2a for paper, rgba(255,255,255,0.05) for subtle contrast, 5) Styled components need theme parameter: styled(Card)(({ theme }) => ({...})), 6) MUI components auto-adapt via palette but custom Box/sx need explicit checks, 7) Toggle button in header with sun/moon icons for UX, 8) Error boundaries keep inline styles for reliability. Result: Zero bright whites in dark mode, comfortable contrast, persistent user preference. Files updated: ThemeContext (new), App, PageLayout, FilterBar (4 files), Associations, OpenAssociation (6 files). Pattern validates: theme.palette.mode checks > hardcoded colors, dark gray palette > pure black/white.

*Impact: 9 | Source: condoshield-crm-signals*

## Architectural_Pattern

### Unknown

*Impact: 10 | Source: session-continuity-framework-signals*

## Configuration_Pattern

### Unknown

*Impact: 8 | Source: session-continuity-framework-signals*

## Versioning_Pattern

### Unknown

*Impact: 8 | Source: session-continuity-framework-signals*

## Security_Enhancement

### XSS Prevention & Input Validation
Implemented Content Security Policy, input validation schemas, and file path sanitization to prevent XSS and injection attacks

*Impact: 9 | Source: session-continuity-framework-signals*

## Ux_Breakthrough

### Unified CLI Interface
Replaced 25+ Python scripts with single intuitive CLI. Role-based onboarding (Hub/Spoke), progressive disclosure UI, automatic user sophistication tracking

*Impact: 8 | Source: session-continuity-framework-signals*

