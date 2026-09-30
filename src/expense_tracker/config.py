"""Central configuration: paths, categories, limits and hashing settings."""

from pathlib import Path

# ---- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
EXPORT_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "expenses.db"
LOG_FILE = LOG_DIR / "app.log"
# ---- Business rules --------------------------------------------------------
CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Shopping",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]
USERNAME_MIN, USERNAME_MAX = 3, 20
PASSWORD_MIN, PASSWORD_MAX = 6, 64
MAX_AMOUNT = 10_000_000
MAX_DESCRIPTION = 100
# Budget alert thresholds (fraction of the monthly limit)
WARN_THRESHOLD = 0.80
ALERT_THRESHOLD = 1.00
# Width (characters) of the longest bar in the monthly report
BAR_WIDTH = 12
# ---- Password hashing (PBKDF2-HMAC-SHA256) ---------------------------------
PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16
