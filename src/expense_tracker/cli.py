"""Presentation layer: menu loop and output formatting."""

from __future__ import annotations

import getpass
from datetime import date

from . import config
from .auth import AuthService
from .database import Database
from .exceptions import AuthError, NotFoundError, ValidationError
from .expenses import ExpenseService
from .logger import get_logger
from .reports import ReportService

logger = get_logger("cli")
GUEST_MENU = "1 Register 2 Login 0 Exit"
USER_MENU = (
    "1 Add 2 List 3 Update 4 Delete 5 Monthly report "
    "6 Set budget 7 Export CSV 0 Logout"
)


class CLI:
    """Interactive menus. Input/output functions can be replaced for scripted demos."""

    def __init__(
        self,
        db: Database,
        input_fn=input,
        password_fn=getpass.getpass,
        print_fn=print,
        export_dir=None,
    ):
        self.auth = AuthService(db)
        self.expenses = ExpenseService(db)
        self.reports = ReportService(db, export_dir)
        self._input, self._password, self._print = input_fn, password_fn, print_fn
        self.user = None

    # ---- helpers -----------------------------------------------------------
    def _ask(self, prompt, default=None):
        text = self._input(f"{prompt}: ").strip()
        return text if text else default

    def _safe(self, action):
        """Run one menu action; show expected errors, log unexpected ones."""
        try:
            action()
        except (ValidationError, AuthError, NotFoundError) as exc:
            self._print(f" Error: {exc}")
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception:
            logger.exception("Unexpected error in menu action")
            self._print(" Unexpected error - details were written to logs/app.log")

    # ---- main loop ---------------------------------------------------------
    def run(self):
        try:
            while True:
                if self.user is None:
                    if not self._guest_menu():
                        break
                else:
                    self._user_menu()
        except (KeyboardInterrupt, EOFError):
            self._print("\nInterrupted.")
        self._print("Goodbye!")

    def _guest_menu(self) -> bool:
        self._print("\n=== Personal Expense Tracker ===")
        self._print(GUEST_MENU)
        choice = self._ask("Choose", "")
        if choice == "1":
            self._safe(self._register)
        elif choice == "2":
            self._safe(self._login)
        elif choice == "0":
            return False
        else:
            self._print(" Please choose 1, 2 or 0.")
        return True

    def _user_menu(self):
        self._print(f"\n--- Menu ({self.user.username}) ---")
        self._print(USER_MENU)
        actions = {
            "1": self._add,
            "2": self._list,
            "3": self._update,
            "4": self._delete,
            "5": self._report,
            "6": self._budget,
            "7": self._export,
        }
        choice = self._ask("Choose", "")
        if choice == "0":
            logger.info("User %r logged out", self.user.username)
            self.user = None
            self._print(" Logged out.")
        elif choice in actions:
            self._safe(actions[choice])
        else:
            self._print(" Please choose a number from the menu.")

    # ---- account actions ---------------------------------------------------
    def _register(self):
        username = self._ask("Username", "")
        password = self._password("Password: ")
        self.auth.register(username, password)
        self._print(" Registered. You can log in now.")

    def _login(self):
        username = self._ask("Username", "")
        password = self._password("Password: ")
        self.user = self.auth.login(username, password)

    # ---- expense actions ---------------------------------------------------
    def _add(self):
        amount = self._ask("Amount", "")
        category = self._ask(f"Category [{'/'.join(config.CATEGORIES)}]", "")
        today = date.today().isoformat()
        when = self._ask(f"Date [{today}]", today)
        description = self._ask("Description", "")
        expense = self.expenses.add(self.user.id, amount, category, when, description)
        self._print(f" Added expense #{expense.id}")

    def _list(self):
        category = self._ask("Filter category (blank = all)")
        items = self.expenses.list(self.user.id, category)
        if not items:
            self._print(" No expenses found.")
            return
        self._print(
            f" {'ID':>4} {'Date':<10} {'Category':<13}{'Amount':>10} Description"
        )
        for e in items:
            self._print(
                f" {e.id:>4} {e.date:<10} {e.category:<13}{e.amount:>10.2f} {e.description}"
            )

    def _update(self):
        current = self.expenses.get(self.user.id, self._ask("Expense ID", ""))
        self._print(" Leave a field blank to keep its current value.")
        amount = self._ask(f"Amount [{current.amount:.2f}]")
        category = self._ask(f"Category [{current.category}]")
        when = self._ask(f"Date [{current.date}]")
        description = self._ask(f"Description [{current.description}]")
        self.expenses.update(
            self.user.id, current.id, amount, category, when, description
        )
        self._print(f" Updated expense #{current.id}")

    def _delete(self):
        current = self.expenses.get(self.user.id, self._ask("Expense ID", ""))
        answer = self._ask(
            f"Delete #{current.id} ({current.category} {current.amount:.2f})? [y/N]",
            "n",
        )
        if answer.lower() == "y":
            self.expenses.delete(self.user.id, current.id)
            self._print(f" Deleted expense #{current.id}")
        else:
            self._print(" Cancelled.")

    # ---- report actions ----------------------------------------------------
    def _report(self):
        this_month = date.today().strftime("%Y-%m")
        month = self._ask(f"Month YYYY-MM [{this_month}]", this_month)
        summary = self.reports.monthly_summary(self.user.id, month)
        if summary["count"] == 0:
            self._print(f" No expenses recorded for {summary['month']}.")
        else:
            self._print(
                f" Summary for {summary['month']}: total {summary['total']:.2f} "
                f"across {summary['count']} expense(s)"
            )
            biggest = max(c["total"] for c in summary["categories"])
            for c in summary["categories"]:
                bar = "#" * max(1, int(c["total"] / biggest * config.BAR_WIDTH))
                self._print(
                    f" {c['category']:<13}{c['total']:>10.2f} "
                    f"{bar:<{config.BAR_WIDTH}} {c['percent']:>3}%"
                )
        for alert in self.reports.budget_alerts(self.user.id, summary["month"]):
            self._print(f" ! {alert}")

    def _budget(self):
        category = self._ask(f"Category [{'/'.join(config.CATEGORIES)}]", "")
        limit = self._ask("Monthly limit", "")
        self.reports.set_budget(self.user.id, category, limit)
        self._print(" Budget saved.")

    def _export(self):
        name = self._ask("File name [expenses.csv]", "expenses.csv")
        path = self.reports.export_csv(self.user.id, name)
        self._print(f" Exported to {path}")
