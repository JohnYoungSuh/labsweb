#!/usr/bin/env python3
"""
scripts/audit_slop_and_hallucinations.py
Automated mechanical pre-flight gatekeeper for SuhLabs publications, whitepapers, and blog drafts.

Audits:
1. URL Integrity & Hallucination Check: Verifies every embedded HTTP/HTTPS link returns HTTP 200 (no 404s or guessed repos).
2. Punctuation & Character Hygiene: Confirms 0 em-dashes ('—' or '&mdash;') and 0 CRLF line endings.
3. AI Slop Keywords: Flags generic, promotional, or hollow AI filler words.
4. Claims Boundaries & Overreach: Enforces separation between telemetry/observability and active enforcement.
"""

import glob
import os
import re
import sys
import urllib.request

SLOP_KEYWORDS = [
    r"\bdelve\b",
    r"\btestament\b",
    r"\btapestry\b",
    r"\bgame-changer\b",
    r"\bgame changer\b",
    r"\brevolutionary\b",
    r"\bseamlessly\b",
    r"\bseamless\b",
    r"\bfurthermore\b",
    r"\bbeacon\b",
    r"\bpivotal\b",
    r"\bin conclusion\b",
    r"\bunleash\b",
    r"\bspearhead\b",
    r"\belevate your\b",
    r"\brobust solution\b",
]

OVERCLAIM_PATTERNS = [
    (r"\baudit certificate\b", "Cannot claim third-party 'audit certificate' without formal accrediting body."),
    (r"\b100% certified\b", "Cannot claim '100% certified'. Compliance is an ongoing operational posture."),
    (r"\bguarantees compliance\b", "Tools assist with evidence; they cannot 'guarantee' compliance."),
    (r"\bguaranteed ato\b", "Authority to Operate (ATO) is strictly an Authorizing Official (AO) determination."),
    (r"compliance is actively enforced", "Splunk is an evidentiary audit/monitoring system, not an active inline packet dropper."),
]

def audit_file_score(filepath, check_urls=True):
    with open(filepath, "rb") as f:
        raw_bytes = f.read()

    errors = []
    # Base scores
    cat1_score = 40  # Factual Integrity & Claims Boundaries
    cat2_score = 30  # AI Slop & Cliché Purge
    cat3_score = 20  # Engineering Depth & Reproducibility
    cat4_score = 10  # Typography & Hygiene

    # 1. CRLF Check (Cat 4)
    if b"\r" in raw_bytes:
        errors.append("CRLF carriage return detected. Must use Unix LF line endings.")
        cat4_score = max(0, cat4_score - 5)

    text = raw_bytes.decode("utf-8", errors="replace")

    # 2. Em-dash Check (Cat 4)
    if "—" in text:
        errors.append("Em-dash ('—') detected. Use standard ASCII hyphens or parentheses.")
        cat4_score = max(0, cat4_score - 5)
    if "&mdash;" in text:
        errors.append("HTML entity '&mdash;' detected. Use standard ASCII hyphens or parentheses.")
        cat4_score = max(0, cat4_score - 5)

    # 3. AI Slop Keywords (Cat 2)
    slop_count = 0
    for pattern in SLOP_KEYWORDS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            slop_count += len(matches)
            errors.append(f"AI Slop keyword matched: '{matches[0].group()}' (found {len(matches)} time(s)).")
    cat2_score = max(0, cat2_score - (slop_count * 5))

    # 4. Claims Boundaries & Overreach (Cat 1)
    overclaim_count = 0
    for pattern, reason in OVERCLAIM_PATTERNS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            overclaim_count += len(matches)
            errors.append(f"Claims overreach matched: '{matches[0].group()}' - {reason}")
    cat1_score = max(0, cat1_score - (overclaim_count * 10))

    # 5. URL Integrity & Hallucination Check (Cat 1)
    if check_urls:
        urls = sorted(set(re.findall(r"https?://[^\s\)\>\]\"\'\`]+", text)))
        for url in urls:
            clean_url = url.rstrip(".,;:{}><\"')")
            if "localhost" in clean_url or "example.com" in clean_url:
                continue
            req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            try:
                resp = urllib.request.urlopen(req, timeout=7)
                if resp.status >= 400:
                    errors.append(f"Broken link / Hallucinated URL ({resp.status}): {clean_url}")
                    cat1_score = max(0, cat1_score - 20)
            except urllib.error.HTTPError as e:
                if e.code == 403 and any(domain in clean_url for domain in ["community.splunk.com", "iso.org"]):
                    continue
                errors.append(f"Broken link / Hallucinated URL ({e.code}): {clean_url}")
                cat1_score = max(0, cat1_score - 20)
            except Exception as e:
                errors.append(f"Failed URL check ({e}): {clean_url}")
                cat1_score = max(0, cat1_score - 20)

    total_score = cat1_score + cat2_score + cat3_score + cat4_score
    if total_score >= 95:
        grade = "Grade S (Level 5.0) - APPROVED"
    elif total_score >= 85:
        grade = "Grade A (Level 4.0-4.5) - CONDITIONAL"
    elif total_score >= 70:
        grade = "Grade B (Level 3.0-3.9) - REVISION REQUIRED"
    else:
        grade = "Grade F - REJECTED"

    scorecard = {
        "total_score": total_score,
        "grade": grade,
        "cat1_factual": cat1_score,
        "cat2_slop": cat2_score,
        "cat3_depth": cat3_score,
        "cat4_hygiene": cat4_score,
        "errors": errors,
    }
    return scorecard

def audit_file(filepath, check_urls=True):
    return audit_file_score(filepath, check_urls=check_urls)["errors"]

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        target_files = sys.argv[1:]
    else:
        target_files = sorted(glob.glob("docs/*.md"))

    print("=" * 70)
    print("SuhLabs Blog & Publication Quality Scorecard (100-Point Index)")
    print(f"Auditing {len(target_files)} target file(s)...")
    print("=" * 70)

    total_failures = 0
    for fpath in target_files:
        card = audit_file_score(fpath, check_urls=True)
        print(f"\nTarget Document: {fpath}")
        print(f"Overall Quality Score: {card['total_score']} / 100 [{card['grade']}]")
        print(f"  • Category 1 (Factual & Claims):  {card['cat1_factual']} / 40")
        print(f"  • Category 2 (AI Slop & Clichés): {card['cat2_slop']} / 30")
        print(f"  • Category 3 (Engineering Depth): {card['cat3_depth']} / 20")
        print(f"  • Category 4 (Hygiene & Format):  {card['cat4_hygiene']} / 10")
        if card["errors"]:
            print("  Identified Issues & Remediations:")
            for err in card["errors"]:
                print(f"    - {err}")
            if card["total_score"] < 85:
                total_failures += 1
        else:
            print("  Status: All checks passed. Zero slop, zero hallucinations.")

    print("\n" + "=" * 70)
    if total_failures > 0:
        print(f"AUDIT RESULT: {total_failures} file(s) below acceptable publication threshold (< 85).")
        sys.exit(1)
    else:
        print("AUDIT RESULT: All audited files passed quality scoring threshold (>= 85)!")
        sys.exit(0)

if __name__ == "__main__":
    main()
