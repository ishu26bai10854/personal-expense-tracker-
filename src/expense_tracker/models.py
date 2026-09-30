"""Plain data objects returned by the services."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str


@dataclass
class Expense:
    id: int
    user_id: int
    amount: float
    category: str
    description: str
    date: str
