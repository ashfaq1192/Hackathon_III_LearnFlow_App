# Skills Development

LearnFlow is built using **reusable skills** that enable AI agents (Claude Code and Goose) to deploy and manage the application autonomously.

## What are Skills?

Skills are instruction files that tell AI agents how to perform specific tasks. They follow the **MCP Code Execution pattern**:

1. **SKILL.md** - Instructions for the AI (~100 tokens)
2. **scripts/** - Executable code that does the work (0 tokens loaded)
3. **REFERENCE.md** - Deep documentation (loaded on-demand)

## Skill Structure

```
.claude/skills/<skill-name>/
├── SKILL.md              # ~100 tokens max (instructions only)
├── REFERENCE.md          # Deep docs (loaded on-demand only)
└── scripts/
    ├── *.py              # Python scripts that execute operations
    ├── *.sh              # Bash scripts for deployment
    └── templates/        # Optional: config/code templates
```

## LearnFlow Skills

| Skill | Purpose |
|-------|---------|
| `k8s-foundation` | Kubernetes cluster operations |
| `kafka-k8s-setup` | Deploy Apache Kafka |
| `neon-postgres-setup` | Setup Neon PostgreSQL |
| `dapr-setup` | Install Dapr service mesh |
| `fastapi-dapr-agent` | Generate FastAPI microservices |
| `nextjs-k8s-deploy` | Deploy Next.js frontend |
| `better-auth-setup` | Configure authentication |
| `kong-gateway-setup` | Deploy API gateway |
| `docusaurus-deploy` | Generate documentation |

## Using Skills

### With Claude Code
```bash
claude "Use kafka-k8s-setup to deploy Kafka in the learnflow namespace"
```

### With Goose
```bash
goose "Use kafka-k8s-setup to deploy Kafka in the learnflow namespace"
```

## Creating New Skills

### 1. Create SKILL.md

```markdown
---
name: my-new-skill
description: Brief description of what this skill does
version: 1.0.0
---

# My New Skill

## When to Use
- Use case 1
- Use case 2

## Instructions
1. Run: `python scripts/setup.py --arg value`
2. Verify: Check output

## Validation
- [ ] Check 1 passes
- [ ] Check 2 passes
```

### 2. Create Scripts

```python
#!/usr/bin/env python3
"""Setup script for my-new-skill."""
import subprocess, sys, argparse

def main(arg):
    # Do the work
    print(f"✓ Completed: {arg}")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arg", required=True)
    args = parser.parse_args()
    sys.exit(main(args.arg))
```

### 3. Test with Both Agents

Test with Claude Code:
```bash
claude "Use my-new-skill to do something"
```

Test with Goose:
```bash
goose "Use my-new-skill to do something"
```

## MCP Code Execution Pattern

The key principle is **token efficiency**:

### Bad (Direct MCP Integration)
```
Agent loads MCP tools → 15,000 tokens consumed
Agent queries data → Full dataset in context
Result: 41% context consumed before work begins
```

### Good (Skills + Scripts)
```
Agent reads SKILL.md → ~100 tokens
Script executes and filters → 0 tokens (executed, not loaded)
Script returns summary → "✓ 5 items found"
Result: 3% context consumed, full capability retained
```

## Best Practices

1. **Keep SKILL.md minimal** - Instructions only, ~100 tokens
2. **Heavy logic in scripts** - They execute, not load into context
3. **Return minimal output** - Status + essential data only
4. **Cross-agent compatibility** - Test with both Claude and Goose
5. **Include validation** - Checkboxes for verification steps
