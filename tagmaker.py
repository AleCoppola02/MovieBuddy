"""Extract refined keyword tags from movie descriptions.

This module reads movie descriptions and extracts a small set of
meaningful noun-based tags using spaCy. It is intended to produce a
keywords column suitable for saving to CSV and later use by the
recommendation pipeline.

Dependencies:
    - spaCy with the "en_core_web_sm" model installed.

Run this file as a script to read `INPUT_CSV`, extract
tags and write `OUTPUT_CSV`.
"""

import pandas as pd
import spacy
from collections import Counter

# -------------------------------
# CONFIG
# -------------------------------
INPUT_CSV = "dataset.csv"
OUTPUT_CSV = "dataset_refined_keywords2.csv"
MAX_TAGS_PER_MOVIE = 6

DESCRIPTION_COLUMN = "description"
KEYWORDS_COLUMN = "keywords"

# Remove overly generic nouns
BLACKLIST = {
    "man", "woman", "people", "person", "life", "story",
    "film", "movie", "world", "time", "way", "day", "year"
}

# Load spaCy English model

nlp = spacy.load("en_core_web_sm")

# tag extraction function
def extract_movie_tags(description: str, max_tags=6) -> list:
    """Extract up to `max_tags` noun-based tags from a description.

    The function uses spaCy to parse the description, collects noun
    chunks, filters tokens to keep only meaningful nouns (excluding
    common blacklist words), and ranks candidates by frequency. Multi-
    word tags up to two words are allowed.

    Args:
        description: Movie description text.
        max_tags: Maximum number of tags to return.

    Returns:
        A list of tag strings (empty list for missing/invalid input).
    """
    if not description or not isinstance(description, str):
        return []

    doc = nlp(description.lower())
    candidates = []

    for chunk in doc.noun_chunks:
        tokens = []

        for tok in chunk:
            # Only nouns (ignore proper noun distinction here)
            if tok.pos_ != "NOUN":
                continue

            # Exclude pronouns & adverbs explicitly
            if tok.pos_ == "PRON" or tok.pos_ == "ADV":
                continue

            lemma = tok.lemma_.strip()
            # Exclude blacklisted words
            if not lemma or lemma in BLACKLIST:
                continue

            tokens.append(lemma)

        # Allow 1-2 word tags only
        if 1 <= len(tokens) <= 2:
            candidates.append(" ".join(tokens))

    ranked = [tag for tag, _ in Counter(candidates).most_common(max_tags)]
    return ranked

def format_tags_for_csv(tags: list) -> str:
    """Format a list of tags for CSV storage.

    The project stores keyword lists as stringified Python lists like
    "['tag1', 'tag2']". This helper converts an iterable of tags into
    that representation, returning "[]" for empty inputs.

    Args:
        tags: Iterable of tag strings.

    Returns:
        A string suitable for writing into a CSV keywords column.
    """
    if not tags:
        return "[]"
    return "[" + ", ".join(f"'{t}'" for t in tags) + "]"


def main():
    """Script entry point: read input CSV, extract tags, save output CSV.

    This function iterates over the `DESCRIPTION_COLUMN` values in the
    input file, extracts up to `MAX_TAGS_PER_MOVIE` tags per row, formats
    them for CSV and writes the result to `OUTPUT_CSV`.
    """
    print("Loading dataset...")
    df = pd.read_csv(INPUT_CSV)

    if DESCRIPTION_COLUMN not in df.columns:
        raise ValueError(f"Column '{DESCRIPTION_COLUMN}' not found")

    refined_keywords = []

    print("Extracting refined tags...")
    for i, desc in enumerate(df[DESCRIPTION_COLUMN]):
        tags = extract_movie_tags(desc, MAX_TAGS_PER_MOVIE)
        refined_keywords.append(format_tags_for_csv(tags))

        if i > 0 and i % 500 == 0:
            print(f"Processed {i} movies")

    df[KEYWORDS_COLUMN] = refined_keywords

    print("Saving new dataset...")
    df.to_csv(OUTPUT_CSV, index=False)

    print("Done.")
    print(f"Saved as: {OUTPUT_CSV}")

# -------------------------------
if __name__ == "__main__":
    main()
