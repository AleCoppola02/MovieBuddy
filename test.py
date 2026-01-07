import itertools
from datetime import datetime
from genutils import *
from graphics import promptGeneticInputs

toolbox = getToolbox()


userInput= promptGeneticInputs()
# Define parameter search space
PARAM_SPACE = {
    "pop_size":  [10, 20, 30, 40, 50, 75, 100, 150],
    "cxpb":      [x / 100 for x in range(10, 101, 10)],    # 0.10 → 1.00
    "mutpb":     [x / 100 for x in range(1, 51, 5)],       # 0.01 → 0.50
    "min_iter":  [5, 10, 20, 30],
    "max_iter":  [50, 75, 100, 150]
}

# Generate all combinations of parameters
def generate_param_grid(param_space):
    keys = list(param_space.keys())
    values = list(param_space.values())
    
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))

# Run mass tests over the parameter grid
def run_mass_tests():
    total_tests = 1
    for values in PARAM_SPACE.values():
        total_tests *= len(values)

    print(f"Total tests to run: {total_tests}")
    print("Starting...\n")

    with open("tests.txt", "a") as f:
        f.write(f"\n=== MASS TEST SESSION [{datetime.now()}] ===\n")

        for i, params in enumerate(generate_param_grid(PARAM_SPACE), start=1):

            # Run the genetic algorithm with the current parameter set
            firstPhaseResult = geneticAlgorithm(
                toolbox=toolbox,
                userInput=userInput,
                pop_size=params["pop_size"],
                cxpb=params["cxpb"],
                mutpb=params["mutpb"],
                min_iter=params["min_iter"],
                max_iter=params["max_iter"]
            )

            # Evaluate this iteration's result
            score = evaluate(firstPhaseResult[0], userInput)

            # Log the result
            f.write(f"Test {i}/{total_tests}: {params} -> Score = {score}\n")

            # Optional console feedback
            print(f"[{i}/{total_tests}] {params} -> Score={score}")

    print("\nAll tests completed.\n")


# Run tests
run_mass_tests()


