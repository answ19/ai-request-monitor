"""Logging utilities for the AI Request Monitor project."""

import json
import logging
from pathlib import Path


_LOG_FILE_PATH = Path(__file__).resolve().parent.parent / "logs.jsonl"


def get_logger(name: str) -> logging.Logger:
    """Create or return a configured logger instance."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger(name)


def append_analysis_log(
    prompt: str,
    risk_score: int,
    is_malicious: bool,
    reasons: list[str],
    timestamp: str,
) -> None:
    """Append a single analysis record to the project JSONL log file."""
    record = {
        "prompt": prompt,
        "risk_score": risk_score,
        "is_malicious": is_malicious,
        "reasons": reasons,
        "timestamp": timestamp,
    }

    try:
        with _LOG_FILE_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(record) + "\n")
    except OSError as exc:
        logging.getLogger(__name__).warning("Failed to write analysis log: %s", exc)
