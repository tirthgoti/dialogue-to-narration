# parser.py
import re

def parse_dialogue(filepath):
    """
    Reads a dialogue file formatted as:  Name: "text"
    Returns a list of dicts: [{'speaker': 'John', 'text': 'Where are you going?', 'punctuation': '?'}]
    """
    pattern = re.compile(r'^(\w+):\s*"(.*)"\s*$')
    turns = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # skip blank lines

            match = pattern.match(line)
            if not match:
                print(f"[Warning] Skipping malformed line {line_num}: {line}")
                continue

            speaker = match.group(1)
            text = match.group(2).strip()
            # Detect leading yes/no
            lead = None
            lower = text.lower()
            if lower.startswith("yes"):
                lead = "yes"
            elif lower.startswith("no"):
                lead = "no"

            # Detect ending punctuation
            if text.endswith('?'):
                punct = '?'
            elif text.endswith('!'):
                punct = '!'
            else:
                punct = '.'

            turns.append({
                'speaker': speaker,
                'text': text,
                'punctuation': punct,
                'lead': lead
            })

    return turns


if __name__ == "__main__":
    turns = parse_dialogue("input/dialogue.txt")
    for t in turns:
        print(t)