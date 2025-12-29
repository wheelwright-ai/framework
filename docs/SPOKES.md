# Wheelwright Spokes

Spokes extend your wheel's capabilities with specialized functions.

## What are Spokes?

Spokes are modular extensions that add specific capabilities to your Wheelwright wheel. They:

- Add specialized context for AI interactions
- Provide domain-specific patterns and guidance
- Can be added or removed as needed
- Share learnings back to your hub

## Built-in Spokes

### Meta-Consultation

**Purpose:** Get diverse perspectives by consulting multiple AI models.

**Use cases:**
- Complex architectural decisions
- Validating important choices
- Getting alternative approaches

**How it works:**
1. Frame your question
2. Query multiple AI models (Claude, GPT, Gemini)
3. Synthesize responses
4. Document the consensus

```bash
wwai spoke add meta-consultation
```

### Document Analysis

**Purpose:** Deep analysis of documents, reports, and files.

**Use cases:**
- Analyzing requirements documents
- Reviewing specifications
- Extracting key information

**Capabilities:**
- PDF and document parsing
- Key point extraction
- Summary generation
- Cross-reference checking

```bash
wwai spoke add document-analysis
```

### Code Review

**Purpose:** Comprehensive code review and suggestions.

**Use cases:**
- Pull request reviews
- Security analysis
- Performance optimization
- Code quality checks

**Focus areas:**
- Security vulnerabilities
- Performance issues
- Code clarity
- Best practices

```bash
wwai spoke add code-review
```

## Managing Spokes

### List Available Spokes

```bash
wwai spoke list
```

### Add a Spoke

```bash
wwai spoke add <spoke-name>
```

### View Active Spokes

Check `spokes.active` in your `WWAI-State.json`:

```json
{
  "spokes": {
    "active": ["meta-consultation", "code-review"],
    "available": ["meta-consultation", "document-analysis", "code-review"]
  }
}
```

## Creating Custom Spokes

Coming soon: Documentation for creating your own spokes.

## Spoke Marketplace

Future feature: Share and discover community-created spokes.

---

*Wheelwright Framework - wheelwright.ai*
