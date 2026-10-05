# converter.py
import json
import spacy

nlp = spacy.load("en_core_web_sm")



SPEAKER_MAP_MALE = {
    "i": "he", "me": "him", "my": "his", "mine": "his", "myself": "himself",
    "we": "they", "us": "them", "our": "their", "ours": "theirs", "ourselves": "themselves",
}
SPEAKER_MAP_FEMALE = {
    "i": "she", "me": "her", "my": "her", "mine": "hers", "myself": "herself",
    "we": "they", "us": "them", "our": "their", "ours": "theirs", "ourselves": "themselves",
}

# Maps for the ADDRESSEE (applies to you/your/yours...)
ADDRESSEE_MAP_MALE = {
    "you": "he",
    "you_obj": "him",
    "your": "his", "yours": "his", "yourself": "himself", "yourselves": "themselves",
}
ADDRESSEE_MAP_FEMALE = {
    "you": "she",
    "you_obj": "her",
    "your": "her", "yours": "hers", "yourself": "herself", "yourselves": "themselves",
}

TIME_WORDS = {
    "now": "then", "today": "that day", "tomorrow": "the next day",
    "yesterday": "the previous day", "tonight": "that night",
    "here": "there", "this": "that", "these": "those", "ago": "before",
}

MODAL_BACKSHIFT = {
    "will": "would", "shall": "should", "can": "could", "may": "might",
    "would": "would", "should": "should", "could": "could", "might": "might",
    "must": "must",
}

IRREGULAR_PAST = {
    "be": "was", "go": "went", "come": "came", "have": "had",
    "do": "did", "say": "said", "get": "got", "make": "made",
    "know": "knew", "think": "thought", "see": "saw", "take": "took",
}

REPORTING_VERBS = {
    "statement": "said",
    "statement_yes": "agreed",
    "statement_no": "denied",
    "wh_question": "asked",
    "yesno_question": "asked",
    "command": "told",
    "exclamation": "exclaimed",
}

IRREGULAR_PAST_PARTICIPLE = {
    "be": "been", "go": "gone", "come": "come", "have": "had",
    "do": "done", "say": "said", "get": "gotten", "make": "made",
    "know": "known", "think": "thought", "see": "seen", "take": "taken",
    "eat": "eaten", "write": "written", "give": "given", "find": "found",
    "leave": "left", "feel": "felt", "run": "run", "read": "read",
    "like": "liked", "love": "loved",
}


def past_participle(lemma):
    if lemma in IRREGULAR_PAST_PARTICIPLE:
        return IRREGULAR_PAST_PARTICIPLE[lemma]
    if lemma.endswith("e"):
        return lemma + "d"
    return lemma + "ed"

# ---------------- Helpers ----------------

