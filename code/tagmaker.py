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
import argparse

# -------------------------------
# CONFIG
# -------------------------------
INPUT_CSV = "dataset.csv"
OUTPUT_CSV = "dataset_refined_keywords3.csv"
MAX_TAGS_PER_MOVIE = 3

DESCRIPTION_COLUMN = "description"
KEYWORDS_COLUMN = "keywords"

# Remove overly generic nouns and common low-information words.
# This list intentionally includes some prepositions/functional words
# that occasionally get mis-classified as nouns by the parser.
BLACKLIST = {
    # generic human/group terms
    "man", "woman", "people", "person", "someone", "anyone",
    "everyone", "others", "group", "groups", "family", "families",
    "guy", "girl"
    # generic narrative/time/place words
    "life", "story", "stories", "film", "films", "movie", "movies",
    "world", "time", "times", "way", "ways", "day", "days",
    "night", "year", "years", "place", "places", "home", "homes",
    # low-information nouns often appearing in descriptions
    "part", "parts", "role", "roles", "character", "characters",
    "scene", "scenes", "actor", "actors", "actress", "actresses",
    "thing", "things", "something", "someone", "case", "cases",
    "problem", "problems", "area", "areas", "system", "systems",
    "city", "cities", "country", "countries", "friend", "friends",
    "tale", "tales", "story", "stories"
    # prepositions / function words that may be mis-tagged
    "behalf", "after", "before", "during", "via", "including",
    "regarding", "per", "among", "between", 
    "about", "above", "across", "against", "along", "alongside",
    "among", "around", "as", "at", "before", "behind", "below",
    "beneath", "beside", "besides", "between", "beyond", "but",
    "by", "concerning", "considering", "despite", "down", "during",
    "except", "for", "from", "in", "inside", "into", "like",
    "near", "of", "off", "on", "onto", "out", "outside", "over",
    "past", "per", "regarding", "round", "since", "through",
    "throughout", "to", "toward", "towards", "under", "underneath",
    "until", "up", "upon", "with", "within", "without", "via",
    "according"
}

# Load spaCy English model

nlp = spacy.load("en_core_web_sm")

# tag extraction function
def extract_movie_tags(description: str, max_tags=6) -> list:
    #Extract up to `max_tags` meaningful noun-based tags from text.
    
    if not description or not isinstance(description, str):
        return []

    doc = nlp(description.lower()) #spacy doc object contains grammatical info 
    candidates = []
    #chunks are sintactic units identified by spacy
    for chunk in doc.noun_chunks: #noun chunks are phrases centered around a noun automatically extracted by spacy
        token_info = []  # (index, lemma, pos_)
        has_noun = False

        for tok in chunk:
            # skip non-alphabetic tokens and stop words
            if not tok.is_alpha or tok.is_stop:
                continue

            # only allow adjectives and common nouns (exclude proper nouns)
            if tok.pos_ not in ("ADJ", "NOUN"):
                continue

            lemma = tok.lemma_.strip()
            if not lemma:
                continue

            # skip overly short lemmas and blacklist items
            if len(lemma) < 3 or lemma in BLACKLIST:
                continue

            token_info.append((tok.i, lemma, tok.pos_))
            if tok.pos_ == "NOUN":
                has_noun = True

        if not token_info or not has_noun:
            continue

        token_info.sort(key=lambda x: x[0])
        lemmas = [t[1] for t in token_info]

        # single-word noun candidates (exclude proper nouns)
        for _, lemma, pos in token_info:
            if pos == "NOUN":
                candidates.append(lemma)

        # (No multi-word candidates — only single-word nouns are kept)

    # Only single-word noun tags are returned (ranked by frequency).
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


def main(input_csv: str = None,
         output_csv: str = None,
         description_col: str = None,
         keywords_col: str = None):
    """Script entry point: read input CSV, extract tags, save output CSV.

    This function iterates over the `DESCRIPTION_COLUMN` values in the
    input file, extracts up to `MAX_TAGS_PER_MOVIE` tags per row, formats
    them for CSV and writes the result to `OUTPUT_CSV`.
    """
    # resolve parameters: use provided values or fall back to module defaults
    input_csv = input_csv or INPUT_CSV
    output_csv = output_csv or OUTPUT_CSV
    description_col = description_col or DESCRIPTION_COLUMN
    keywords_col = keywords_col or KEYWORDS_COLUMN

    print("Loading dataset...")
    df = pd.read_csv(input_csv)

    if description_col not in df.columns:
        raise ValueError(f"Column '{description_col}' not found in {input_csv}")

    refined_keywords = []

    print("Extracting refined tags...")
    for i, desc in enumerate(df[DESCRIPTION_COLUMN]):
        tags = extract_movie_tags(desc, MAX_TAGS_PER_MOVIE)
        refined_keywords.append(format_tags_for_csv(tags))

        if i > 0 and i % 500 == 0:
            print(f"Processed {i} movies")

    df[keywords_col] = refined_keywords

    print("Saving new dataset...")
    df.to_csv(output_csv, index=False)

    print("Done.")
    print(f"Saved as: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract refined keyword tags from movie descriptions.")
    parser.add_argument("--input-csv", dest="input_csv", help="Path to input CSV", default=INPUT_CSV)
    parser.add_argument("--output-csv", dest="output_csv", help="Path to output CSV", default=OUTPUT_CSV)
    parser.add_argument("--description-column", dest="description_col", help="Name of the description column", default=DESCRIPTION_COLUMN)
    parser.add_argument("--keywords-column", dest="keywords_col", help="Name of the keywords column to write", default=KEYWORDS_COLUMN)

    args = parser.parse_args()
    main(input_csv=args.input_csv,
         output_csv=args.output_csv,
         description_col=args.description_col,
         keywords_col=args.keywords_col)
