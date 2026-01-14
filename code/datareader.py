import pandas
import numpy as np

def getDataFrame(name : str) -> pandas.DataFrame:
    """Load a parquet file into a pandas DataFrame.

    Args:
        name: Path to the parquet file.

    Returns:
        A pandas.DataFrame containing the file data.
    """
    return pandas.read_parquet(name) 

df = getDataFrame("dataset.parquet")

def extractYear(date_str: str) -> int:
    """Extract the year as an integer from a date string.

    Expected format is 'YYYY-MM-DD'.
    Args:
        date_str: Date string in ISO-like format.

    Returns:
        The year as an int.
    """
    return int(date_str.split("-")[0])

def extractDuration(time_str: str) -> int:
    """Parse a duration string and return total minutes.

    Accepts strings such as '1h 30m', '45m', or '2h'. Returns 0 for
    falsy or empty inputs.

    Args:
        time_str: Duration string.

    Returns:
        Total duration in minutes as an int.
    """
    if not time_str or not time_str.strip(): #handle null values
        return 0
    
    time_str = time_str.strip()
    hours = 0
    minutes = 0

    # Split into parts, e.g., ["1h", "30m"]
    parts = time_str.split()

    for part in parts:
        if part.endswith("h"):
            hours = int(part[:-1])
        elif part.endswith("m"):
            minutes = int(part[:-1])

    return hours * 60 + minutes

def extractList(string: str) -> list:
    """Convert a stringified list (e.g. "['A','B']") to a Python list.

    Returns None for empty or missing values. Strips surrounding
    brackets and quotes and returns a list of strings.

    Args:
        string: The input string representing a list.

    Returns:
        A list of strings, or None if input is empty.
    """
    if(not string or not string.strip() or string == "[]"):
        return None
    stringList = string.removeprefix("[").removesuffix("]").split(",")
    for  i in range(len(stringList)):
        stringList[i] = stringList[i].strip().removeprefix("'").removesuffix("'")
    return stringList

def extractRating(rating : float):
    """Safely extract a numeric rating, converting NaN to 0.

    Args:
        rating: Numeric rating (may be numpy.nan).

    Returns:
        Rating value or 0 if NaN.
    """
    if(np.isnan(rating)):
        return 0
    else: 
        return rating

def getMovieParameterList(index : int, columns = ["duration", "rating", "release_date", "genres"] ) -> list:
    """Retrieve selected parameter values for a movie by index.

    Args:
        index: Row index in the global dataframe `df`.
        columns: List of columns to extract (default duration, rating, release_date, genres).

    Returns:
        A list containing the column values for the given index.
    """
    row = df.loc[index, columns ].tolist()
    return row

def normalize(value):
    """Normalize stored list-like values to a Python list.

    - None becomes an empty list.
    - A string is parsed via `extractList`.
    - Other iterable values are cast to `list`.

    Args:
        value: The value to normalize.

    Returns:
        A list representing the normalized value.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return extractList(value)
    return list(value)

def extractPreferences(choice_dict):
    """Build a user preference dictionary from rated movie indices.

    The provided `choice_dict` maps categories (e.g. 'like'/'dislike') to
    lists of movie indices. For each index, this function collects the
    movie's actors, directors and keywords and returns a dict with
    keys like 'actors+' / 'actors-' containing lists of unique values.

    Args:
        choice_dict: Dict mapping 'like'/'dislike' to lists of movie indices.

    Returns:
        Dict with keys 'actors+', 'actors-', 'directors+', 'directors-', 'keywords+', 'keywords-'.
    """
    preferences = {
        "actors+": set(),
        "actors-": set(),
        "directors+": set(),
        "directors-": set(),
        "keywords+": set(),
        "keywords-": set()
    }

    COLUMNS = ["stars", "directors", "keywords"]

    for category, index_list in choice_dict.items():
        sign = "+" if category == "like" else "-"

        for idx in index_list:
            actors, directors, keywords = getMovieParameterList(idx, COLUMNS)

            actors = normalize(actors)
            directors = normalize(directors)
            keywords = normalize(keywords)

            preferences[f"actors{sign}"].update(actors)
            preferences[f"directors{sign}"].update(directors)
            preferences[f"keywords{sign}"].update(keywords)

    return {key: list(values) for key, values in preferences.items()}