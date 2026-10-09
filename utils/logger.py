import logging
from pathlib import Path

# Find the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Create the logs directory if it does not exist
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log file location
LOG_FILE = LOG_DIR / "zecpath.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)


def get_logger(name):
    """Return a logger for the specified module."""
    return logging.getLogger(name)