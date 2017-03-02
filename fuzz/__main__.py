import click
import functions
from functions import get_path


@click.command()
@click.option('--clean-path', default=get_path('data', 'restaurant-1.csv'))
@click.option('--messy-path', default=get_path('data', 'restaurant-2.csv'))
@click.option('--training-file', default=get_path('data', 'training.json'))
@click.option('--logger-level', default='WARNING')
# TODO: If we use Anaconda then multiprocessing will not work because
# Anaconda uses MKL: https://github.com/datamade/dedupe/issues/499
@click.option('--num-cores', default=1)
@click.option('--fields-file', default=get_path('data', 'fields.json'))
@click.option('--sample-size', default=10000)
@click.option('--settings-file', default='my.settings')
@click.option('--interactive/--not-interactive', default=True)
def train(*args, **kwargs):
    functions.train(*args, **kwargs)


@click.command()
@click.option('--messy-path', default=get_path('data', 'restaurant-2.csv'))
@click.option('--settings-file', default='my.settings')
@click.option('--output-file', default='output.csv')
@click.option('--first-row-number', default=None, type=int)
@click.option('--offset', default=None, type=int)
@click.option('--nrows', default=None, type=int)
def merge(*args, **kwargs):
    functions.merge(*args, **kwargs)


@click.command()
@click.option('--messy', default=get_path('data', 'restaurant-2.csv'))
@click.option('--settings', default='my.settings')
@click.option('--nblocks', default=10)
@click.option('--output', default='output.csv')
@click.option('--json-file', default='temp.json')
def parallel_merge(*args, **kwargs):
    functions.parallel_merge(*args, **kwargs)


cli = click.Group(commands={
    'train': train,
    'merge': merge,
    'parallel_merge': parallel_merge,
})

if __name__ == '__main__':
    cli()
