"""Custom exceptions so the CLI can tell user mistakes apart from real bugs."""


class ExpenseTrackerError(Exception):
    """Base class for all expected (user-facing) errors."""


class ValidationError(ExpenseTrackerError):
    """Input failed validation."""


class AuthError(ExpenseTrackerError):
    """Authentication failed."""


class NotFoundError(ExpenseTrackerError):
    """Requested record does not exist (or belongs to another user)."""
