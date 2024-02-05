#!/usr/bin/env python

import json

import click
import pandas as pd


OWN_OPINIONS = 'data/own_opinions.csv'
OWN_OPINIONS_COLS = ['round', 'group', 'avatar', 'opinion', 'rating']
OTHER_OPINIONS = 'data/other_opinions.csv'
OTHER_OPINIONS_COLS = [
    'round', 'group', 'subject', 'object', 'rating', 'compromise'
]
AVATARS_FINISHED = 'data/avatars_finished.csv'
AVATARS_FINISHED_COLS = ['avatar']


def group_status(g, avatars):
    try:
        opinions = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS, sep='\t')
        opinions = opinions[opinions['group'] == g]
        ronda = opinions['round'].max()
        esperant = set(opinions[opinions['round'] == ronda]['avatar'])
        anterior = set(opinions[opinions['round'] == ronda-1]['avatar'])
    except FileNotFoundError:
        ronda = 1
        esperant = set()
        anterior = set()
    try:
        exp = pd.read_csv(
            AVATARS_FINISHED, names=AVATARS_FINISHED_COLS, sep='\t'
        )
        exp = set(exp[exp['avatar'].apply(lambda x: x in avatars)]['avatar'])
    except FileNotFoundError:
        exp = set()
    opinant = avatars - esperant - exp
    print(
        f'GRUP {g}: RONDA {ronda}\n'
        f'Expulsats: {len(exp)}\n'
        f'Esperant: {len(esperant)}\n'
        f'Opinant o puntuant:'
    )
    for i, o in enumerate(opinant):
        try:
            other = pd.read_csv(
                OTHER_OPINIONS, names=OTHER_OPINIONS_COLS, sep='\t'
            )
            other = other[other['round'] == ronda-1]
            other = other[other['group'] == g]
            other = other[other['subject'] == o]
        except FileNotFoundError:
            other = set()
        print(
            f'{i+1}. {len(other)}/{len(anterior)-1} companys puntuats per {o}'
        )
    print()


@click.command()
@click.argument('config_file', type=click.File())
def main(config_file):
    avatars = json.load(config_file)['avatars']
    groups = {g+1: set(a) for g, a in enumerate(avatars)}
    for g, a in groups.items():
        group_status(g, a)


if __name__ == '__main__':
    main()
