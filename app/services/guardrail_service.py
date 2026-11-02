import re


INSURANCE_KEYWORDS = {
    "insurance",
    "health insurance",
    "medical insurance",
    "policy",
    "policies",
    "coverage",
    "covered",
    "premium",
    "premiums",
    "deductible",
    "deductibles",
    "copay",
    "copayment",
    "coinsurance",
    "claim",
    "claims",
    "reimbursement",
    "hospital",
    "hospitalization",
    "healthcare",
    "health care",
    "benefits",
    "eligibility",
    "enrollment",
    "enrolment",
    "maternity",
    "outpatient",
    "inpatient",
    "network",
    "pre-existing",
    "preexisting",
    "plan",
    "plans",
    "provider",
    "providers",
    "pharmacy",
    "prescription",
    "family coverage",
    "medical bills",
    "health plan",
    "health plans",
    "insurance company",
    "insurance cost",
    "insurance price",
    "insurance quote",
    "waiting period",
    "exclusions",
    "coverage limit",
    "coverage limits",
}

GREETING_PATTERNS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "thanks",
    "thank you",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def is_in_scope(message: str) -> bool:
    normalized = normalize_text(message)

    if normalized in GREETING_PATTERNS:
        return True

    return any(keyword in normalized for keyword in INSURANCE_KEYWORDS)


def get_out_of_scope_response() -> str:
    return (
        "I'm CoverCare AI, your health insurance assistant. "
        "I can help you understand health insurance plans, coverage, "
        "benefits, premiums, eligibility, and suitable insurance options. "
        "Please ask me something related to health insurance."
    )
