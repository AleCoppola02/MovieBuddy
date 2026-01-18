import datareader as dr
import random
import numpy as np
from deap import tools, creator, base
from datareader import *
import eval
from eval import calculatePList, calculatePL, calculatePP, calculatePS, maxPublicationDistance
from datareader import extractRating, extractDuration, extractList, extractYear, getMovieParameterList

weightPublication = 10/maxPublicationDistance
weightLength = 0.5
weightScore = 0.5
weightGenres = 2.7

DURATION_INDEX = 0
RATING_INDEX = 1
RELEASEDATE_INDEX = 2
GENRES_INDEX = 3
IND_SIZE = 5

def mutRandomReset(individual, low=1, high=63248, indpb=0.05):
    """
    Random resetting mutation for list-based integer individuals.
    Each gene has an independent probability indpb of being reset.
    """
    for i in range(len(individual)):
        if random.random() < indpb:
            individual[i] = random.randint(low, high)
    return (individual,)

def cxUniformInts(ind1, ind2, indpb=0.1):
    """
    Uniform crossover for list-based integer individuals.
    For each gene, swap with probability indpb.
    """
    for i in range(len(ind1)):
        if random.random() < indpb:
            ind1[i], ind2[i] = ind2[i], ind1[i]
    return ind1, ind2

def selProbabilisticTournament(population, k, tournsize=3, p=0.7):
    """Select k individuals using probabilistic tournament selection.

    For each of k selections, a tournament of `tournsize` individuals is
    sampled. Those aspirants are ranked by fitness and a winner is
    chosen probabilistically based on geometric-like probabilities
    controlled by `p` (the top-ranked has probability ~p).

    Args:
        population: Sequence of individuals (with `.fitness.values`).
        k: Number of individuals to select.
        tournsize: Number of aspirants per tournament.
        p: Base probability for top-ranked aspirant.

    Returns:
        A list of selected individuals.
    """
    minimize = all(w < 0 for w in population[0].fitness.weights) #if individuals have negative weights, sort by descending order so lower fitness is better
    chosen = []
    for _ in range(k):
        

        # Draw tournament contenders
        aspirants = random.sample(population, tournsize)
        
        # Sort by fitness based on minimize
        aspirants.sort(key=lambda ind: ind.fitness.values, reverse = not minimize)

        # Probabilities based on rank
        probs = []
        for i in range(tournsize):
            probs.append(p * ((1 - p) ** i))
        
        # Normalize
        total = sum(probs)
        probs = [x / total for x in probs]

        # Choose one individual proportional to probability
        winner = random.choices(aspirants, weights=probs, k=1)[0]
        chosen.append(winner)
    
    return chosen

def evaluate(individual, userInput : dict) -> float:
    """Compute the aggregate fitness score for an individual.

    Each individual is a list of movie indices. For each movie this
    function extracts parameters (duration, rating, release year, genres)
    and computes the component penalties using functions from `eval`.

    Args:
        individual: Iterable of movie indices.
        userInput: Dict containing user preferences used by scoring functions.

    Returns:
        A single-element tuple containing the total score (lower is better).
    """
    totalScore = 0.0
    for  movie in individual:
        movieParameterList = getMovieParameterList(movie)
        movieReleaseYear = extractYear(movieParameterList[RELEASEDATE_INDEX])
        movieDuration = extractDuration(movieParameterList[DURATION_INDEX])
        movieGenres = extractList(movieParameterList[GENRES_INDEX])
        movieRating =  extractRating(movieParameterList[RATING_INDEX].item())

        PP = calculatePP(movieReleaseYear, userInput.get("Periodo"), weightPublication) 
        PL = calculatePL(movieDuration, userInput.get("Lunghezza"), weightLength)
        PG = calculatePList(movieGenres, userInput.get("Generi"), weightGenres)
        PS = calculatePS(movieRating, weightScore)

        P = PP + PL + PG + PS
        totalScore += P
    return totalScore, 








def geneticAlgorithm(userInput:dict, toolbox, pop_size=100, cxpb=0.2, mutpb=0.02, min_iter = 5, max_iter = 15):
    """Run a genetic algorithm to optimize movie selections.

    The function uses the provided DEAP `toolbox` to create an initial
    population, evaluate individuals, and iterate selection, crossover
    and mutation until a stopping condition (max generations or
    stagnation) is met.

    Args:
        userInput: Dict with user preference parameters used by the evaluator.
        toolbox: DEAP toolbox configured with `population`, `evaluate`, `select`, `mate`, `mutate`.
        pop_size: Population size.
        cxpb: Crossover probability applied per pair of individuals.
        mutpb: Mutation probability applied per individual.
        min_iter: Minimum number of generations to run before allowing early stop.
        max_iter: Maximum number of generations to run.

    Returns:
        The selected best individuals as returned by `tools.selBest`.
    """

    # Create population
    population = toolbox.population(n=pop_size)

    # Evaluate initial population
    fitnesses = list(map(lambda ind: toolbox.evaluate(ind, userInput), population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    # Track best fitness and stagnation
    best_prev = min(ind.fitness.values[0] for ind in population)
    stagnation_counter = 0 # Initialize stagnation counter
    MAX_STAGNATION = 2    
    
    gen = 0

    # The loop now stops if gen reaches max_iter OR stagnation_counter reaches MAX_STAGNATION
    while gen < max_iter and stagnation_counter < MAX_STAGNATION:
        gen += 1
        
        # Check stagnation and update best_prev after the mandatory minimum iterations
        if gen > min_iter:
            best_now = min(ind.fitness.values[0] for ind in population)

            if best_now < best_prev:
                # improvement (lower is better)
                best_prev = best_now
                stagnation_counter = 0
            else:
                # no improvement (equal or worse)
                stagnation_counter += 1
        
        # Selection
        offspring = toolbox.select(population, len(population))

        # Clone the offspring (DEAP convention)
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover
        # zip does pairwise iteration over the offspring list and crossover is applied to each pair
        for child1, child2 in zip(offspring[::2], offspring[1::2]): #offspring[::2] gives even indexed, offspring[1::2] gives odd indexed
            if random.random() < cxpb:
                toolbox.mate(child1, child2, indpb = 0.5)
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Re-evaluate individuals with invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid_ind:
            ind.fitness.values = toolbox.evaluate(ind, userInput)

        # Replace population 
        population = offspring

    # Return Best movies 
    print(gen)
    return tools.selBest(population, pop_size)


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)


def getToolbox():
    toolbox = base.Toolbox()
    toolbox.register("mutate", mutRandomReset, low=0, high=63248, indpb=0.2)
    toolbox.register("select", selProbabilisticTournament, tournsize=3, p=0.7)
    toolbox.register("mate", cxUniformInts, indpb=0.5)

    toolbox.register("movie_index", random.randint, 0, 63248)
    toolbox.register("individual", tools.initRepeat, creator.Individual,
                    toolbox.movie_index, n=IND_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    return toolbox