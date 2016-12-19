#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools
import csv
import dedupe
import os
import time
import optparse
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm
import click
import json


def _data_frame_to_dict(data, name):
    return {
        '%s:%d' % (name, i): row.to_dict() for i, row in data.iterrows()
    }


@click.command()
@click.option('--clean-path', default='example/restaurant-1.csv')
@click.option('--messy-path', default='example/restaurant-2.csv')
@click.option('--training-file', default='example/training.json')
@click.option('--logger-level', default='WARNING')
@click.option('--num-cores', default=1)
@click.option('--fields-file', default='example/fields.json')
@click.option('--output-file', default='example/output.csv')
def main(clean_path, messy_path, training_file, logger_level, num_cores, fields_file, output_file):
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)
    
    clean = pd.read_csv(clean_path)
    data_1 = _data_frame_to_dict(clean, name=clean_path)
    messy = pd.read_csv(messy_path)
    data_2 = _data_frame_to_dict(messy, name=messy_path)

    true_matches = clean.set_index('unique_id').join(
        messy.set_index('unique_id'),
        how='inner', lsuffix='_clean', rsuffix='_messy'
    )

    with open(fields_file) as f:
        fields = json.load(f)

    gazetteer = dedupe.Gazetteer(fields, num_cores=num_cores)
    gazetteer.sample(data_1, data_2, 10000)

    # Let's train manually at the console:
    if os.path.exists(training_file):
        with open(training_file, 'r') as tf:
            gazetteer.readTraining(tf)
    dedupe.consoleLabel(gazetteer)
    # Save the manual entries in case we need them later
    with open(training_file, 'w') as tf:
        gazetteer.writeTraining(tf)

    gazetteer.train()

    gazetteer.index(data_1)

    alpha = gazetteer.threshold(data_2)

    # Add columns to messy data
    messy['match_id'] = np.nan
    messy['match_probability'] = np.nan
    for i, row in tqdm(messy.iterrows()):
        d = row.to_dict()
        match = gazetteer.match({i: d}, threshold=alpha)
        if match:
            pair, phat = match[0][0]
            messy.loc[i, 'match_id'] = pair[1]
            messy.loc[i, 'match_probability'] = phat

    messy.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()
