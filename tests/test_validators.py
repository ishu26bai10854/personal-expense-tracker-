import unittest

from src.expense_tracker import validators as v
from src.expense_tracker.exceptions import ValidationError


class ValidatorTests(unittest.TestCase):
    def test_amount(self):
        self.assertEqual(v.validate_amount("250"), 250.0)
        self.assertEqual(v.validate_amount("12.345"), 12.35)
        for bad in ("-5", "0", "abc", "", "nan", "inf", "99999999999", True):
            with self.assertRaises(ValidationError):
                v.validate_amount(bad)

    def test_date(self):
        self.assertEqual(v.validate_date("2025-03-01"), "2025-03-01")
        for bad in ("2025-3-1", "2025-02-30", "01-03-2025", "", "1999-01-01"):
            with self.assertRaises(ValidationError):
                v.validate_date(bad)

    def test_month(self):
        self.assertEqual(v.validate_month("2025-03"), "2025-03")
        for bad in ("2025-13", "2025-3", "March", ""):
            with self.assertRaises(ValidationError):
                v.validate_month(bad)

    def test_category(self):
        self.assertEqual(v.validate_category(" fOOd "), "Food")
        with self.assertRaises(ValidationError):
            v.validate_category("Gadgets")

    def test_username(self):
        self.assertEqual(v.validate_username(" Alice_1 "), "alice_1")
        for bad in ("ab", "x" * 21, "bad name", "bob;drop", ""):
            with self.assertRaises(ValidationError):
                v.validate_username(bad)

    def test_password(self):
        self.assertEqual(v.validate_password("secret12"), "secret12")
        for bad in ("sh0rt", "onlyletters", "12345678", "x" * 65):
            with self.assertRaises(ValidationError):
                v.validate_password(bad)


if __name__ == "__main__":
    unittest.main()
