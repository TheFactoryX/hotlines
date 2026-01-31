"""
Hotlines - Operator 0

The night operator.
Connects calls that were never made.
Records conversations that never happened.

Every 15 minutes, a new call comes in.
From somewhere. To somewhere.
The operator writes it down.
"""

import anthropic
import random
import subprocess
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()

# The switchboard - calls from around the world
HOTLINES = [
    {"code": "1-800", "language": "English", "location": "New York"},
    {"code": "0800", "language": "中文", "location": "上海"},
    {"code": "0120", "language": "日本語", "location": "東京"},
    {"code": "080", "language": "한국어", "location": "서울"},
    {"code": "0800", "language": "Deutsch", "location": "Berlin"},
    {"code": "0800", "language": "Français", "location": "Paris"},
    {"code": "800", "language": "Español", "location": "Madrid"},
    {"code": "800", "language": "Português", "location": "São Paulo"},
    {"code": "800", "language": "Italiano", "location": "Roma"},
    {"code": "8800", "language": "Русский", "location": "Москва"},
    {"code": "1800", "language": "हिन्दी", "location": "मुंबई"},
    {"code": "1800", "language": "العربية", "location": "دبي"},
    {"code": "1800", "language": "ไทย", "location": "กรุงเทพ"},
    {"code": "1800", "language": "Tiếng Việt", "location": "Hà Nội"},
    {"code": "0800", "language": "Nederlands", "location": "Amsterdam"},
    {"code": "800", "language": "Türkçe", "location": "İstanbul"},
]

# Types of hotlines - what people call about
HOTLINE_TYPES = [
    "Existential Crisis Hotline",
    "Lost Object Recovery Line",
    "Dream Interpretation Service",
    "Time Travel Complaints",
    "Parallel Universe Support",
    "Memory Retrieval Assistance",
    "Forgiveness Request Line",
    "Future Self Consultation",
    "Stranger Advice Bureau",
    "Confession Hotline",
    "Apology Acceptance Center",
    "Last Words Registry",
    "Unfinished Business Department",
    "Coincidence Reporting Line",
    "Déjà Vu Documentation",
    "Silent Listener Service",
]


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


def record_call():
    """The operator takes a call."""

    # Random incoming call
    hotline_info = random.choice(HOTLINES)
    hotline_type = random.choice(HOTLINE_TYPES)

    call_number = get_next_call_number()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # The operator's prompt
    prompt = f"""You are recording a call to a fictional hotline.

HOTLINE: {hotline_type}
LANGUAGE: {hotline_info['language']}
LOCATION: {hotline_info['location']}
TOLL-FREE: {hotline_info['code']}-XXX-XXXX

Write a complete call transcript in {hotline_info['language']}.

The call should be:
- Surreal but emotionally genuine
- 2-4 minutes of conversation
- Between a caller and an operator
- Written entirely in {hotline_info['language']}
- Poetic, strange, touching

Format:
- Use [OPERATOR] and [CALLER] labels
- Include pauses like [...] or [silence]
- End with a proper goodbye

Do not translate. Do not explain. Just record the call."""

    # Make the call
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    transcript = response.content[0].text

    # Format the call log
    call_log = f"""# Call #{call_number:04d}

**Hotline:** {hotline_type}
**Language:** {hotline_info['language']}
**Location:** {hotline_info['location']}
**Toll-Free:** {hotline_info['code']}-XXX-XXXX
**Recorded:** {timestamp}

---

{transcript}

---

*Call ended. Operator on standby.*
"""

    # Save to call logs
    call_logs_dir = Path(__file__).parent / "call-logs"
    filename = f"call_{call_number:04d}.md"
    filepath = call_logs_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(call_log)

    print(f"Call #{call_number:04d} recorded")
    print(f"Hotline: {hotline_type}")
    print(f"Language: {hotline_info['language']}")
    print(f"Location: {hotline_info['location']}")
    print(f"Saved: {filepath}")

    return filepath


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
    print("Operator 0 - Connecting...")
    print("-" * 40)

    filepath = record_call()
    commit_call(filepath)

    print("-" * 40)
    print("Operator 0 - Standing by.")
