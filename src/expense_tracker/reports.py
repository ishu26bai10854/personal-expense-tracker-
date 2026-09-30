"""Module 3 - monthly summary, budgets and alerts, CSV export."""

from __future__ import annotations

import csv
from pathlib import Path

from . import config
from .database import Database
from .exceptions import ValidationError
from .logger import get_logger
from .validators import (
    validate_amount,
    validate_category,
    validate_filename,
    validate_month,
)

logger = get_logger("reports")


def _csv_safe(text: str) -> str:
    """Stop spreadsheet programs from running text such as '=SUM(...)' as a formula."""
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


class ReportService:
    def __init__(self, db: Database, export_dir=None):
        self.db = db
        self.export_dir = Path(export_dir or config.EXPORT_DIR)

    # ---- monthly summary ---------------------------------------------------
    def monthly_summary(self, user_id, month) -> dict:
        month = validate_month(month)
        rows = self.db.query(
            "SELECT category, SUM(amount) AS total, COUNT(*) AS n FROM expenses "
            "WHERE user_id = ? AND substr(date, 1, 7) = ? GROUP BY category ORDER BY total DESC",
            (user_id, month),
        )
        grand_total = sum(row["total"] for row in rows)
        categories = [
            {
                "category": row["category"],
                "total": round(row["total"], 2),
                "count": row["n"],
                "percent": (
                    round(row["total"] / grand_total * 100) if grand_total else 0
                ),
            }
            for row in rows
        ]
        return {
            "month": month,
            "total": round(grand_total, 2),
            "count": sum(row["n"] for row in rows),
            "categories": categories,
        }

    # ---- budgets -----------------------------------------------------------
    def set_budget(self, user_id, category, limit) -> None:
        category = validate_category(category)
        limit = validate_amount(limit)
        self.db.execute(
            "INSERT OR REPLACE INTO budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)",
            (user_id, category, limit),
        )
        logger.info("User %s set budget %s = %.2f", user_id, category, limit)

    def get_budgets(self, user_id) -> dict:
        rows = self.db.query(
            "SELECT category, monthly_limit FROM budgets WHERE user_id = ? ORDER BY category",
            (user_id,),
        )
        return {row["category"]: row["monthly_limit"] for row in rows}

    def budget_alerts(self, user_id, month) -> list[str]:
        """Return a message for every category at 80% or more of its monthly budget."""
        spent = {
            c["category"]: c["total"]
            for c in self.monthly_summary(user_id, month)["categories"]
        }
        alerts = []
        for category, limit in self.get_budgets(user_id).items():
            ratio = round(spent.get(category, 0) / limit, 6)
            percent = int(ratio * 100)
            if ratio >= config.ALERT_THRESHOLD:
                alerts.append(
                    f"ALERT: {category} at {percent}% of budget - limit exceeded"
                )
            elif ratio >= config.WARN_THRESHOLD:
                alerts.append(f"WARNING: {category} at {percent}% of budget")
        return alerts

    # ---- CSV export --------------------------------------------------------
    def export_csv(self, user_id, filename) -> str:
        filename = validate_filename(filename)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        target = (self.export_dir / filename).resolve()
        if target.parent != self.export_dir.resolve():  # second line of defence
            raise ValidationError("Invalid file name.")
        rows = self.db.query(
            "SELECT id, date, category, amount, description FROM expenses "
            "WHERE user_id = ? ORDER BY date, id",
            (user_id,),
        )
        with open(target, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["id", "date", "category", "amount", "description"])
            for row in rows:
                writer.writerow(
                    [
                        row["id"],
                        row["date"],
                        row["category"],
                        f"{row['amount']:.2f}",
                        _csv_safe(row["description"]),
                    ]
                )
        logger.info("User %s exported %d expense(s) to %s", user_id, len(rows), target)
        return str(target)
