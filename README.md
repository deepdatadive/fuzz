# Next Up: Write Batch Scripts

    sbatch -p general -n 1 -N 1 -t 0-1:00 --mem 4000 python index.py --messy example/restaurant-2.csv --nblocks 3 --json-file temp.json
    
    sbatch: error: This does not look like a batch script.  The first
    sbatch: error: line must start with #! followed by the path to an interpreter.
    sbatch: error: For instance: #!/bin/sh




# Fuzzy Merge

How to perform fuzzy matches on Odyssey.

# Installation

Load the Anaconda Python module:

    module load Anaconda

Use conda to install the required packages:

    conda env create -f environment.yml

# Usage

Load the Anaconda Python module:

    module load Anaconda

Activate the environment created above:

    source activate dedupe

Train a gazetteer:

    python train.py --clean-path foreclosures/deduped_banks.csv --messy-path batch.csv --training-file training.json --fields-file foreclosures/fields.json --settings-file foreclosures/my.settings

Merge the two datasets:

    python merge.py --messy-path foreclosures/full_data.csv --settings-file foreclosures/my.settings --output-file temp.csv

# Evaluating the Merge

1.  How confident are we that we found _a_ match for each observation? Plot histogram of predicted probabilities over all observations in the messy data.
2.  How confident are we that we found _the_ match for one observation? Plot histogram of predicted probabilities over all observations in the clean data.

# TODO

As an alternative to using row numbers in the output file we should also allow for specifying id columns.

# Constructing Random Subsample

    head -n 1 foreclosures/full_data.csv > batch.csv
    tail -n +2 foreclosures/full_data.csv | shuf -n 10000 >> batch.csv
