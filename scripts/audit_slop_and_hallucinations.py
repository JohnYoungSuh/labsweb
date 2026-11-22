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

def audit_file(filepath, check_urls=True):
    errors = []
    with open(filepath, "rb") as f:
        raw_bytes = f.read()

    # 1. CRLF Check
    if b"\r" in raw_bytes:
        errors.append("CRLF carriage return detected. Must use Unix LF line endings.")

    text = raw_bytes.decode("utf-8", errors="replace")

    # 2. Em-dash Check
    if "—" in text:
        errors.append("Em-dash ('—') detected. Use standard ASCII hyphens or parentheses.")
    if "&mdash;" in text:
        errors.append("HTML entity '&mdash;' detected. Use standard ASCII hyphens or parentheses.")

    # 3. AI Slop Keywords
    for pattern in SLOP_KEYWORDS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            errors.append(f"AI Slop keyword matched: '{matches[0].group()}' (found {len(matches)} time(s)).")

    # 4. Claims Boundaries & Overreach
    for pattern, reason in OVERCLAIM_PATTERNS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            errors.append(f"Claims overreach matched: '{matches[0].group()}' - {reason}")

    # 5. URL Integrity & Hallucination Check
    if check_urls:
        urls = sorted(set(re.findall(r"https?://[^\s\)\>\]\"\'\`]+", text)))
        for url in urls:
            # Clean trailing punctuation and bracket artifacts from markdown/BibTeX/HTML
            clean_url = url.rstrip(".,;:{}><\"')")
            # Skip localhost or example URLs
            if "localhost" in clean_url or "example.com" in clean_url:
                continue
            req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            try:
                resp = urllib.request.urlopen(req, timeout=7)
                if resp.status >= 400:
                    errors.append(f"Broken link / Hallucinated URL ({resp.status}): {clean_url}")
            except urllib.error.HTTPError as e:
                # Splunk community blog protects itself with anti-bot 403; test with curl or ignore if 403 on community.splunk.com
                if e.code == 403 and "community.splunk.com" in clean_url:
                    continue
                errors.append(f"Broken link / Hallucinated URL ({e.code}): {clean_url}")
            except Exception as e:
                errors.append(f"Failed URL check ({e}): {clean_url}")

    return errors

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    target_files = sorted(glob.glob("docs/*.md") + glob.glob("*.html"))
    total_errors = 0

    print("=" * 70)
    print("SuhLabs Automated AI Slop & Hallucination Gatekeeper")
    print(f"Auditing {len(target_files)} publication and whitepaper files...")
    print("=" * 70)

    for fpath in target_files:
        errors = audit_file(fpath, check_urls=True)
        if errors:
            print(f"\n[FAIL] {fpath}:")
            for err in errors:
                print(f"  - {err}")
            total_errors += len(errors)
        else:
            print(f"[PASS] {fpath}")

    print("\n" + "=" * 70)
    if total_errors > 0:
        print(f"FAILED: Found {total_errors} errors across audited files.")
        sys.exit(1)
    else:
        print("SUCCESS: 0 AI slop keywords, 0 hallucinated URLs, 0 em-dashes, 0 CRLF!")
        print("All publications adhere to SuhLabs institutional claims boundaries.")
        sys.exit(0)

if __name__ == "__main__":
    main()
