import tkinter as tk
from tkinter import messagebox, ttk
from deap import base, creator, tools
import pandas as pd
import random
import re
import numpy as np
import random
import genutils as gu
import datareader as dr
from genutils import geneticAlgorithm, getToolbox
import graphics
from graphics import promptGeneticInputs, promptUserPreference, SimpleLoadingScreen, MovieExplanationGUI
from datareader import extractPreferences
import secondphase
from secondphase import runSecondPhase
import threading

pop_size= 150
cxpb= 0.7
mutpb= 0.11
min_iter= 10
max_iter= 20
toolbox = getToolbox()


userInput= promptGeneticInputs()

if(userInput == None):
    exit()

# --- START OF LOADING SCREEN LOGIC ---
loading = SimpleLoadingScreen()
# Use a container to get the result out of the thread
results_container = []

#Define a function that will be executed by a background thread
def run_ga():
    """Run the genetic algorithm in a background thread and store results.

    This helper invokes `geneticAlgorithm` with configured parameters,
    appends the returned value to `results_container` and quits the
    loading window's mainloop to continue the main UI flow.
    """
    res = geneticAlgorithm(
        toolbox=toolbox,
        userInput=userInput,
        pop_size=pop_size,
        cxpb=cxpb,
        mutpb=mutpb,
        min_iter=min_iter,
        max_iter=max_iter
    )
    results_container.append(res)
    loading.root.quit() 

# Start the genetic algorithm in the background
threading.Thread(target=run_ga, daemon=True).start()

# Show the loading window
loading.root.mainloop() 

# Once mainloop ends, grab the result and close the window
firstPhaseResults = results_container[0]
loading.close()
# --- END OF LOADING SCREEN LOGIC ---

inputPreferences = promptUserPreference(firstPhaseResults[0])
preferences = extractPreferences(inputPreferences)

secondPhaseInput = userInput | preferences
finalResult = runSecondPhase(firstPhaseResults, secondPhaseInput)
MovieExplanationGUI(finalResult[0], preferences)

print(finalResult)






