# narrator.py
import re


def join_sentences(sentences):
    """
    Join a list of narration sentences into one paragraph.
    Normalizes whitespace, ensures each sentence ends with punctuation.
    """
    if not sentences:
        return ""

    cleaned = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Collapse any multiple spaces into one
        s = re.sub(r'\s+', ' ', s)
        # Ensure sentence ends with punctuation
        if not s.endswith((".", "!", "?")):
            s += "."
        cleaned.append(s)

    # Join with a single space between sentences
    paragraph = " ".join(cleaned)

    # Final whitespace normalize
    paragraph = re.sub(r'\s+', ' ', paragraph).strip()

    # Capitalize first letter
    if paragraph:
        paragraph = paragraph[0].upper() + paragraph[1:]

    return paragraph


def add_opening(paragraph, speakers):
    """
    Optional framing sentence: "John and Mary had the following conversation."
    """
    if len(speakers) >= 2:
        names = ", ".join(speakers[:-1]) + " and " + speakers[-1]
        opening = f"{names} had the following conversation."
        return opening + " " + paragraph
    return paragraph


def narrate(sentences, speakers=None, with_opening=False):
    paragraph = join_sentences(sentences)
    if with_opening and speakers:
        paragraph = add_opening(paragraph, speakers)
    return paragraph