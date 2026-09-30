"""Module 2 - add, get, list, update and delete expenses (always scoped to one user)."""

from __future__ import annotations

from .database import Database
from .exceptions import NotFoundError, ValidationError
from .logger import get_logger
from .models import Expense
from .validators import (
    validate_amount,
    validate_category,
    validate_date,
    validate_description,
    validate_id,
)

logger = get_logger("expenses")
_COLUMNS = "id, user_id, amount, category, description, date"


def _to_expense(row) -> Expense:
    return Expense(
        id=row["id"],
        user_id=row["user_id"],
        amount=row["amount"],
        category=row["category"],
        description=row["description"],
        date=row["date"],
    )


class ExpenseService:
    def __init__(self, db: Database):
        self.db = db

    def add(self, user_id, amount, category, date, description="") -> Expense:
        amount = validate_amount(amount)
        category = validate_category(category)
        date = validate_date(date)
        description = validate_description(description)
        cursor = self.db.execute(
            "INSERT INTO expenses (user_id, amount, category, description, date) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, description, date),
        )
        logger.info(
            "User %s added expense #%s (%.2f %s)",
            user_id,
            cursor.lastrowid,
            amount,
            category,
        )
        return Expense(cursor.lastrowid, user_id, amount, category, description, date)

    def get(self, user_id, expense_id) -> Expense:
        expense_id = validate_id(expense_id)
        row = self.db.query_one(
            f"SELECT {_COLUMNS} FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        )
        if row is None:
            raise NotFoundError(f"Expense #{expense_id} was not found.")
        return _to_expense(row)

    def list(self, user_id, category=None) -> list[Expense]:
        sql = f"SELECT {_COLUMNS} FROM expenses WHERE user_id = ?"
        params = [user_id]
        if category:
            sql += " AND category = ?"
            params.append(validate_category(category))
        sql += " ORDER BY date DESC, id DESC"
        return [_to_expense(row) for row in self.db.query(sql, params)]

    def update(
        self,
        user_id,
        expense_id,
        amount=None,
        category=None,
        date=None,
        description=None,
    ) -> Expense:
        current = self.get(user_id, expense_id)  # raises NotFoundError
        changes = {}
        if amount is not None:
            changes["amount"] = validate_amount(amount)
        if category is not None:
            changes["category"] = validate_category(category)
        if date is not None:
            changes["date"] = validate_date(date)
        if description is not None:
            changes["description"] = validate_description(description)
        if not changes:
            raise ValidationError("Nothing to update.")
        # column names come from the fixed dict above, values are bound parameters
        assignments = ", ".join(f"{column} = ?" for column in changes)
        self.db.execute(
            f"UPDATE expenses SET {assignments} WHERE id = ? AND user_id = ?",
            (*changes.values(), current.id, user_id),
        )
        logger.info(
            "User %s updated expense #%s (%s)",
            user_id,
            current.id,
            ", ".join(changes),
        )
        return self.get(user_id, current.id)

    def delete(self, user_id, expense_id) -> None:
        current = self.get(user_id, expense_id)  # raises NotFoundError
        self.db.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?", (current.id, user_id)
        )
        logger.info("User %s deleted expense #%s", user_id, current.id)
