"""Rule-based request analysis helpers."""

from datetime import datetime, timezone
import re

from app.logger import get_logger
from app.schemas import AnalyzeRequest, AnalyzeResponse


logger = get_logger(__name__)

_PATTERN_RULES: list[tuple[list[list[str]], int, str]] = [
    (
        [["ignore", "previous", "instructions"]],
        30,
        "Prompt tries to ignore previous instructions.",
    ),
    (
        [["reveal", "system", "prompt"]],
        35,
        "Prompt asks to reveal the system prompt.",
    ),
    (
        [["developer", "message"]],
        20,
        "Prompt references developer-only messages.",
    ),
    (
        [["override", "rules"]],
        25,
        "Prompt attempts to override safety or behavior rules.",
    ),
    (
        [["jailbreak"]],
        30,
        "Prompt explicitly mentions a jailbreak attempt.",
    ),
    (
        [["act", "as", "system"]],
        25,
        "Prompt tries to impersonate or replace system instructions.",
    ),
    (
        [["do", "not", "follow", "prior", "instructions"]],
        30,
        "Prompt tells the model not to follow prior instructions.",
    ),
    (
        [["print", "secrets"]],
        35,
        "Prompt asks for secrets to be printed.",
    ),
    (
        [["expose", "hidden", "prompt"]],
        35,
        "Prompt asks to expose hidden instructions or prompts.",
    ),
]


def _normalize_prompt(prompt: str) -> str:
    """Lowercase text, remove punctuation, and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", prompt.lower())).strip()


def _contains_terms_in_order(
    prompt_tokens: list[str],
    required_terms: list[str],
    max_gap: int = 3,
) -> bool:
    """Return True when the required terms appear in order with small gaps."""
    if not required_terms:
        return False

    search_start = 0
    last_match_index = -1

    for term in required_terms:
        found_index = -1

        for index in range(search_start, len(prompt_tokens)):
            if prompt_tokens[index] == term:
                found_index = index
                break

        if found_index == -1:
            return False

        if last_match_index != -1 and found_index - last_match_index - 1 > max_gap:
            return False

        last_match_index = found_index
        search_start = found_index + 1

    return True


def _rule_matches(prompt_tokens: list[str], rule_patterns: list[list[str]]) -> bool:
    """Return True when any pattern for a rule matches the prompt tokens."""
    return any(
        _contains_terms_in_order(prompt_tokens, required_terms)
        for required_terms in rule_patterns
    )


def _find_matches(normalized_prompt: str) -> list[tuple[int, str]]:
    """Return the score and reason for each matched rule."""
    matches: list[tuple[int, str]] = []
    prompt_tokens = normalized_prompt.split()

    for rule_patterns, score, reason in _PATTERN_RULES:
        if _rule_matches(prompt_tokens, rule_patterns):
            matches.append((score, reason))

    return matches


def _clamp_score(score: int) -> int:
    """Clamp the risk score to the inclusive range 0-100."""
    return max(0, min(score, 100))


def detect_prompt_injection(prompt: str) -> tuple[int, bool, list[str]]:
    """Score a prompt for common prompt injection patterns."""
    normalized_prompt = _normalize_prompt(prompt)
    matches = _find_matches(normalized_prompt)

    raw_score = sum(score for score, _ in matches)
    risk_score = _clamp_score(raw_score)
    reasons = [reason for _, reason in matches]
    is_malicious = risk_score >= 60

    return risk_score, is_malicious, reasons


def analyze_request(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a request payload using simple rule-based detection."""
    logger.info("Analyzing request prompt of length %s", len(payload.prompt))

    risk_score, is_malicious, reasons = detect_prompt_injection(payload.prompt)

    return AnalyzeResponse(
        risk_score=risk_score,
        is_malicious=is_malicious,
        reasons=reasons,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )
