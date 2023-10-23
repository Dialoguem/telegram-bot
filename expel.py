#!/usr/bin/env python

import csv

import click


AVATARS_FINISHED = 'data/avatars_finished.csv'


@click.command()
@click.argument('avatar')
def main(avatar):
    with open(AVATARS_FINISHED, 'a') as f:
        csv.writer(f).writerow([avatar])


if __name__ == '__main__':
    main()
