# main.py
from parser import parse_dialogue
from analyzer import analyze_dialogue
from converter import (
    load_speakers,
    SPEAKER_MAP_MALE, SPEAKER_MAP_FEMALE,
    ADDRESSEE_MAP_MALE, ADDRESSEE_MAP_FEMALE,
    convert_turn,
    determine_addressee,
)
from narrator import narrate


def main(input_file="input/dialogue.txt",
         output_file="output/narration.txt",
         speakers_file="speakers.json",
         with_opening=True):

    # 1. Load speaker genders
    speakers = load_speakers(speakers_file)

    # 2. Parse
    turns = parse_dialogue(input_file)
    if not turns:
        print("No dialogue found.")
        return

    # 3. Analyze
    turns = analyze_dialogue(turns)

    # 4. Convert each turn (single loop!)
    sentences = []
    prev_speaker = None
    seen = []

    for t in turns:
        speaker_gender = speakers.get(t["speaker"], "he")
        sp_map = SPEAKER_MAP_FEMALE if speaker_gender == "she" else SPEAKER_MAP_MALE

        addressee_gender = determine_addressee(t["speaker"], speakers)
        ad_map = ADDRESSEE_MAP_FEMALE if addressee_gender == "she" else ADDRESSEE_MAP_MALE

        # Addressee object pronoun for commands
        addressee_pronoun = "her" if addressee_gender == "she" else "him"

        sentence = convert_turn(
            t,
            speaker_map=sp_map,
            addressee_map=ad_map,
            previous_speaker=prev_speaker,
            current_speaker_gender=speaker_gender,
            addressee_pronoun=addressee_pronoun,
        )
        sentences.append(sentence)
        prev_speaker = t["speaker"]

        # Track unique speakers in order
        if t["speaker"] not in seen:
            seen.append(t["speaker"])

    # 5. Narrate
    paragraph = narrate(sentences, speakers=seen, with_opening=with_opening)

    # 6. Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(paragraph + "\n")

    print("----- Narration -----")
    print(paragraph)
    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    main()