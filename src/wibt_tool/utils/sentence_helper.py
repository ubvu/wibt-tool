import re



def get_numbered_sentences(text):
    sentence_pattern = r"(?<=[.!?])\s+|\n+"
    sentences = re.split(sentence_pattern, text)
    clean_sentences = [s.strip() for s in sentences if s.strip()]
    return [f"{i}: {sentence}" for i, sentence in enumerate(clean_sentences, 1)]
