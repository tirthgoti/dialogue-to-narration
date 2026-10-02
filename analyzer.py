# analyzer.py
import spacy

nlp = spacy.load("en_core_web_sm")

# Words that shift when converting to reported speech
TIME_WORDS = {
    "now": "then",
    "today": "that day",
    "tomorrow": "the next day",
    "yesterday": "the previous day",
    "tonight": "that night",
    "here": "there",
    "this": "that",
    "these": "those",
    "ago": "before",
}

MODAL_MAP = {
    "will": "would",
    "shall": "should",
    "can": "could",
    "may": "might",
    "must": "must",   # stays
    "would": "would",
    "should": "should",
    "could": "could",
    "might": "might",
}

# Pronouns that need shifting (1st/2nd person → 3rd person)
SHIFTABLE_PRONOUNS = {"i", "me", "my", "mine", "myself",
                      "we", "us", "our", "ours", "ourselves",
                      "you", "your", "yours", "yourself", "yourselves"}


def detect_sentence_type(text, punctuation):
    """Classify the sentence based on its last punctuation and structure."""
    lower = text.lower().strip()

    if punctuation == '?':
        # Wh-question or yes/no question
        wh_words = ("what", "where", "when", "why", "who", "whom", "whose", "how", "which")
        if lower.startswith(wh_words):
            return "wh_question"
        return "yesno_question"

    if punctuation == '!':
        return "exclamation"

    # Command check: starts with a base verb and has no explicit subject
    doc = nlp(text)
    first_token = next((t for t in doc if not t.is_space), None)
    if first_token and first_token.tag_ == "VB" and first_token.dep_ == "ROOT":
        return "command"

    return "statement"


def extract_main_verb(doc):
    root = None
    auxes = []

    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
            root = token
        if token.dep_ in ("aux", "auxpass"):
            auxes.append(token)

    if root is None:
        return None

    def get_morph(token, feature):
        vals = token.morph.get(feature)
        return vals[0] if vals else None

    # Detect modal auxiliary (spaCy tags these as AUX with tag MD)
    modal = None
    for a in auxes:
        if a.tag_ == "MD":
            modal = a.text.lower()
            break

    tense = get_morph(root, "Tense") or (get_morph(auxes[0], "Tense") if auxes else None)
    aspect = get_morph(root, "Aspect")
    verbform = get_morph(root, "VerbForm")

    return {
        "root_token": root.text,
        "root_lemma": root.lemma_,
        "root_index": root.i,
        "aux_tokens": [a.text for a in auxes],
        "aux_indices": [a.i for a in auxes],
        "modal": modal,
        "tense": tense,
        "aspect": aspect,
        "verbform": verbform,
    }

def extract_pronouns(doc):
    """Return list of pronouns that need shifting."""
    pronouns = []
    for token in doc:
        if token.pos_ == "PRON" and token.text.lower() in SHIFTABLE_PRONOUNS:
            pronouns.append({
                "text": token.text,
                "lower": token.text.lower(),
                "person": token.morph.get("Person", [None])[0] if token.morph.get("Person") else None,
                "case": token.morph.get("Case", [None])[0] if token.morph.get("Case") else None,
                "index": token.i,
            })
    return pronouns


def extract_time_words(doc):
    """Return time/place words that need shifting."""
    found = []
    for token in doc:
        if token.text.lower() in TIME_WORDS:
            found.append({
                "text": token.text,
                "lower": token.text.lower(),
                "replacement": TIME_WORDS[token.text.lower()],
                "index": token.i,
            })
    return found


def analyze_turn(turn):
    """Enrich a single turn dict with linguistic info."""
    text = turn["text"]
    doc = nlp(text)

    turn["sentence_type"] = detect_sentence_type(text, turn["punctuation"])
    turn["main_verb"] = extract_main_verb(doc)
    turn["pronouns"] = extract_pronouns(doc)
    turn["time_words"] = extract_time_words(doc)
    turn["doc"] = doc  # keep for converter (we'll remove before saving)

    return turn


def analyze_dialogue(turns):
    return [analyze_turn(t) for t in turns]


if __name__ == "__main__":
    from parser import parse_dialogue
    import json

    turns = parse_dialogue("input/dialogue.txt")
    analyzed = analyze_dialogue(turns)

    for t in analyzed:
        # We can't print the spaCy doc nicely, so strip it
        printable = {k: v for k, v in t.items() if k != "doc"}
        print(json.dumps(printable, indent=2))