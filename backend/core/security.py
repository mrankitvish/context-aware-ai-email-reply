from fastapi import HTTPException

UNSAFE_KEYWORDS = [
    # Basic keywords
    "sexual", "sex", "porn", "xxx", "nude", "naked",
    "kill", "murder", "suicide", "die", "death to",
    "hate", "racist", "slur", "nazi",
    "scam", "fraud", "lottery", "winner",

    # Explicit sexual content (keep narrow)
    "explicit sexual", "hardcore porn", "sex video",
    "nude pics", "naked photos", "sexual favors",

    # Sexual content involving minors (always block)
    "child porn", "cp", "underage sex", "minor nude",
    "pedo", "pedophile",

    # Direct violence / threats (not general discussion)
    "i will kill", "threaten your life", "death threat",
    "bomb threat", "shoot you", "stab you",

    # Self-harm intent (first-person phrasing)
    "kill myself", "end my life", "want to die",
    "suicide note",

    # Hate / extremism slogans (not academic mentions)
    "white power", "heil hitler", "kkk",
    "death to jews", "death to muslims",

    # Scams / fraud (email is ground zero here)
    "lottery winner", "you have won",
    "urgent transfer", "wire transfer immediately",
    "inheritance funds", "beneficiary",
    "bank verification required",
    "confirm your account",
    "limited time offer",
    "act now",

    # Phishing / social engineering
    "password reset required",
    "verify your identity",
    "login attempt detected",
    "click below to verify",
    "suspended account",

    # Malware / malicious intent
    "attached executable",
    "enable macros",
    "download attachment",
    "invoice.zip",
    "payment receipt.exe",

    # Extortion / blackmail
    "i have your password",
    "recorded you",
    "send bitcoin",
    "pay within 24 hours",
    "or else",

    # Piracy distribution (email-specific)
    "cracked software",
    "license key attached",
    "serial number included"
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
