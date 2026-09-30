"""Module 1 - user registration and login."""

from __future__ import annotations

import hashlib
import hmac
import os

from . import config
from .database import Database
from .exceptions import AuthError, ValidationError
from .logger import get_logger
from .models import User
from .validators import validate_password, validate_username

logger = get_logger("auth")
_INVALID = "Invalid username or password."


def _hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, config.PBKDF2_ITERATIONS
    ).hex()


class AuthService:
    def __init__(self, db: Database):
        self.db = db

    def register(self, username: str, password: str) -> User:
        username = validate_username(username)
        validate_password(password)
        if self.db.query_one("SELECT 1 FROM users WHERE username = ?", (username,)):
            logger.warning(
                "Registration rejected: username %r already exists", username
            )
            raise ValidationError("That username is already taken.")

        salt = os.urandom(config.SALT_BYTES)
        cursor = self.db.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, _hash(password, salt), salt.hex()),
        )
        logger.info("Registered user %r (id=%s)", username, cursor.lastrowid)
        return User(cursor.lastrowid, username)

    def login(self, username: str, password: str) -> User:
        try:
            username = validate_username(username)
        except ValidationError:
            raise AuthError(_INVALID) from None
        if not isinstance(password, str):
            raise AuthError(_INVALID)

        row = self.db.query_one(
            "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
            (username,),
        )
        if row is None:
            _hash(password, b"\x00" * config.SALT_BYTES)  # keep timing similar
            logger.warning("Failed login: unknown username %r", username)
            raise AuthError(_INVALID)

        attempt = _hash(password, bytes.fromhex(row["salt"]))
        # constant-time comparison during login
        if not hmac.compare_digest(attempt, row["password_hash"]):
            logger.warning("Failed login: wrong password for %r", username)
            raise AuthError(_INVALID)

        logger.info("User %r logged in", username)
        return User(row["id"], row["username"])
