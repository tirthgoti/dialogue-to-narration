# model_narrator.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "sshleifer/distilbart-cnn-6-6"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
print("Model loaded.")


def dialogue_to_text(turns):
    """Convert parsed turns into a single string for the model."""
    return " ".join(f'{t["speaker"]}: {t["text"]}' for t in turns)


def model_narration(turns, max_len=80, min_len=25):
    """Generate narration using a pre-trained summarization model."""
    dialogue_text = dialogue_to_text(turns)
    if len(dialogue_text) > 900:
        dialogue_text = dialogue_text[:900]

    try:
        inputs = tokenizer(
            dialogue_text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )
        outputs = model.generate(
            **inputs,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            num_beams=4,
        )
        result = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return result.strip()
    except Exception as e:
        return f"[Model error: {e}]"


if __name__ == "__main__":
    from parser import parse_dialogue
    turns = parse_dialogue("input/dialogue.txt")
    print("\n--- Model-generated narration ---")
    print(model_narration(turns))