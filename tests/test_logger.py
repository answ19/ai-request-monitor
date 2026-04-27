"""Tests for simple JSONL logging."""

from app.logger import append_analysis_log


class _BrokenPath:
    """Test double that raises an I/O error when opened."""

    def open(self, *args, **kwargs):
        raise OSError("disk is unavailable")


def test_append_analysis_log_ignores_os_errors(monkeypatch) -> None:
    monkeypatch.setattr("app.logger._LOG_FILE_PATH", _BrokenPath())

    append_analysis_log(
        prompt="test prompt",
        risk_score=10,
        is_malicious=False,
        reasons=[],
        timestamp="2026-04-23T00:00:00Z",
    )
