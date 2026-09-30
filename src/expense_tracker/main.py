"""Program entry point."""

import sys

from . import config
from .cli import CLI
from .database import Database
from .logger import get_logger, setup_logging


def main() -> int:
    setup_logging()
    logger = get_logger("main")
    logger.info("Application started")
    db = None
    try:
        db = Database(config.DB_PATH)
        CLI(db).run()
        return 0
    except Exception:  # top-level handler: never crash with a raw traceback
        logger.exception("Fatal error")
        print("A fatal error occurred. Please check logs/app.log for details.")
        return 1
    finally:
        if db is not None:
            db.close()
        logger.info("Application stopped")


if __name__ == "__main__":
    sys.exit(main())
