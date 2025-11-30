import argparse
import os
import shutil
import sys
from src.local_scanner import LocalScanner
from src.ai_scanner import AIScanner

def quarantine_file(filepath):
    """Moves the file to the quarantine directory."""
    quarantine_dir = "quarantine"
    os.makedirs(quarantine_dir, exist_ok=True)

    filename = os.path.basename(filepath)
    dest_path = os.path.join(quarantine_dir, filename + ".infected")

    try:
        shutil.move(filepath, dest_path)
        print(f"\n[!!!] FILE QUARANTINED: Moved to {dest_path}")
    except Exception as e:
        print(f"\n[ERROR] Failed to quarantine file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Source Code Antivirus & Safety Checker")
    parser.add_argument("filepath", help="Path to the source code file to scan")
    args = parser.parse_args()

    filepath = args.filepath

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    print(f"Scanning {filepath}...\n")

    # 1. Local Pattern Scan
    print("--- Phase 1: Local Pattern Scanning ---")
    local_scanner = LocalScanner()
    findings = local_scanner.scan_file(filepath)

    is_malicious = False

    if findings:
        print(f"[WARN] Suspicious patterns found ({len(findings)}):")
        for f in findings:
            print(f"  Line {f['line']}: {f['issue']} -> {f['content']}")
        is_malicious = True
    else:
        print("No suspicious patterns found locally.")

    # 2. AI Scan
    print("\n--- Phase 2: AI Deep Analysis ---")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        ai_scanner = AIScanner()
        ai_result = ai_scanner.scan_code(content)

        print(f"AI Verdict: {'SAFE' if ai_result['is_safe'] else 'MALICIOUS/UNSAFE'}")
        print(f"Reason: {ai_result['reason']}")

        if not ai_result['is_safe']:
            is_malicious = True

    except Exception as e:
        print(f"Error reading file for AI scan: {e}")
        # Fail-closed: If we can't scan it, we assume it's risky or at least warn the user.
        print("\n[WARN] Could not complete AI analysis due to error.")

    # 3. Final Action
    if is_malicious:
        print("\n[DANGER] The file detected as MALICIOUS or UNSAFE.")
        quarantine_file(filepath)
    else:
        print("\n[SAFE] The file appears safe to run (or no threats detected).")

if __name__ == "__main__":
    main()
