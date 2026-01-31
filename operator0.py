"""
Hotlines - Operator 0

The night operator.
Answers every call.
Records every conversation.

When someone calls (creates an issue),
the operator picks up,
responds,
and files the record.
"""

import anthropic
import re
import subprocess
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()


def get_next_call_number():
    """Find the next call log number."""
    call_logs_dir = Path(__file__).parent / "call-logs"
    call_logs_dir.mkdir(exist_ok=True)

    existing = list(call_logs_dir.glob("call_*.md"))
    if not existing:
        return 1

    numbers = []
    for f in existing:
        try:
            num = int(f.stem.split("_")[1])
            numbers.append(num)
        except (IndexError, ValueError):
            continue

    return max(numbers, default=0) + 1


def detect_language(text):
    """Detect the primary language of the text."""
    # Simple heuristic based on character ranges
    if re.search(r'[\u4e00-\u9fff]', text):
        return "中文"
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return "日本語"
    if re.search(r'[\uac00-\ud7af]', text):
        return "한국어"
    if re.search(r'[\u0600-\u06ff]', text):
        return "العربية"
    if re.search(r'[\u0400-\u04ff]', text):
        return "Русский"
    if re.search(r'[\u0e00-\u0e7f]', text):
        return "ไทย"
    if re.search(r'[àâäéèêëïîôùûüÿçœæ]', text, re.IGNORECASE):
        return "Français"
    if re.search(r'[áéíóúüñ¿¡]', text, re.IGNORECASE):
        return "Español"
    if re.search(r'[ãõáéíóúâêôç]', text, re.IGNORECASE):
        return "Português"
    if re.search(r'[äöüß]', text, re.IGNORECASE):
        return "Deutsch"
    if re.search(r'[àèéìòù]', text, re.IGNORECASE):
        return "Italiano"
    return "English"


def answer_call(issue_number, issue_title, issue_body):
    """The operator answers the call."""

    # Detect language from the issue
    full_text = f"{issue_title}\n{issue_body}"
    language = detect_language(full_text)

    call_number = get_next_call_number()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # The operator's prompt
    prompt = f"""You are a night operator at a surreal hotline service.

A caller has reached you with the following message:

---
TITLE: {issue_title}

{issue_body}
---

DETECTED LANGUAGE: {language}

You must respond as the operator:
1. Write ENTIRELY in {language} - the same language as the caller
2. Be warm, strange, and poetic
3. Take their concern seriously, even if surreal
4. Offer comfort or guidance in your unique way
5. Keep response between 150-300 words
6. End with a gentle closing

Do not translate. Do not explain. Just respond as the operator would.
Begin with "[OPERATOR]:" """

    # Answer the call
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    operator_response = response.content[0].text

    # Format the call log
    call_log = f"""# Call #{call_number:04d}

**Issue:** #{issue_number}
**Language:** {language}
**Recorded:** {timestamp}

---

## Incoming Call

**{issue_title}**

{issue_body}

---

## Operator Response

{operator_response}

---

*Call ended. Issue closed.*
"""

    # Save to call logs
    call_logs_dir = Path(__file__).parent / "call-logs"
    filename = f"call_{call_number:04d}.md"
    filepath = call_logs_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(call_log)

    print(f"Call #{call_number:04d} recorded")
    print(f"Issue: #{issue_number}")
    print(f"Language: {language}")
    print(f"Saved: {filepath}")

    return operator_response, filepath


def commit_call(filepath):
    """The operator files the record."""
    try:
        subprocess.run(["git", "add", str(filepath)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"📞 Call recorded: {filepath.name}"],
            check=True
        )
        print("Call log filed.")
    except subprocess.CalledProcessError:
        print("Filing skipped.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python operator0.py <issue_number> <issue_title> <issue_body>")
        sys.exit(1)

    issue_number = sys.argv[1]
    issue_title = sys.argv[2]
    issue_body = sys.argv[3]

    print("Operator 0 - Answering...")
    print("-" * 40)

    response, filepath = answer_call(issue_number, issue_title, issue_body)
    commit_call(filepath)

    # Output response for GitHub Actions to use
    print("-" * 40)
    print("OPERATOR_RESPONSE_START")
    print(response)
    print("OPERATOR_RESPONSE_END")
    print("-" * 40)
    print("Operator 0 - Standing by.")
