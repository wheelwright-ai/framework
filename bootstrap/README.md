# WAI Bootstrap (GPT Single-File Mode)

Use this folder when you are in a GPT session without the WAI framework.
Goal: produce ONE minimal file that captures the benefits of WAI tracking.

## What WAI Is (Short)
Wheelwright AI (WAI) keeps project context continuous across sessions.
It stores identity, scope, decisions, and next actions so any AI can
pick up the work with full context.

## How to Use This Bootstrap
1) Open this README and WAI-Minimal.template.md in your GPT session.
2) Ask GPT to fill the template for your project in ONE file.
3) Save the result as WAI-Minimal.md.
4) After initializing Wheelwright locally, move it to:
   WAI-Spoke/seed/ingest/WAI-Minimal.md
5) Run WAI closeout (or Shipit). Closeout will ingest and
   distribute the content into WAI-State.json, WAI-State.md, and WAI-Guide.md.

## Notes
- Keep the output to a single file.
- Be concise: focus on identity, scope, decisions, and next actions.
- Avoid secrets you would not store in the repo.
