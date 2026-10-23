"""Tests for bidi_check — broken vs clean Arabic-script fixtures.

Run: python3 -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "rtl-text" / "scripts"))
from bidi_check import check_text, score  # noqa: E402

BAD_FA = """این متن خراب است و می شود آن را دید.
کتاب ها روی میز هستند و بچه ها بازی می کنند.
اين خط با حروف عربي نوشته شده است و حرف گ هم دارد.
عدد 123 و عدد ۴۵۶ با هم قاطی شده‌اند.
"""

GOOD_FA = """این متن درست است و می‌شود آن را دید.
کتاب‌ها روی میز هستند و بچه‌ها بازی می‌کنند.
این خط با حروف فارسی نوشته شده و عدد ۴۵۶ دارد.
سال ۲۰۲۶ و نسخهٔ برنامه همه با عدد فارسی‌اند.
"""

BIDI_HIDDEN = "متن عادی با نویسهٔ پنهان ‮ در وسط جمله."


def codes(text):
    return [f["code"] for f in check_text(text)]


class TestBidiCheck(unittest.TestCase):
    def test_zwnj_space_detected(self):
        self.assertIn("ZWNJ_SPACE", codes(BAD_FA))

    def test_plural_space_detected(self):
        self.assertIn("PLURAL_SPACE", codes(BAD_FA))

    def test_arabic_codepoint_in_persian_detected(self):
        self.assertIn("ARABIC_CODEPOINT", codes(BAD_FA))

    def test_digit_mixing_detected(self):
        self.assertIn("DIGIT_MIXING", codes(BAD_FA))

    def test_bidi_control_detected(self):
        self.assertIn("BIDI_CONTROL", codes(BIDI_HIDDEN))

    def test_clean_persian_has_no_errors(self):
        errors = [f for f in check_text(GOOD_FA) if f["severity"] == "error"]
        self.assertEqual(errors, [])

    def test_good_scores_higher_than_bad(self):
        self.assertGreater(score(check_text(GOOD_FA)), score(check_text(BAD_FA)))

    def test_pure_english_untouched(self):
        self.assertEqual(check_text("Hello world, this is plain English text."), [])


if __name__ == "__main__":
    unittest.main()
