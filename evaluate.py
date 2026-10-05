# evaluate.py
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from parser import parse_dialogue
from analyzer import analyze_dialogue
from converter import (
    load_speakers, SPEAKER_MAP_MALE, SPEAKER_MAP_FEMALE,
    ADDRESSEE_MAP_MALE, ADDRESSEE_MAP_FEMALE,
    convert_turn, determine_addressee,
)
from narrator import narrate
from model_narrator import model_narration


# Reference narrations (written by hand — what a human would produce)
TEST_CASES = [
    {
        "file": "input/dialogue.txt",
        "reference": (
            "John asked Mary where she was going. She replied that she was going "
            "to the market. John then asked if she would be back soon, and she "
            "agreed to return within an hour."
        ),
    },
]


def rule_based_narration(turns, speakers):
    sentences = []
    prev = None
    seen = []
    for t in turns:
        g = speakers.get(t["speaker"], "he")
        sp = SPEAKER_MAP_FEMALE if g == "she" else SPEAKER_MAP_MALE
        ag = determine_addressee(t["speaker"], speakers)
        ad = ADDRESSEE_MAP_FEMALE if ag == "she" else ADDRESSEE_MAP_MALE
        ap = "her" if ag == "she" else "him"
        sentences.append(convert_turn(t, sp, ad, prev, g, ap))
        prev = t["speaker"]
        if t["speaker"] not in seen:
            seen.append(t["speaker"])
    return narrate(sentences, speakers=seen, with_opening=True)


def main():
    speakers = load_speakers()
    smoother = SmoothingFunction().method1
    rule_scores = []
    model_scores = []

    for i, case in enumerate(TEST_CASES, 1):
        turns = analyze_dialogue(parse_dialogue(case["file"]))
        raw_turns = parse_dialogue(case["file"])

        rule_out = rule_based_narration(turns, speakers)
        model_out = model_narration(raw_turns)
        ref = case["reference"]

        rule_score = sentence_bleu(
            [ref.split()], rule_out.split(), smoothing_function=smoother
        )
        model_score = sentence_bleu(
            [ref.split()], model_out.split(), smoothing_function=smoother
        )

        rule_scores.append(rule_score)
        model_scores.append(model_score)

        print(f"\n--- Test Case {i} ---")
        print(f"Reference: {ref[:80]}...")
        print(f"Rule-based: {rule_out[:80]}...")
        print(f"Model:      {model_out[:80]}...")
        print(f"BLEU — Rule-based: {rule_score:.3f} | Model: {model_score:.3f}")

    avg_rule = sum(rule_scores) / len(rule_scores)
    avg_model = sum(model_scores) / len(model_scores)

    print("\n" + "=" * 60)
    print(f"AVERAGE BLEU SCORE")
    print(f"  Rule-based:  {avg_rule:.3f}")
    print(f"  Model-based: {avg_model:.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()