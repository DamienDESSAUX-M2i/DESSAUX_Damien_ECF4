import logging
import logging.config
from pathlib import Path

import yaml

DEFAULT_LOG_DIR = Path("api/logs")
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "api.log"


def set_up_logging(log_config_path: Path, log_file: Path | None = None) -> None:
    """Initialize logging configuration from YAML file.

    Args:
        log_config_path: Path to YAML config file
        log_file: Optional override for log file path
    """

    if not log_config_path.exists():
        raise FileNotFoundError(f"Logging config not found: {log_config_path}")

    with open(log_config_path, "r") as f:
        config = yaml.safe_load(f)

    log_file = log_file or DEFAULT_LOG_FILE
    log_file = log_file.resolve()

    log_dir = log_file.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    if "handlers" in config and "file" in config["handlers"]:
        config["handlers"]["file"]["filename"] = str(log_file)

    logging.config.dictConfig(config)


def get_logger(name: str = "api") -> logging.Logger:
    """Retrieve configured logger."""
    return logging.getLogger(name)
