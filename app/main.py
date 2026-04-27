"""FastAPI application entrypoint for AI Request Monitor."""

from datetime import datetime, timezone

from fastapi import FastAPI

from app.detector import detect_prompt_injection
from app.logger import append_analysis_log
from app.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse


app = FastAPI(
    title="AI Request Monitor",
    description="A minimal FastAPI starter project for analyzing AI requests.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a simple health status for the API."""
    return HealthResponse(status="ok")


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a request payload for prompt injection patterns."""
    risk_score, is_malicious, reasons = detect_prompt_injection(payload.prompt)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    append_analysis_log(
        prompt=payload.prompt,
        risk_score=risk_score,
        is_malicious=is_malicious,
        reasons=reasons,
        timestamp=timestamp,
    )

    return AnalyzeResponse(
        risk_score=risk_score,
        is_malicious=is_malicious,
        reasons=reasons,
        timestamp=timestamp,
    )
