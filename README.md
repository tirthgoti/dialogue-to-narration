# Dialogue-to-Narration Converter

A comparative NLP project that converts script-style dialogue into natural narration (reported speech), implemented in **two approaches** — a rule-based system and a pre-trained transformer model — with quantitative evaluation.

## Example

**Input** (`input/dialogue.txt`):
```
John: "Where are you going?"
Mary: "I am going to the market."
John: "Will you come back soon?"
Mary: "Yes, I will be back in an hour."
```

**Rule-based output:**
```
John and Mary had the following conversation. John asked where she was going. Mary said she was going to the market. John asked if she would come back soon. Mary agreed she would be back in an hour.
```

**Model-based output (DistilBART):**
```
Mary: I am going to the market. John: Will you come back soon? Mary: Yes, I will be back in an hour. John: Where are you going?
```

## Two Approaches Compared

This project implements **two approaches** to dialogue-to-narration conversion and compares them.

### 1. Rule-Based Approach (Primary)
Uses spaCy for linguistic analysis and applies explicit reported-speech rules.
Produces grammatically correct narration with proper tense backshift and pronoun shift.

### 2. Model-Based Approach (Baseline)
Uses the pre-trained `sshleifer/distilbart-cnn-6-6` summarization model.
Treats the dialogue as text to summarize.

### Comparison

| Metric | Rule-Based | Model-Based |
|---|---|---|
| BLEU Score | **0.363** | 0.086 |
| Tense backshift | ✅ Correct | ❌ Not applied |
| Pronoun shift | ✅ Correct | ❌ Not applied |
| Reporting verbs | ✅ Chosen contextually | ❌ None |
| Output format | Narration | Reordered dialogue |

**Conclusion:** For structured transformation tasks like reported-speech conversion, rule-based methods outperform general-purpose summarization models, which lack the specific linguistic knowledge required.

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
- BLEU-based evaluation comparing rule-based and model-based outputs

## Project Structure

```
dialogue2narration/
├── input/
│   └── dialogue.txt              # input dialogue
├── output/
│   ├── narration.txt             # rule-based narration (from main.py)
│   ├── rule_based_narration.txt  # rule-based output (from compare.py)
│   └── model_narration.txt       # model-based output (from compare.py)
├── speakers.json                 # speaker gender mapping
├── parser.py                     # extracts (speaker, text, punctuation, lead)
├── analyzer.py                   # spaCy-based linguistic analysis
├── converter.py                  # core conversion rules
├── narrator.py                   # paragraph assembly
├── main.py                       # rule-based pipeline driver
├── model_narrator.py             # model-based narration (DistilBART)
├── compare.py                    # runs both approaches, prints side-by-side
├── evaluate.py                   # BLEU score comparison
├── requirements.txt
└── README.md
```

## Setup

### Requirements
- Python 3.8+
- spaCy (with `en_core_web_sm` model)
- transformers
- torch (CPU version is sufficient)
- nltk

### Install

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

> **Note:** The first run of `model_narrator.py`, `compare.py`, or `evaluate.py` will download the DistilBART model (~300 MB) from HuggingFace. This is a one-time download.

## Usage

### 1. Prepare input

Add your dialogue to `input/dialogue.txt` in this format:
```
SpeakerName: "Their line of dialogue."
```

Add each speaker's gender to `speakers.json`:
```json
{
  "John": "he",
  "Mary": "she"
}
```

### 2. Run the rule-based pipeline

```bash
python main.py
```

Output is saved to `output/narration.txt`.

### 3. Run the comparison

```bash
python compare.py
```

Prints rule-based and model-based outputs side by side and saves both:
- `output/rule_based_narration.txt`
- `output/model_narration.txt`

### 4. Evaluate with BLEU

```bash
python evaluate.py
```

Prints BLEU scores for both approaches against a reference narration.

## Modules

| Module | Responsibility |
|---|---|
| `parser.py` | Reads dialogue file, extracts speakers and utterances via regex |
| `analyzer.py` | Runs spaCy on each utterance; identifies sentence type, verb phrase, pronouns, time words |
| `converter.py` | Applies pronoun shift, tense backshift, question restructuring, and reporting verb rules |
| `narrator.py` | Joins converted sentences into a single paragraph with optional framing sentence |
| `main.py` | Wires the rule-based pipeline together and writes output |
| `model_narrator.py` | Loads DistilBART and generates narration via the pre-trained model |
| `compare.py` | Runs both approaches on the same input and prints results side by side |
| `evaluate.py` | Computes BLEU scores for both approaches |

## Sample Test Cases

| Input | Rule-Based Output |
|---|---|
| `Anna: "I went to Paris yesterday."` | `Anna said she had gone to Paris the previous day.` |
| `Ben: "Did you like it?"` | `Ben asked if she liked it.` |
| `Boss: "Close the door."` | `Boss told him to close the door.` |
| `Sam: "I will call you tomorrow."` | `Sam said he would call her the next day.` |

## Evaluation Results

Tested on a 4-turn dialogue (John & Mary):

| Approach | BLEU Score |
|---|---|
| Rule-Based | **0.363** |
| Model-Based (DistilBART) | 0.086 |

The rule-based system achieved a 4.2× higher BLEU score, confirming that explicit linguistic rules are better suited to structured transformation tasks than general-purpose summarization models.

## Limitations

- Irregular verb tables are finite; unknown irregular verbs may backshift incorrectly.
- Only handles two-speaker address resolution cleanly ("you" = other speaker).
- Does not perform full coreference resolution.
- Past perfect output can sound formal in informal contexts.
- No support for multi-clause complex sentences.
- The model-based approach is zero-shot (not fine-tuned); fine-tuning on paired data would likely improve results.

## Future Work

- Fine-tune a transformer (T5, BART) on a manually-created dialogue/narration dataset.
- Add coreference resolution for multi-speaker dialogues.
- Extend the irregular verb lexicon using `mlconjug3`.
- Support passive voice and conditionals.
- Expand to multilingual dialogue conversion.

## Requirements

```
spacy>=3.7.0
en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
transformers>=4.30
torch>=2.0
nltk>=3.8
```

## License

For academic use.