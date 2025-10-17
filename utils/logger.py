import logging
import os
import sys
from typing import Optional


_configured = False


def _configure_root(level: Optional[str] = None) -> None:
    global _configured
    if _configured:
        return

    lvl_name = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    lvl = getattr(logging, lvl_name, logging.INFO)

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(lvl)
    # Avoid duplicate handlers if reloaded
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(handler)

    # Quiet down noisy libraries by default
    logging.getLogger("werkzeug").setLevel(os.getenv("WERKZEUG_LOG_LEVEL", "WARNING"))
    logging.getLogger("urllib3").setLevel("WARNING")

    _configured = True


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    _configure_root(level)
    return logging.getLogger(name)

