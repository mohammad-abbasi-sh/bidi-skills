---
name: rtl-text
description: Produce correct right-to-left and mixed-direction text (Persian, Arabic, Urdu, Hebrew) — proper ZWNJ joining, Persian vs Arabic codepoints, digit and punctuation discipline, and keeping embedded Latin/code/formula tokens intact and correctly ordered. Use whenever writing, translating, editing, or generating content that contains Arabic-script or Hebrew text, or bilingual RTL/LTR content such as documents, UI strings, captions, tables, or social posts. Also run the bundled checker on finished text files before delivering them.
---

# RTL Text — write Arabic-script and mixed-direction content correctly

LLMs routinely corrupt RTL text in predictable ways. Follow these rules
whenever your output contains Persian, Arabic, Urdu, or Hebrew — and verify
with the checker at the end.

## Joining: ZWNJ is not optional (Persian)

- Join prefixes and suffixes with ZWNJ (U+200C, «‌»), never a space:
  «می‌شود» not «می شود» · «نمی‌خواهم» not «نمی خواهم» · «کتاب‌ها» not
  «کتاب ها» · «خانه‌ام» not «خانه ام».
- Never insert spaces or letter-spacing inside an Arabic-script word —
  the script is cursive; spacing breaks the letter joining.

## Characters: Persian ≠ Arabic codepoints

- In Persian text use Persian ی (U+06CC) and ک (U+06A9). Arabic ي (U+064A)
  and ك (U+0643) look similar but are different codepoints — mixing them
  breaks search, sorting, and fonts.
- Persian-specific letters: گ چ پ ژ. If they appear, the text is Persian —
  apply Persian rules even inside mostly-Arabic-looking passages.

## Mixed direction: keep LTR islands intact

- English terms, code, URLs, and formulas embedded in RTL text are single
  LTR units. Never split them, never reorder their internals:
  in «فرمول ihr = ریشه + t است», the formula is one LTR strip.
- Operators and numbers bind to the LTR island: write «نسخه 3.2» (logical
  order) and let the renderer place it; don't manually flip tokens.
- Sentence punctuation belongs to the surrounding RTL sentence: it goes
  at the end of the RTL text, not after a trailing Latin word.

## Numbers and dates

- Pick one digit system per document and locale: Persian ۱۲۳ for Persian
  text, Arabic ١٢٣ for Arabic text, ASCII 123 inside code, versions, and
  URLs. Never mix systems in one document.
- Keep numbers with their units in logical order; don't split a number
  from its unit across a direction boundary.

## Layout (when generating HTML, images, or tables)

- RTL text aligns right; the first table column is the rightmost one.
- Line height for Arabic script needs ~1.9–2× the font size — ascenders
  and dots clip at Latin line heights.
- Never apply letter-spacing (tracking) to Arabic script.

## Invisible characters

- Don't emit bidi override/embedding controls (U+202A–U+202E,
  U+2066–U+2069) unless deliberately isolating a token — they invisibly
  reorder rendered text and are a known content-hiding trick.

## Verify before delivering

Run the bundled checker on any text file you produced:

```bash
python3 scripts/bidi_check.py <file> [--json]
```

Fix every error it reports (ZWNJ spacing, split plurals, Arabic
codepoints in Persian text) before showing the result to the user.
Warnings (bidi controls, digit mixing) need a deliberate decision, not
silence.
