maxPublicationDistance = 105
lengthRanges = range(40, 245, 5)

SPMax = 105
dMax = len(lengthRanges)-1
scoreMax = 10
#this method receives the year a movie was published and returns the publication penalty
def calculatePP( movieReleaseYear  : int, selectedPeriod : range, weightPublication : int) -> float:
    """Calculate publication penalty based on distance from user's period.

    If the movie has no release year, return the full publication weight.
    Otherwise compute SP (scarto pubblicazione) as the distance the
    movie year lies outside the selected period and scale by
    `weightPublication`.

    Args:
        movieReleaseYear: The movie's release year (int).
        selectedPeriod: A range representing the user's desired period.
        weightPublication: Scaling weight for publication distance.

    Returns:
        A float penalty proportional to how far the movie is from the period.
    """
    if(not movieReleaseYear):
        return weightPublication
    """
        SP (scarto pubblicazione) indicates distance between movie release date and selected period. 
        SP is equal to 0 if the publication year is within the range defined by the user
    """
    SP = 0 
    if   movieReleaseYear  not in selectedPeriod:
        SP = max(selectedPeriod.start -  movieReleaseYear ,  movieReleaseYear -selectedPeriod.stop) #SP is how much the publication year falls outside the range
    return SP*weightPublication

#calculate genre score by finding how many matching genres there are
def calculatePList(movieList : list, inputList : list, weightList : int, normalize = True ) -> float:
    """Compute a genre (or list) matching penalty or score.

    If the movie has no genres, return the maximum list weight. If the
    user's input list is empty, return 0. Otherwise count matching
    items and either return a normalized penalty (missing fraction * weight)
    or, when normalize is False, return a negative score proportional to
    number of matches.

    Args:
        movieList: List of movie items (e.g., genres, directors).
        inputList: User-provided list to match against.
        weightList: Weight to scale the result.
        normalize: If True, return normalized penalty; if False return negative match score.

    Returns:
        A float penalty or score based on matches.
    """
    if(not movieList or len(movieList) == 0):
        return weightList
    if(not inputList or inputList == 0):
        return 0
    matchingItems = 0
    for genre in movieList:
        if genre in inputList:
            matchingItems += 1
    if(normalize):
        return (len(inputList) - matchingItems)*weightList/len(inputList)
    else:
        return -(matchingItems * weightList)

def calculatePS(movieScore : float, weightScore : int) -> float:
    """Convert a movie rating into a penalty term.

    Higher movie scores reduce the penalty; the output is scaled by
    `weightScore` and the global `scoreMax`.

    Args:
        movieScore: Numeric rating of the movie.
        weightScore: Scaling weight for score impact.

    Returns:
        A float penalty reflecting the difference from maximum rating.
    """
    return weightScore - (movieScore/scoreMax*weightScore)

def getLengthRange( movielength : int) -> int:
    """Round a movie length to the nearest 5-minute bracket.

    Args:
        movielength: Length in minutes.

    Returns:
        The length rounded to the nearest multiple of 5.
    """

    if( movielength % 5 <= 2):
        return  movielength -  movielength%5
    else:
        return  movielength + 5 -  movielength%5

def calculatePL( movielength : int, selectedBracket : int, weightLength : int ) -> float:
    """Calculate length penalty based on distance between brackets.

    If movielength is missing, return the full weight. Otherwise map the
    movie length to the nearest 5-minute bracket and compute the
    normalized distance `d/dMax` scaled by `weightLength`.

    Args:
        movielength: Movie duration in minutes.
        selectedBracket: The user's preferred length bracket (minutes rounded to multiple of 5).
        weightLength: Scaling weight for length penalty.

    Returns:
        A float penalty proportional to how far the lengths differ.
    """
    d = dMax #d is the distance between the movie's length bracket and the selected bracket. Start by assuming it's max
    if (not  movielength or  movielength == 0):
        return weightLength
    lengthRange = getLengthRange(movielength)
    d = (abs(selectedBracket - lengthRange)) / 5
    PL = d/dMax*weightLength
    return PL