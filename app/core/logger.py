import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create reusable logger
logger = logging.getLogger(__name__)