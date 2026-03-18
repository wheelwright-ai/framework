# Closing Request Prompt

Paste this into any AI conversation (ChatGPT, Claude, Gemini) when you are ready to end the session and want a structured Track file for Wheelwright.

---

## The Prompt

"We are finishing this session. Please perform a session closeout by generating a structured Track file following the Wheelwright format.

1. **Review our entire conversation history.**
2. **Reconstruct every turn as a 'point' in JSONL format.**
3. **For each point, include:** `turn`, `ts`, `phase`, `focus`, `action`, `thinking` (3-8 sentences), and `activity`.
4. **Capture any `decisions`, `insights`, `fossils`, or `open` threads** from the turns.
5. **Output the result as a single code block** containing the pure JSONL lines.

Do not summarize. Record every turn so I can resume this work perfectly in another session."
