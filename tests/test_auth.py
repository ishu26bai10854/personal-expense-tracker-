import unittest
from unittest import mock

from src.expense_tracker import config
from src.expense_tracker.auth import AuthService
from src.expense_tracker.database import Database
from src.expense_tracker.exceptions import AuthError, ValidationError


class AuthTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(config, "PBKDF2_ITERATIONS", 1000)  # fast tests
        patcher.start()
        self.addCleanup(patcher.stop)
        self.db = Database(":memory:")
        self.addCleanup(self.db.close)
        self.auth = AuthService(self.db)

    def test_login_success(self):
        registered = self.auth.register("alice", "secret12")
        user = self.auth.login("ALICE", "secret12")
        self.assertEqual(user.id, registered.id)
        self.assertEqual(user.username, "alice")

    def test_login_wrong_password(self):
        self.auth.register("alice", "secret12")
        with self.assertRaises(AuthError):
            self.auth.login("alice", "wrong123")

    def test_login_unknown_user(self):
        with self.assertRaises(AuthError):
            self.auth.login("nobody", "secret12")

    def test_duplicate_username(self):
        self.auth.register("alice", "secret12")
        with self.assertRaises(ValidationError):
            self.auth.register("Alice", "another99")

    def test_password_is_hashed_and_salted(self):
        self.auth.register("alice", "secret12")
        self.auth.register("bobby", "secret12")
        rows = self.db.query("SELECT password_hash, salt FROM users ORDER BY id")
        self.assertNotIn("secret12", rows[0]["password_hash"])
        self.assertEqual(len(bytes.fromhex(rows[0]["salt"])), config.SALT_BYTES)
        self.assertNotEqual(rows[0]["password_hash"], rows[1]["password_hash"])

    def test_weak_password_rejected(self):
        with self.assertRaises(ValidationError):
            self.auth.register("alice", "abc")
        self.assertEqual(self.db.query("SELECT COUNT(*) AS n FROM users")[0]["n"], 0)


if __name__ == "__main__":
    unittest.main()
