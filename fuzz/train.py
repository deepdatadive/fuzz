from tqdm import tqdm
import click
import csv
import dedupe
import json
import logging
import os
import re


# https://github.com/datamade/dedupe/blob/master/tests/exampleIO.py#L5-L11
def _clean(s):
    result = re.sub('\n', ' ', s)
    result = re.sub(r'[^\x00-\x7F]','?', result) # remove non-ascii characters
    result = re.sub('  +', ' ', result)
    result = result.strip().strip('"').strip("'").lower()
    if not result:
        result = None
    return result


def read_csv(path, first_row_number=None, offset=None, nrows=None, encoding='utf-8'):
    assert (first_row_number is None and offset is None and nrows is None) or \
        (first_row_number is not None and offset is not None and nrows is not None)

    read_whole_file = first_row_number is None
    clean_row = lambda x: {k : _clean(v.decode(encoding)) for (k, v) in x.iteritems()}

    with open(path) as f:
        reader = csv.DictReader(f)

        if read_whole_file:
            for i, row in enumerate(reader):
                yield i + 1, clean_row(row)
        else:
            # initialize the headers
            first_row = reader.next()
            # reposition the reader
            f.seek(offset)
            for i, row in enumerate(reader):
                yield first_row_number + i, clean_row(row)
                if i == nrows - 1:
                    break
            


def read(*args, **kwargs):
    enum_rows = read_csv(*args, **kwargs)
    return {i: row for i, row in enum_rows}


@click.command()
@click.option('--clean-path', default='example/restaurant-1.csv')
@click.option('--messy-path', default='example/restaurant-2.csv')
@click.option('--training-file', default='example/training.json')
@click.option('--logger-level', default='WARNING')
# TODO: If we use Anaconda then multiprocessing will not work because
# Anaconda uses MKL: https://github.com/datamade/dedupe/issues/499
@click.option('--num-cores', default=1)
@click.option('--fields-file', default='example/fields.json')
@click.option('--sample-size', default=10000)
@click.option('--settings-file', default='example/my.settings')
@click.option('--interactive/--not-interactive', default=True)
def train(clean_path, messy_path, training_file, logger_level, num_cores, fields_file, sample_size, settings_file, interactive):
    # Set logger level
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)

    logging.info('Reading data ...')
    clean = read(clean_path)
    messy = read(messy_path, encoding='latin-1')

    logging.info('Reading metadata ...')
    with open(fields_file) as f:
        fields = json.load(f)

    logging.info('Initializing gazetteer ...')
    gazetteer = dedupe.Gazetteer(fields, num_cores=num_cores)

    logging.info('Sampling pairs for gazetteer ...')
    gazetteer.sample(clean, messy, sample_size=sample_size)

    # Train the gazetteer at the console
    if os.path.exists(training_file):
        with open(training_file, 'r') as tf:
            gazetteer.readTraining(tf)

    if interactive:
        dedupe.consoleLabel(gazetteer)
        # Save the manual entries
        with open(training_file, 'w') as tf:
            gazetteer.writeTraining(tf)

    logging.info('Training gazetteer ...')
    gazetteer.train(recall=1.0, index_predicates=False)

    logging.info('Indexing gazetteer ...')
    gazetteer.index(clean)

    with open(settings_file, 'wb') as f:
        gazetteer.writeSettings(f, index=True)


if __name__ == '__main__':
    train()