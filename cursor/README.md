# bidi-skills in Cursor — and other agents

The `rtl-text` rules were written as an Agent Skill for Claude, but the
rules are plain text and the checker is plain Python — nothing here is
Claude-specific. This folder adapts them for Cursor first, then everyone
else.

## Cursor (project rule — recommended)

Copy the rule into your project:

```bash
mkdir -p .cursor/rules
cp cursor/rtl-text.mdc .cursor/rules/
```

Cursor picks the rule up automatically when you edit files matching its
globs (Markdown, text, HTML, JSON, JSX/TSX, Vue…) and its description
matches the task. It is `alwaysApply: false` on purpose — it should only
load when RTL text is actually involved.

Want it in every project? Add the body of `rtl-text.mdc` (without the
frontmatter) as a **User Rule** under Cursor Settings → Rules.

## The checker, from Cursor's terminal

The rule tells the agent *what* to do; the checker proves it did it:

```bash
git clone https://github.com/mohammad-abbasi-sh/bidi-skills
python3 bidi-skills/skills/rtl-text/scripts/bidi_check.py your-file.md
```

Zero dependencies. Exit code 1 on errors, `--json` for tooling, 0–100
score. Works in CI and pre-commit hooks exactly the same way.

## Other agents & editors

- **Claude Code / Claude.ai** — native Agent Skill: see the main README.
- **Windsurf, Cline, Continue, Cody, generic chatbots** — paste the body
  of `rtl-text.mdc` (or `skills/rtl-text/SKILL.md`) into the tool's rules
  file (`.windsurfrules`, `.clinerules`, system prompt…). The content is
  identical; only the envelope differs.
- **Any MCP client (Cursor included)** — an MCP server wrapping
  `bidi_check` is on the roadmap; until then the CLI above is the
  integration point.
