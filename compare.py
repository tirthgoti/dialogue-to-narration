# compare.py
from parser import parse_dialogue
from analyzer import analyze_dialogue
from converter import (
    load_speakers, SPEAKER_MAP_MALE, SPEAKER_MAP_FEMALE,
    ADDRESSEE_MAP_MALE, ADDRESSEE_MAP_FEMALE,
    convert_turn, determine_addressee,
)
from narrator import narrate
from model_narrator import model_narration


def rule_based_narration(turns, speakers):
    """Run the rule-based pipeline on analyzed turns."""
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
    print("=" * 70)
    print("DIALOGUE-TO-NARRATION: RULE-BASED vs MODEL-BASED")
    print("=" * 70)

    speakers = load_speakers()
    turns = analyze_dialogue(parse_dialogue("input/dialogue.txt"))

    print("\n--- INPUT DIALOGUE ---")
    for t in turns:
        print(f'  {t["speaker"]}: "{t["text"]}"')

    print("\n--- RULE-BASED OUTPUT ---")
    rule_out = rule_based_narration(turns, speakers)
    print("  " + rule_out)

    print("\n--- MODEL-BASED OUTPUT (DistilBART) ---")
    # Pass raw parsed turns (model_narrator will handle formatting)
    raw_turns = parse_dialogue("input/dialogue.txt")
    model_out = model_narration(raw_turns)
    print("  " + model_out)

    print("\n" + "=" * 70)

    # Save both outputs to files
    with open("output/rule_based_narration.txt", "w", encoding="utf-8") as f:
        f.write(rule_out + "\n")
    with open("output/model_narration.txt", "w", encoding="utf-8") as f:
        f.write(model_out + "\n")

    print("\nSaved:")
    print("  output/rule_based_narration.txt")
    print("  output/model_narration.txt")


if __name__ == "__main__":
    main()