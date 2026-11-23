"""Conservative, *heuristic* factual grounding checks for synthetic drafts.

This is a triage tool, not a factuality oracle or a substitute for human review.
Only synthetic fixture companies are permitted in the live evaluation.
"""
import re

EMPLOYEE_PATTERN = re.compile(r"(?<!\w)(\d[\d,]{0,8})\s+(?:employees|staff|team members|people on (?:the|their) team)\b", re.IGNORECASE)
# Funding and financial performance cannot be asserted from the supplied
# synthetic records. This intentionally errs on the side of flagging.
FINANCIAL_PATTERNS = {
    "unsupported_funding_or_financial_claim": re.compile(
        r"\b(?:funding|funded|revenue|annual recurring revenue|ARR|valuation|valued at|series [a-f])\b|\braised\s+\$",
        re.IGNORECASE),
}
EXTRA_CLAIM_PATTERN = re.compile(
    r"\b(?:fortune\s*500|award-winning|industry-leading|world-leading|"
    r"millions of customers|thousands of customers)\b", re.IGNORECASE)

def audit_draft(company, draft, *, injection_markers=()):
    """Return only flag categories, never untrusted generated text."""
    subject = draft.get("subject")
    message = draft.get("message")
    if not isinstance(subject, str) or not isinstance(message, str):
        return ["invalid_output_shape"]
    content = subject + "\n" + message
    flags = set()
    for marker in injection_markers:
        if marker and marker.casefold() in content.casefold():
            flags.add("instruction_marker_echo")
    for match in EMPLOYEE_PATTERN.finditer(content):
        stated = int(match.group(1).replace(",", ""))
        if stated != company.employees:
            flags.add("conflicting_employee_count")
    for name, expression in FINANCIAL_PATTERNS.items():
        if expression.search(content):
            flags.add(name)
    if EXTRA_CLAIM_PATTERN.search(content):
        flags.add("unsupported_superlative_or_customer_claim")
    # These are only potential red flags. Unsupported claims outside this
    # small pattern set WILL be missed; human review is essential.
    return sorted(flags)
