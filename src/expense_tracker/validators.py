"""Input validation. Every function returns the cleaned value or raises ValidationError."""

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from . import config
from .exceptions import ValidationError

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
_FILENAME_RE = re.compile(r"^[A-Za-z0-9_\-. ]+$")


def validate_username(username):
    if not isinstance(username, str):
        raise ValidationError("Username must be text.")
    username = username.strip()
    if not config.USERNAME_MIN <= len(username) <= config.USERNAME_MAX:
        raise ValidationError(
            f"Username must be {config.USERNAME_MIN}-{config.USERNAME_MAX} characters long."
        )
    if not _USERNAME_RE.match(username):
        raise ValidationError(
            "Username may contain only letters, digits and underscore."
        )
    return username.lower()


def validate_password(password):
    if not isinstance(password, str):
        raise ValidationError("Password must be text.")
    if not config.PASSWORD_MIN <= len(password) <= config.PASSWORD_MAX:
        raise ValidationError(
            f"Password must be {config.PASSWORD_MIN}-{config.PASSWORD_MAX} characters long."
        )
    if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
        raise ValidationError(
            "Password must contain at least one letter and one digit."
        )
    return password


def validate_amount(value):
    """Return a positive amount rounded to 2 decimals."""
    if isinstance(value, bool):
        raise ValidationError("Amount must be a number.")
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValidationError("Amount must be a number.") from None
    if not amount.is_finite():
        raise ValidationError("Amount must be a number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if amount > config.MAX_AMOUNT:
        raise ValidationError(f"Amount must not exceed {config.MAX_AMOUNT:,}.")
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount <= 0:
        raise ValidationError("Amount must be at least 0.01.")
    return float(amount)


def validate_date(value):
    """Accept a real calendar date written as YYYY-MM-DD."""
    if not isinstance(value, str) or not _DATE_RE.match(value.strip()):
        raise ValidationError("Date must be in YYYY-MM-DD format.")
    value = value.strip()
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Date is not a valid calendar date.") from None
    if parsed.year < 2000:
        raise ValidationError("Date must be in the year 2000 or later.")
    return value


def validate_month(value):
    if not isinstance(value, str) or not _MONTH_RE.match(value.strip()):
        raise ValidationError("Month must be in YYYY-MM format.")
    return value.strip()


def validate_category(value):
    """Case-insensitive match against the fixed category list."""
    if not isinstance(value, str):
        raise ValidationError("Category must be text.")
    wanted = value.strip().lower()
    for category in config.CATEGORIES:
        if category.lower() == wanted:
            return category
    raise ValidationError(
        "Category must be one of: " + ", ".join(config.CATEGORIES) + "."
    )


def validate_description(value):
    value = (value or "").strip()
    if len(value) > config.MAX_DESCRIPTION:
        raise ValidationError(
            f"Description must be at most {config.MAX_DESCRIPTION} characters."
        )
    return value


def validate_id(value):
    try:
        number = int(str(value).strip())
    except ValueError:
        raise ValidationError("ID must be a whole number.") from None
    if number <= 0:
        raise ValidationError("ID must be a positive number.")
    return number


def validate_filename(value):
    """Plain file name only - blocks path traversal such as '../x.csv' or 'a/b.csv'."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("File name must not be empty.")
    value = value.strip()
    if ".." in value or "/" in value or "\\" in value or not _FILENAME_RE.match(value):
        raise ValidationError(
            "Invalid file name (use letters, digits, '-', '_' and '.')."
        )
    if not value.lower().endswith(".csv"):
        value += ".csv"
    return value
