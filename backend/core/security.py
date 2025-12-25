from fastapi import HTTPException

UNSAFE_KEYWORDS = [
    "sexual", "porn", "xxx", "nude", "naked",
    "kill", "murder", "suicide", "die", "death to",
    "hate", "racist", "slur", "nazi",
    "scam", "fraud", "lottery", "winner"
]

def check_safety(text: str) -> tuple[bool, str]:
    """
    Checks text for unsafe content.
    Returns (is_safe, reason).
    """
    content = text.lower()
    for keyword in UNSAFE_KEYWORDS:
        if keyword in content:
            return False, f"Content contains unsafe keyword '{keyword}'"
    return True, ""

def validate_content(subject: str, body: str):
    """
    Basic guardrail to check for inappropriate, harmful, or sexual content.
    Raises HTTPException if content is deemed unsafe.
    """
    is_safe, reason = check_safety(subject + " " + body)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Request rejected: {reason}")
    return True
