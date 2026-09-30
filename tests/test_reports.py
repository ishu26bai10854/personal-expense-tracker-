import csv
import tempfile
import unittest
from pathlib import Path

from src.expense_tracker.database import Database
from src.expense_tracker.exceptions import ValidationError
from src.expense_tracker.expenses import ExpenseService
from src.expense_tracker.reports import ReportService


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.addCleanup(self.db.close)
        self.db.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES ('alice', 'h', 's')"
        )
        self.uid = 1
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.expenses = ExpenseService(self.db)
        self.reports = ReportService(self.db, export_dir=self.tmp.name)
        self.expenses.add(self.uid, 250, "Food", "2025-03-01", "Lunch with friends")
        self.expenses.add(self.uid, 1200, "Bills", "2025-03-05", "Electricity bill")
        self.expenses.add(self.uid, 400, "Transport", "2025-03-09", "Metro card")
        self.expenses.add(self.uid, 999, "Food", "2025-04-01", "Other month")

    def test_monthly_totals(self):
        summary = self.reports.monthly_summary(self.uid, "2025-03")
        self.assertEqual(summary["total"], 1850.0)
        self.assertEqual(summary["count"], 3)
        self.assertEqual(
            [c["category"] for c in summary["categories"]],
            ["Bills", "Transport", "Food"],
        )
        self.assertEqual([c["percent"] for c in summary["categories"]], [65, 22, 14])

    def test_empty_month(self):
        summary = self.reports.monthly_summary(self.uid, "2020-01")
        self.assertEqual(
            (summary["total"], summary["count"], summary["categories"]), (0, 0, [])
        )
        self.assertEqual(self.reports.budget_alerts(self.uid, "2020-01"), [])

    def test_budget_alerts(self):
        self.reports.set_budget(self.uid, "Food", 300)
        self.reports.set_budget(self.uid, "Bills", 5000)
        alerts = self.reports.budget_alerts(self.uid, "2025-03")
        self.assertEqual(alerts, ["WARNING: Food at 83% of budget"])
        self.expenses.add(self.uid, 100, "Food", "2025-03-20")
        alerts = self.reports.budget_alerts(self.uid, "2025-03")
        self.assertEqual(len(alerts), 1)
        self.assertTrue(alerts[0].startswith("ALERT: Food at 116%"))

    def test_budget_overwrite(self):
        self.reports.set_budget(self.uid, "Food", 300)
        self.reports.set_budget(self.uid, "food", 500)
        self.assertEqual(self.reports.get_budgets(self.uid), {"Food": 500.0})
        with self.assertRaises(ValidationError):
            self.reports.set_budget(self.uid, "Food", -1)

    def test_csv_export(self):
        self.expenses.add(self.uid, 5, "Other", "2025-03-11", "=1+1")
        path = Path(self.reports.export_csv(self.uid, "march"))
        self.assertEqual(path.name, "march.csv")
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(rows[0], ["id", "date", "category", "amount", "description"])
        self.assertEqual(len(rows), 1 + 5)
        self.assertEqual(rows[1][1:4], ["2025-03-01", "Food", "250.00"])
        self.assertIn("'=1+1", [r[4] for r in rows])  # formula neutralised

    def test_path_traversal_rejected(self):
        for name in (
            "../evil.csv",
            "a/b.csv",
            "..\\x.csv",
            "/etc/passwd",
            "",
            "bad;name.csv",
        ):
            with self.assertRaises(ValidationError):
                self.reports.export_csv(self.uid, name)
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
