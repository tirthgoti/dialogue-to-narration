# Dialogue-to-Narration Converter

A rule-based NLP project that converts script-style dialogue into natural-sounding narration (indirect/reported speech).

## Example

**Input** (`input/dialogue.txt`):
```
John: "Where are you going?"
Mary: "I am going to the market."
John: "Will you come back soon?"
Mary: "Yes, I will be back in an hour."
```

**Output** (`output/narration.txt`):
```
John and Mary had the following conversation. John asked where she was going. Mary said she was going to the market. John asked if she would come back soon. Mary agreed she would be back in an hour.
```

## Features

- Parses dialogue in `Name: "text"` format
- Detects sentence type: statement, wh-question, yes/no question, command, exclamation
- Pronoun shifting (I → he/she, you → he/she/him/her)
- Case-aware pronoun mapping (nominative vs accusative)
- Tense backshift (present → past, past → past perfect)
- Modal backshift (will → would, can → could, may → might)
- Time and place word shifting (now → then, here → there, tomorrow → the next day)
- Question un-inversion (e.g., "Where are you going?" → "where she was going")
- Reporting verb selection based on sentence type and yes/no lead
- Command handling ("Close the door." → "told him to close the door")
- Multi-turn paragraph assembly

## Project Structure

```
dialogue2narration/
├── input/
│   └── dialogue.txt          # input dialogue
├── output/
│   └── narration.txt         # generated narration
├── speakers.json             # speaker gender mapping
├── parser.py                 # extracts (speaker, text, punctuation, lead)
├── analyzer.py               # spaCy-based linguistic analysis
├── converter.py              # core conversion rules
├── narrator.py               # paragraph assembly
├── main.py                   # pipeline driver
└── README.md
```

## Setup

### Requirements
- Python 3.8+
- spaCy

### Install

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

## Usage

1. Add your dialogue to `input/dialogue.txt` using the format:
   ```
   SpeakerName: "Their line of dialogue."
   ```

2. Add each speaker's gender to `speakers.json`:
   ```json
   {
     "John": "he",
     "Mary": "she"
   }
   ```

3. Run:
   ```bash
   python main.py
   ```

4. View `output/narration.txt` for the narration.

## Modules

| Module | Responsibility |
|---|---|
| `parser.py` | Reads dialogue file, extracts speakers and utterances via regex |
| `analyzer.py` | Runs spaCy on each utterance; identifies sentence type, verb phrase, pronouns, time words |
| `converter.py` | Applies pronoun shift, tense backshift, question restructuring, and reporting verb rules |
| `narrator.py` | Joins converted sentences into a single paragraph with optional framing sentence |
| `main.py` | Wires all modules together and writes output |

## Sample Test Cases

| Input | Output |
|---|---|
| `Anna: "I went to Paris yesterday."` | `Anna said she had gone to Paris the previous day.` |
| `Ben: "Did you like it?"` | `Ben asked if she liked it.` |
| `Boss: "Close the door."` | `Boss told him to close the door.` |
| `Sam: "I will call you tomorrow."` | `Sam said he would call her the next day.` |

## Limitations

- Irregular verb tables are finite; unknown irregular verbs may backshift incorrectly.
- Only handles two-speaker address resolution cleanly ("you" = other speaker).
- Does not perform full coreference resolution.
- Past perfect output can sound formal in informal contexts.
- No support for multi-clause complex sentences.

## Future Work

- Replace rule-based conversion with a fine-tuned transformer model (T5/BART).
- Add coreference resolution for multi-speaker dialogues.
- Extend verb tables and handle passive voice.
- Support additional languages.

## License

For academic use.