def load_speakers(path="speakers.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def past_simple(lemma):
    if lemma in IRREGULAR_PAST:
        return IRREGULAR_PAST[lemma]
    if lemma.endswith("e"):
        return lemma + "d"
    return lemma + "ed"


def shift_token(token_text, combined_map, case=None):
    lower = token_text.lower()
    if lower == "you" and case == "Acc" and "you_obj" in combined_map:
        return combined_map["you_obj"]
    if lower in combined_map:
        return combined_map[lower]
    if lower in TIME_WORDS:
        return TIME_WORDS[lower]
    return token_text


def get_verb_span_indices(main_verb):
    if main_verb is None:
        return set()
    return set(main_verb["aux_indices"] + [main_verb["root_index"]])


def backshift_verb_phrase(main_verb, plural_subject):
    if main_verb is None:
        return None

    modal = main_verb["modal"]
    tense = main_verb["tense"]
    aspect = main_verb["aspect"]
    lemma = main_verb["root_lemma"]
    aux_tokens = [a.lower() for a in main_verb["aux_tokens"]]

    # Case: "do/does/did" as auxiliary (emphasis or question)
    # Did you like it? → if she liked it
    if any(a in ("do", "does", "did") for a in aux_tokens):
        return past_simple(lemma)

    # Modal case: will go → would go
    if modal:
        return f"{MODAL_BACKSHIFT.get(modal, modal)} {lemma}"

    # Present continuous: is going → was going
    if tense == "Pres" and aspect == "Prog":
        be_past = "were" if plural_subject else "was"
        return f"{be_past} {main_verb['root_token']}"

    # Present simple: goes → went
    if tense == "Pres" and aspect is None:
        return past_simple(lemma)

    # Past simple: went → had gone
    if tense == "Past":
        return f"had {past_participle(lemma)}"

    return main_verb["root_token"]



def build_reported_clause(turn, speaker_map, addressee_map):
    """
    speaker_map   -> applied to I/we/... tokens
    addressee_map -> applied to you/your/... tokens
    """
    text = turn["text"]
    stype = turn["sentence_type"]
    main_verb = turn["main_verb"]

    doc = nlp(text)
    verb_span = get_verb_span_indices(main_verb)

    # Merge the two maps for token lookup
    combined_map = {**speaker_map, **addressee_map}

    # ---- Determine shifted subject for was/were agreement ----
    shifted_subj = None
    for p in turn["pronouns"]:
        if p["case"] == "Nom":
            if p["lower"] in speaker_map:
                shifted_subj = speaker_map[p["lower"]]
            elif p["lower"] in addressee_map:
                shifted_subj = addressee_map[p["lower"]]
            break
    plural_subject = shifted_subj in ("they", "we")

    new_verb = backshift_verb_phrase(main_verb, plural_subject)

    # ---- Identify subject pronoun index for inversion fix ----
    subj_idx = None
    if stype in ("wh_question", "yesno_question") and main_verb and main_verb["aux_indices"]:
        first_aux = min(main_verb["aux_indices"])
        root_idx = main_verb["root_index"]
        for p in turn["pronouns"]:
            if first_aux < p["index"] < root_idx:
                subj_idx = p["index"]
                break

    # ---- Build ordered list of content indices ----
    all_indices = [i for i, t in enumerate(doc) if not t.is_space and not t.is_punct]

    # Move inverted subject before the verb span (un-invert questions)
    if subj_idx is not None:
        verb_start = min(verb_span)
        if subj_idx in all_indices and verb_start in all_indices:
            all_indices.remove(subj_idx)
            insert_pos = all_indices.index(verb_start)
            all_indices.insert(insert_pos, subj_idx)

    # ---- Emit tokens ----
    tokens_out = []
    for i in all_indices:
        if i in verb_span:
            if i == min(verb_span):
                tokens_out.append(new_verb)
            continue
        tok = doc[i]
        case = None
        for p in turn["pronouns"]:
            if p["index"] == i:
                case = p["case"]
                break
        tokens_out.append(shift_token(tok.text, combined_map, case=case))

    # ---- Strip leading Yes/No ----
    if tokens_out and tokens_out[0].lower().rstrip(",") in ("yes", "no"):
        tokens_out = tokens_out[1:]
        if tokens_out and tokens_out[0] == ",":
            tokens_out = tokens_out[1:]

    clause = " ".join(tokens_out)

    # ---- Question restructuring ----
    if stype == "wh_question":
        clause = clause.rstrip("?.").strip()
        words = clause.split()
        if words and words[0].lower() in ("what", "where", "when", "why", "who", "how", "which"):
            words[0] = words[0].lower()
        return " ".join(words)

    if stype == "yesno_question":
        clause = clause.rstrip("?.").strip()
        return "if " + clause

    if stype == "command":
        clause = clause.rstrip(".!").strip()
        # Lowercase first letter of verb
        if clause and clause[0].isupper():
            clause = clause[0].lower() + clause[1:]
        return "to " + clause

    # statement / exclamation
    clause = clause.rstrip(".!").strip()
    if clause and clause[0].isupper() and not clause.startswith("I "):
        clause = clause[0].lower() + clause[1:]
    return clause


def choose_reporting_verb(turn):
    st = turn["sentence_type"]
    if st == "statement":
        if turn.get("lead") == "yes":
            return REPORTING_VERBS["statement_yes"]
        if turn.get("lead") == "no":
            return REPORTING_VERBS["statement_no"]
        return REPORTING_VERBS["statement"]
    return REPORTING_VERBS.get(st, "said")


def convert_turn(turn, speaker_map, addressee_map,
                 previous_speaker=None, current_speaker_gender="he",
                 addressee_pronoun="him"):
    reporting_verb = choose_reporting_verb(turn)
    clause = build_reported_clause(turn, speaker_map, addressee_map)

    if turn["speaker"] == previous_speaker:
        subject = current_speaker_gender.capitalize()
    else:
        subject = turn["speaker"]

    # Commands: insert addressee between verb and clause
    if turn["sentence_type"] == "command":
        return f"{subject} {reporting_verb} {addressee_pronoun} {clause}."

    return f"{subject} {reporting_verb} {clause}."


# ---------------- Main driver ----------------

def determine_addressee(current_speaker, speakers_dict):
    """
    If exactly 2 speakers, addressee = the other one.
    Returns gender string ("he"/"she") or None.
    """
    if len(speakers_dict) == 2:
        for name, gender in speakers_dict.items():
            if name != current_speaker:
                return gender
    return None


if __name__ == "__main__":
    from parser import parse_dialogue
    from analyzer import analyze_dialogue

    speakers = load_speakers()
    turns = analyze_dialogue(parse_dialogue("input/dialogue.txt"))

    prev = None
    for t in turns:
        speaker_gender = speakers.get(t["speaker"], "he")

        # Pick speaker's pronoun map (for I / we)
        sp_map = SPEAKER_MAP_FEMALE if speaker_gender == "she" else SPEAKER_MAP_MALE

        # Pick addressee's pronoun map (for you)
        addressee_gender = determine_addressee(t["speaker"], speakers)
        if addressee_gender == "she":
            ad_map = ADDRESSEE_MAP_FEMALE
        else:
            ad_map = ADDRESSEE_MAP_MALE  # default fallback

        out = convert_turn(
            t,
            speaker_map=sp_map,
            addressee_map=ad_map,
            previous_speaker=prev,
            current_speaker_gender=speaker_gender,
        )
        print(out)
        prev = t["speaker"]