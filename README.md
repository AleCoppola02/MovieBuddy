

# MovieBuddy
This repository contains a small genetic-algorithm-based movie recommender GUI.

## Dependencies
- Python 3.8 or newer
- pandas
- numpy
- deap
- spacy
- PyArrow
- FastParquet

Optional (for `tagmaker.py`):

`python -m spacy download en_core_web_sm`


Note: `tkinter` is used for the GUI and is included with standard Windows Python installs.

## How to run
From the `code` folder, run: 

`python moviebuddy.py`

The program uses the provided dataset which you can find [here](https://www.kaggle.com/datasets/raedaddala/top-500-600-movies-of-each-year-from-1960-to-2024/data).
The file dataset.parquet is used for the algorithm. If you use your own dataset, it must contain the fields "duration", "rating", "release_date", "genres", "directors", "stars", "keywords", "description"

If you wish to use tagmaker.py, run 

`python tagmaker.py --input-csv your_dataset.csv --output-csv your_output.csv --description-column description_column_name --keywords-column keywords_column_name`







