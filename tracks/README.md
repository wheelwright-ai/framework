# Tracks — Session Active-Collection Standard

**Tracks** is the standard for high-fidelity session telemetry in the Wheelwright ecosystem. This repository contains the specifications, prompts, and reference artifacts for recording "points" (turns) during AI-human conversations.

---

## 🚀 The Tracks Model

A Track is more than a chat log — it's a **cognitive artifact**. It captures not just what was said, but the reasoning, decisions, and abandoned concepts behind every turn.

- **Fidelity:** Every turn is recorded, regardless of size.
- **Narrative:** 3-8 sentences of "thinking" reconstruct the agent's mental model.
- **Precision:** Tool calls are logged by name, range, and output.
- **Negative Space:** "Fossils" capture what was rejected and why.

---

## 📂 Repository Structure

- `spec/track-format.md` — The pure JSONL specification.
- `prompts/` — System and user prompts for triggering collection.
- `samples/` — Reference track files for different scenarios.

---

## 🛠️ Usage

### For AI Developers
Integrate the `track-encapsulation.yaml` skill into your agent. Make point recording a **Mandatory Final Step** of every turn.

### For Users
Use the prompts in `prompts/` to manually trigger session closeouts or enable active-collection in external AI tools (ChatGPT, Claude, Gemini).

---

## 📜 License

MIT License — see `LICENSE` for details.
