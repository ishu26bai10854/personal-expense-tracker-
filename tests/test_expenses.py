import unittest

from src.expense_tracker.database import Database
from src.expense_tracker.exceptions import NotFoundError, ValidationError
from src.expense_tracker.expenses import ExpenseService


class ExpenseTests(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.addCleanup(self.db.close)
        for name in ("alice", "bobby"):
            self.db.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, 'h', 's')",
                (name,),
            )
        self.svc = ExpenseService(self.db)
        self.alice, self.bob = 1, 2

    def test_add_and_get(self):
        added = self.svc.add(self.alice, "250", "food", "2025-03-01", "Lunch")
        fetched = self.svc.get(self.alice, added.id)
        self.assertEqual(fetched.amount, 250.0)
        self.assertEqual(fetched.category, "Food")
        self.assertEqual(fetched.description, "Lunch")

    def test_list_and_filter(self):
        self.svc.add(self.alice, 250, "Food", "2025-03-01")
        self.svc.add(self.alice, 1200, "Bills", "2025-03-05")
        self.svc.add(self.alice, 400, "Transport", "2025-03-09")
        everything = self.svc.list(self.alice)
        self.assertEqual(
            [e.date for e in everything],
            ["2025-03-09", "2025-03-05", "2025-03-01"],
        )
        only_bills = self.svc.list(self.alice, "bills")
        self.assertEqual([e.amount for e in only_bills], [1200.0])

    def test_update(self):
        added = self.svc.add(self.alice, 250, "Food", "2025-03-01", "Lunch")
        updated = self.svc.update(
            self.alice, added.id, amount="300", description="Dinner"
        )
        self.assertEqual((updated.amount, updated.description), (300.0, "Dinner"))
        self.assertEqual(updated.category, "Food")  # untouched
        with self.assertRaises(ValidationError):
            self.svc.update(self.alice, added.id)  # nothing to change

    def test_delete(self):
        added = self.svc.add(self.alice, 250, "Food", "2025-03-01")
        self.svc.delete(self.alice, added.id)
        with self.assertRaises(NotFoundError):
            self.svc.get(self.alice, added.id)
        with self.assertRaises(NotFoundError):
            self.svc.delete(self.alice, added.id)

    def test_invalid_input(self):
        bad_calls = [
            (-5, "Food", "2025-03-10"),
            (10, "Gadgets", "2025-03-10"),
            (10, "Food", "2025-02-31"),
        ]
        for amount, category, when in bad_calls:
            with self.assertRaises(ValidationError):
                self.svc.add(self.alice, amount, category, when)
        self.assertEqual(self.svc.list(self.alice), [])

    def test_user_data_isolation(self):
        secret = self.svc.add(self.alice, 999, "Health", "2025-03-01", "private")
        self.assertEqual(self.svc.list(self.bob), [])
        with self.assertRaises(NotFoundError):
            self.svc.get(self.bob, secret.id)
        with self.assertRaises(NotFoundError):
            self.svc.update(self.bob, secret.id, amount=1)
        with self.assertRaises(NotFoundError):
            self.svc.delete(self.bob, secret.id)
        self.assertEqual(self.svc.get(self.alice, secret.id).amount, 999.0)


if __name__ == "__main__":
    unittest.main()
