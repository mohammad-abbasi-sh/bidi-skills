#!/usr/bin/env python3
"""bidi_check — deterministic checker for common RTL / Arabic-script text bugs
that AI agents (and humans) produce in Persian, Arabic, Urdu and Hebrew content.

Zero-dependency (Python standard library only).

Checks:
  ZWNJ_SPACE            (error)   "می شود" written with a space instead of ZWNJ
  PLURAL_SPACE          (error)   "کتاب ها" — plural suffix split off with a space
  ARABIC_CODEPOINT      (error)   Arabic ي / ك / ة inside Persian text
  BIDI_CONTROL          (warning) bidi override/embedding control characters present
  DIGIT_MIXING          (warning) ASCII digits mixed with Persian/Arabic digits
  LATIN_RUN_IN_RTL      (info)    long Latin run inside an RTL line — verify order

Usage:
  python3 bidi_check.py FILE [FILE ...] [--json]
Exit code: 1 if any error-severity finding, else 0.
"""

import json
import re
import sys

ZWNJ = "\u200c"
AR = "[\u0600-\u06FF]"  # Arabic script block

# --- patterns -------------------------------------------------------------
MI_SPACE = re.compile(r"(می|نمی)[ ]+(?=" + AR + ")")
PLURAL_SPACE = re.compile(r"(?<=" + AR + r")[ ]+(ها|های|هایی)(?=[\s\.,،؛:!؟]|$)")
ARABIC_CP = {"\u064a": "ی", "\u0643": "ک", "\u0629": "ه"}  # ي ك ة -> ی ک ه
PERSIAN_MARKERS = set("گچپژ")
BIDI_OVERRIDES = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
                  "\u2066", "\u2067", "\u2068", "\u2069"}
DIGITS_ASCII = re.compile(r"[0-9]")
DIGITS_FA = re.compile(r"[\u06f0-\u06f9]")
DIGITS_AR = re.compile(r"[\u0660-\u0669]")
LATIN_WORDS = re.compile(r"[A-Za-z]{2,}")
ARABIC_CHARS = re.compile(AR)

SEVERITY_PENALTY = {"error": 10, "warning": 4, "info": 1}


def check_text(text: str, filename: str = "<text>") -> list[dict]:
    findings: list[dict] = []
    is_persian = any(c in text for c in PERSIAN_MARKERS) or ZWNJ in text

    for lineno, line in enumerate(text.splitlines(), 1):
        for m in MI_SPACE.finditer(line):
            findings.append({
                "file": filename, "line": lineno, "code": "ZWNJ_SPACE",
                "severity": "error",
                "message": f"«{m.group(1)} …» uses a space; Persian prefixes join with ZWNJ: «{m.group(1)}‌» + verb",
                "snippet": line.strip()[:80],
            })
        for _m in PLURAL_SPACE.finditer(line):
            findings.append({
                "file": filename, "line": lineno, "code": "PLURAL_SPACE",
                "severity": "error",
                "message": "Plural suffix split by a space; join with ZWNJ: «کتاب‌ها» not «کتاب ها»",
                "snippet": line.strip()[:80],
            })
        if is_persian:
            bad = [c for c in line if c in ARABIC_CP]
            if bad:
                findings.append({
                    "file": filename, "line": lineno, "code": "ARABIC_CODEPOINT",
                    "severity": "error",
                    "message": "Arabic codepoint(s) " + ", ".join(
                        f"U+{ord(c):04X}→{ARABIC_CP[c]}" for c in sorted(set(bad))) +
                        " in Persian text — use the Persian characters",
                    "snippet": line.strip()[:80],
                })
        controls = [c for c in line if c in BIDI_OVERRIDES]
        if controls:
            findings.append({
                "file": filename, "line": lineno, "code": "BIDI_CONTROL",
                "severity": "warning",
                "message": "Bidi override/isolate control character(s) present "
                           "(" + ", ".join(f"U+{ord(c):04X}" for c in sorted(set(controls))) +
                           ") — invisible, can reorder rendered text and hide content",
                "snippet": line.strip()[:80],
            })
        if len(ARABIC_CHARS.findall(line)) >= 10 and len(LATIN_WORDS.findall(line)) >= 3:
            findings.append({
                "file": filename, "line": lineno, "code": "LATIN_RUN_IN_RTL",
                "severity": "info",
                "message": "Long Latin run inside an RTL line — verify the rendered order keeps the Latin phrase intact",
                "snippet": line.strip()[:80],
            })

    digit_kinds = sum(bool(p.search(text)) for p in (DIGITS_ASCII, DIGITS_FA, DIGITS_AR))
    if digit_kinds > 1:
        findings.append({
            "file": filename, "line": 0, "code": "DIGIT_MIXING",
            "severity": "warning",
            "message": "Mixed digit systems in one document (ASCII / Persian / Arabic digits) — pick one per locale and stay consistent",
            "snippet": "",
        })
    return findings


def score(findings: list[dict]) -> int:
    return max(0, 100 - sum(SEVERITY_PENALTY[f["severity"]] for f in findings))


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    all_findings: list[dict] = []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            all_findings.extend(check_text(fh.read(), path))
    if as_json:
        print(json.dumps({"score": score(all_findings), "findings": all_findings},
                         ensure_ascii=False, indent=2))
    else:
        for f in all_findings:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"[{f['severity'].upper():7}] {loc} {f['code']}: {f['message']}")
            if f["snippet"]:
                print(f"          {f['snippet']}")
        print(f"\nBidi score: {score(all_findings)}/100 · {len(all_findings)} finding(s)")
    return 1 if any(f["severity"] == "error" for f in all_findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
