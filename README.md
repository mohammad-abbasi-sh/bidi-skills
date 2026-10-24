# bidi-skills

**AI agents write broken RTL text. These skills fix that.**

Skills + a deterministic checker that teach Claude Code, Cursor, Codex and other agents to produce correct right-to-left and mixed-direction content — Persian, Arabic, Urdu, Hebrew. Zero dependencies.

## The problem

Ask any LLM for Persian or Arabic content and you get the same corruptions, every time:

| ❌ What agents produce | ✅ Correct | Why it matters |
|---|---|---|
| می شود (space) | می‌شود (ZWNJ) | The prefix must join with U+200C; a space reads wrong and breaks search |
| کتاب ها | کتاب‌ها | Plural suffix split off as its own word |
| كتاب / کتاب with Arabic ك ي | کتاب with Persian ک ی | Different codepoints — search, sorting and fonts break silently |
| `ihr = ریشه + t` reordered by bidi | formula kept as one LTR strip | Mixed-direction rendering scrambles operators and tokens |
| 123 next to ۴۵۶ | one digit system per document | Mixed digits look broken and parse inconsistently |

Maintainers of RTL content fix these by hand, forever. There was no skill pack for this — in an ecosystem with hundreds of English-centric agent skills, RTL (≈600M speakers) had none. Now it does.

## What's inside (v0.1)

- **`skills/rtl-text`** — an Agent Skill with the production rules: ZWNJ joining, Persian vs Arabic codepoints, LTR-island handling for code/formulas/URLs, digit & punctuation discipline, RTL layout rules (alignment, line height, no letter-spacing).
- **`skills/rtl-text/scripts/bidi_check.py`** — a zero-dependency checker that scans text files and flags the corruptions deterministically, with a 0–100 bidi score:

```bash
$ python3 bidi_check.py article.md
[ERROR  ] article.md:3 ZWNJ_SPACE: «می …» uses a space; Persian prefixes join with ZWNJ
[ERROR  ] article.md:5 PLURAL_SPACE: Plural suffix split by a space; join with ZWNJ: «کتاب‌ها»
[WARNING] article.md DIGIT_MIXING: Mixed digit systems in one document

Bidi score: 76/100 · 3 finding(s)
```

## Install in Claude Code

```bash
git clone https://github.com/mohammad-abbasi-sh/bidi-skills
cp -r bidi-skills/skills/rtl-text ~/.claude/skills/
```

Then write Persian/Arabic content as usual — the skill loads when RTL text is involved and the agent self-checks its output with `bidi_check.py` before delivering.

For Claude.ai: download the release zip of the skill and upload it in Settings → Capabilities → Skills.

## Install in Cursor (and other agents)

Nothing here is Claude-specific — the rules are plain text and the checker is plain Python.

- **Cursor:** copy `cursor/rtl-text.mdc` into your project's `.cursor/rules/` — see [cursor/README.md](cursor/README.md) for details, including the checker in Cursor's terminal.
- **Windsurf / Cline / Continue / generic agents:** paste the body of the rule (or of `skills/rtl-text/SKILL.md`) into the tool's rules file or system prompt.

## Roadmap

- `ar-text` / `ur-text` / `he-text` — language-specific rule depth (Arabic ة/همزة discipline, Urdu Nastaliq notes, Hebrew niqqud & acronyms)
- `rtl-ui-audit` — scan HTML/CSS for `dir`, alignment, and logical-property mistakes
- MCP server exposing `bidi_check` as a tool to any MCP client
- More checker rules, driven by real-world failure reports (issues welcome)

## Principles

- **Deterministic where it counts.** The rules are text, but the verification is code — the agent must run the checker, not vibes.
- **Born in production.** These rules come from shipping real Persian content daily, not from a spec sheet.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — SEO × AI, working in Persian and English every day.

## License

MIT
