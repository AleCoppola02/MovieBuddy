import eval
import datareader as dr
from eval import calculatePList, calculatePL, calculatePP, calculatePS, maxPublicationDistance
from datareader import extractList, extractDuration, extractRating, extractYear, getMovieParameterList 

DURATION_INDEX = 0
RATING_INDEX = 1
RELEASEDATE_INDEX = 2
GENRES_INDEX = 3
DIRECTORS_INDEX = 4
ACTORS_INDEX = 5
KEYWORDS_INDEX = 6

weightPublication = 10/maxPublicationDistance 
weightLength = 0.5
weightScore = 0.5
weightGenres = 2.7
weightB = (weightGenres + weightPublication + weightLength + weightScore) / 20
weightDirectors = weightB/2
weightActors = weightB/3
weightKeywords = weightB

def evaluateSecondPhase (movie, userInput:dict):
    """Evaluate a single movie using extended second-phase criteria.

    This computes publication, length, genre and score penalties
    (reusing functions from `eval`) and also adds director/keyword
    based preferences derived from the user's feedback.

    Args:
        movie: Movie index to evaluate.
        userInput: Dict with preferences (period, length, genres and like/dislike lists).

    Returns:
        A single-element tuple containing the total penalty score (lower is better).
    """
    totalScore = 0.0

    movieParameterList = getMovieParameterList(movie, ["duration", "rating", "release_date", "genres", "directors", "stars", "keywords"])
    movieReleaseYear = extractYear(movieParameterList[RELEASEDATE_INDEX])
    movieDuration = extractDuration(movieParameterList[DURATION_INDEX])
    movieGenres = extractList(movieParameterList[GENRES_INDEX])
    movieRating =  extractRating(movieParameterList[RATING_INDEX].item())
    movieDirectors = extractList(movieParameterList[DIRECTORS_INDEX])
    #movieActors = extractList(movieParameterList[ACTORS_INDEX])
    movieKeywords = extractList(movieParameterList[KEYWORDS_INDEX])

    PP = calculatePP(movieReleaseYear, userInput.get("Periodo"), weightPublication) 
    PL = calculatePL(movieDuration, userInput.get("Lunghezza"), weightLength)
    PG = calculatePList(movieGenres, userInput.get("Generi"), weightGenres)
    PS = calculatePS(movieRating, weightScore)

    #scores added in phase 2
    PRplus = calculatePList(movieDirectors, userInput.get("directors+"), weightDirectors) #liked movies
    PRMinus = calculatePList(movieDirectors, userInput.get("directors-"), weightDirectors) #disliked movies
    PR = PRplus - PRMinus

    #PAplus = calculatePList(movieActors, userInput.get("actors+"), weightActors) #liked movies
    #PAMinus = calculatePList(movieActors, userInput.get("actors-"), weightActors) #disliked movies
    #PA = PAplus - PAMinus

    PTplus = calculatePList(movieKeywords, userInput.get("keywords+"), weightKeywords) #liked movies
    PTMinus = calculatePList(movieKeywords, userInput.get("keywords-"), weightKeywords) #disliked movies
    PT = PTplus - PTMinus

    P = PP + PL + PG + PS + PR + PT # +PA
    totalScore += P
    return totalScore, 

def runSecondPhase(firstPhaseResults, secondPhaseInput):
    """Run the second phase ranking over candidates from phase one.

    The first phase returns a collection of candidate individuals.
    This function evaluates each unique movie in those individuals
    using `evaluateSecondPhase`, sorts them by score and returns the
    best movie, along with the general results.

    Args:
        firstPhaseResults: Iterable of individuals (lists of movie indices).
        secondPhaseInput: User preference dict augmented with phase-2 preferences.

    Returns:
        A tuple: (best_individual_index, best_score, scored_list) where scored_list is
        a list of (score, movie_index) tuples sorted ascending by score.
    """ 
    scored = []
    toCheck = {elem for individual in firstPhaseResults for elem in individual}


    for elem in toCheck:
        score = evaluateSecondPhase(elem, secondPhaseInput)
        scored.append((score, elem))

    scored.sort(key=lambda x: x[0])  # lowest score = best
    
    (best_score, best_individual) = scored[0]
    return best_individual, best_score, scored

