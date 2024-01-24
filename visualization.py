#!/usr/bin/env python

import json
import os.path
import subprocess

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Arc


OWN_OPINIONS = 'data/own_opinions.csv'
OWN_OPINIONS_COLS = ['round', 'group', 'avatar', 'opinion', 'rating']
OTHER_OPINIONS = 'data/other_opinions.csv'
OTHER_OPINIONS_COLS = [
    'round', 'group', 'subject', 'object', 'rating', 'compromise'
]

config = dict()


def arrowplot(own1, own2, compr, order):
    plt.clf()
    ax = sns.stripplot(
        data=own1, x='rating', y='avatar', color='black',
        label='Own opinion'
    )
    for i, (o1, o2) in enumerate(zip(own1['rating'], own2['rating'])):
        if not np.isnan(o1) and not np.isnan(o2) and o2 != o1:
            absmax = max((own2['rating']-own1['rating']).dropna().apply(abs))
            color = 0.2 + 0.8*abs(o2-o1)/absmax
            if o2 > o1:
                color = (round(1-color, 4), round(1-color, 4), 1)
            else:
                color = (1, round(1-color, 4), round(1-color, 4))
            plt.arrow(
                o1, i, o2-o1, 0, ec=color,
                linewidth=2, head_width=0.1, head_length=0.05
            )
    plt.scatter(
        [], [], marker=r'$\leftarrow$', color='red', s=100,
        label='Own opinion change to the left'
    )
    plt.scatter(
        [], [], marker=r'$\rightarrow$', color='blue', s=100,
        label='Own opinion change to the right'
    )

    sns.stripplot(
        data=compr, x='rating', y='subject',
        color='black', marker='x', linewidth=0.5, size=4, jitter=False,
        label='Compromiseble opinion'
    )

    compr = compr[['rating', 'subject']].groupby('subject').mean()
    compr = compr.reindex(order)
    if not all(compr[compr < own1]['rating'].isna()):
        sns.stripplot(
            data=compr[compr < own1], x='rating', y='avatar',
            color='red', marker='X',
            label='Mean of compromiseble opinions (if it is on the left)'
        )
    if not all(compr[compr > own1]['rating'].isna()):
        sns.stripplot(
            data=compr[compr > own1], x='rating', y='avatar',
            color='blue', marker='X',
            label='Mean of compromiseble opinions (if it is on the right)'
        )

    handles, labels = ax.get_legend_handles_labels()
    handles, labels = zip(*[
        (h, l) for i, (h, l) in enumerate(zip(handles, labels))
        if l not in labels[:i]
    ])
    plt.legend(handles, labels, bbox_to_anchor=(0.5, -0.1), loc='upper center')

    draw_avatars(ax)
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.xlim(0, 10)
    plt.xticks(range(0, 11))
    plt.ylabel('')


def egoplot(ratings, compr, avatar):
    compr = ratings.mask(compr != 'Yes').dropna()
    rating = ratings[avatar]
    plt.clf()
    ax = plt.subplot()
    drawn = []
    for a, r in ratings.items():
        size = plt.rcParams['font.size']
        height = len([d for d in drawn if d == r]) * size
        if a != avatar and a not in compr:
            size /= 2
        draw_avatar(ax, a, size, xy=(r, 0), xybox=(0, height))
        drawn += [r]
    for c in compr:
        center = ((rating+c)/2, 0)
        diameter = abs(c-rating)
        ax.add_patch(Arc(
            center, diameter, diameter, theta1=0, theta2=180,
            linestyle='--', edgecolor='grey'
        ))
    mi = ratings.min() - 0.5
    ma = ratings.max() + 0.5
    plt.xlim(mi, ma)
    plt.ylim(0, (ma-mi)/2)
    plt.yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)


def graphplot(ratings, compr):
    compr = compr.stack().reset_index()
    compr = compr[compr[0] == 'Yes']
    ratings = ratings['rating']
    plt.clf()
    ax = plt.subplot()
    for a, r in ratings.items():
        draw_avatar(ax, a, xy=(r, 0), xybox=(0, 0))
    for _, c in compr.iterrows():
        subj = ratings[c['subject']]
        obj = ratings[c['object']]
        center = ((subj+obj)/2, 0)
        diameter = abs(subj-obj)
        if obj > subj:
            ax.add_patch(Arc(
                center, diameter, diameter, theta1=0, theta2=180, color='blue'
            ))
        else:
            ax.add_patch(Arc(
                center, diameter, diameter, theta1=180, theta2=360, color='red'
            ))
    plt.scatter(
        [], [], marker=r'$\leftarrow$', color='red', s=100,
        label='Compromise to the left'
    )
    plt.scatter(
        [], [], marker=r'$\rightarrow$', color='blue', s=100,
        label='Compromise to the right'
    )
    plt.legend(bbox_to_anchor=(0.5, 0), loc='upper center')
    lim = (ratings.max()-ratings.min()) / 2
    plt.ylim(-lim, lim)
    plt.xlim(ratings.min()-0.5, ratings.max()+0.5)
    plt.axis('off')


def draw_avatar(ax, im, size=plt.rcParams['font.size'], **kwargs):
    im = config['emojis'][im].encode('unicode_escape').decode('utf-8')[-5:]
    im = plt.imread(f'72x72/{im}.png')
    im = OffsetImage(im, zoom=size/len(im))
    a = AnnotationBbox(im, boxcoords='offset points', frameon=False, **kwargs)
    ax.add_artist(a)


def draw_avatars(ax, x=False, pos=0.0):
    if x:
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

    ticks = [t.get_text() for t in ax.yaxis.get_ticklabels()]
    ax.set_yticklabels(['   ' for _ in ticks])
    if x:
        ax.set_xticklabels(['   ' for _ in ticks])

    size = plt.rcParams['font.size']
    tick = ax.yaxis.get_major_ticks()[0]
    pad = tick.get_pad() + tick.get_tick_padding() + size/2
    for i, t in enumerate(ticks):
        draw_avatar(ax, t, size, xy=(0, i+pos), xybox=(-pad, 0))
        if x:
            draw_avatar(ax, t, size, xy=(i+pos, 0), xybox=(0, pad))


def get_compr(other, order, round):
    other = other[other['round'] == round]
    other = get_pivot(other, 'compromise', order)
    return other


def get_data(round, group):
    own = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS, sep='\t')
    other = pd.read_csv(OTHER_OPINIONS, names=OTHER_OPINIONS_COLS, sep='\t')
    own = own[own['group'] == group]
    other = other[other['group'] == group]
    order = get_order(own)
    ratings = get_ratings(own, other, order, round)
    compr = get_compr(other, order, round)
    return ratings, compr, order


def get_mask(ratings, compr, order):
    compr = ratings.mask(compr != 'Yes')
    compr = compr.stack().reset_index()
    compr.columns = ['object', 'subject', 'rating']
    ratings = pd.DataFrame({'rating': np.diag(ratings)}, index=order)
    return ratings, compr


def get_mean(ratings, order):
    ratings = ratings.stack().reset_index()
    ratings.columns = ['object', 'subject', 'rating']
    ratings = ratings[['rating', 'object']].groupby('object').mean()
    ratings.reindex(order)
    return ratings


def get_order(own):
    own = own[own['round'] == 1]
    own = own.sort_values('rating', ascending=False)
    return own['avatar']


def get_ratings(own, other, order, round):
    other = other[other['round'] == round]
    own = own[own['round'] == round].copy()
    own['subject'] = own['avatar']
    own['object'] = own['avatar']
    other = pd.concat([own, other])
    other = get_pivot(other, 'rating', order)
    other = other.applymap(float)
    return other


def get_pivot(x, values, order):
    x = x.pivot(index='object', columns='subject', values=values)
    x = x.reindex(order, axis=0)
    x = x.reindex(order, axis=1)
    x.index.name = 'object'
    x.columns.name = 'subject'
    return x


def plot_egonet_mean(ratings, compr, order, round, group, avatar):
    try:
        ratings = get_mean(ratings, order)['rating']
        compr = compr[avatar]
        egoplot(ratings, compr, avatar)
        plt.title(
            'Egonetwork of compromises '
            f'(round {round}, group {group}, {avatar})\n'
            'with non compromisable opinions depicted smaller'
        )
        plt.xlabel('Mean of ratings')
        savefig(f'egonet_mean_{round}_{group}_{avatar}')
    except (ValueError, KeyError):
        return


def plot_egonet_subjective(ratings, compr, round, group, avatar):
    try:
        ratings = ratings[avatar]
        compr = compr[avatar]
        egoplot(ratings, compr, avatar)
        plt.title(
            'Egonetwork of compromises '
            f'(round {round}, group {group}, {avatar})\n'
            'with non compromisable opinions depicted smaller'
        )
        plt.xlabel(f'Rating given by {avatar}')
        savefig(f'egonet_subj_{round}_{group}_{avatar}')
    except (ValueError, KeyError):
        return


def plot_graph(ratings, compr, order, round, group):
    ratings = get_mean(ratings, order)
    graphplot(ratings, compr)
    plt.title(f'Graph of compromises (round {round}, group {group})')
    savefig(f'graph_{round}_{group}')


def plot_moves_mean(ratings1, compr1, ratings2, compr2, order, round, group):
    ratings1 = get_mean(ratings1, order)
    ratings2 = get_mean(ratings2, order)
    ratings1 = pd.DataFrame({a: ratings1['rating'] for a in order}, order)
    ratings2 = pd.DataFrame({a: ratings2['rating'] for a in order}, order)
    ratings1, compr1 = get_mask(ratings1, compr1, order)
    ratings2, _ = get_mask(ratings2, compr2, order)
    arrowplot(ratings1, ratings2, compr1, order)
    plt.title(f'Opinion movements (rounds {round-1}-{round}, group {group})')
    plt.xlabel('Mean of ratings')
    savefig(f'moves_mean_{round}_{group}')


def plot_moves_subj(ratings1, compr1, ratings2, compr2, order, round, group):
    ratings1, compr1 = get_mask(ratings1, compr1, order)
    ratings2, _ = get_mask(ratings2, compr2, order)
    arrowplot(ratings1, ratings2, compr1, order)
    plt.title(f'Opinion movements (rounds {round-1}-{round}, group {group})')
    plt.xlabel('Rating given by avatar')
    plt.ylabel('Avatar')
    savefig(f'moves_subj_{round}_{group}')


def plot_ratings(ratings, round, group):
    plt.clf()
    ax = sns.heatmap(
        ratings,
        cmap=sns.color_palette('YlGnBu', 11), vmin=0, vmax=10,
        annot=True, cbar=False
    )
    draw_avatars(ax, x=True, pos=0.5)
    ax.set_aspect('equal')
    plt.title(
        "Rating of object's opinion given by subject\n"
        f'(round {round}, group {group})'
    )
    savefig(f'ratings_{round}_{group}')


def plot_ratings_diff(ratings, round, group):
    plt.clf()
    ax = sns.heatmap(
        ratings.sub(np.diag(ratings), axis=0),
        cmap=sns.color_palette('coolwarm', 21), vmin=-10, vmax=10,
        annot=True, cbar=False
    )
    draw_avatars(ax, x=True, pos=0.5)
    plt.title(
        'Difference between rating\ngiven by subject and given by object\n'
        "of object's opinion "
        f'(round {round}, group {group})'
    )
    ax.set_aspect('equal')
    savefig(f'ratings_diff_{round}_{group}')


def plot_round(round, group):
    ratings, compr, order = get_data(round, group)

    plot_ratings(ratings, round, group)
    plot_ratings_diff(ratings, round, group)
    plot_graph(ratings, compr, order, round, group)
    if round > 1:
        ratings1, compr1, _ = get_data(round-1, group)
        plot_moves_subj(ratings1, compr1, ratings, compr, order, round, group)
        plot_moves_mean(ratings1, compr1, ratings, compr, order, round, group)
    for avatar in config['emojis']:
        plot_egonet_subjective(ratings, compr, round, group, avatar)
        plot_egonet_mean(ratings, compr, order, round, group, avatar)


def savefig(name):
    plt.savefig(f'fig/{name}.pdf', bbox_inches='tight', dpi=1000)
    plt.savefig(f'fig/{name}.png', bbox_inches='tight', dpi=1000)


@click.command()
@click.argument('config_file', type=click.File())
def main(config_file):
    global config
    config = json.load(config_file)
    config['emojis'] = {
        avatar: emoji
        for group in config['avatars']
        for avatar, emoji in group.items()
    }

    if not os.path.isdir('72x72'):
        url = 'https://codeload.github.com/twitter/twemoji/tar.gz/master'
        p = subprocess.Popen(['curl', url], stdout=subprocess.PIPE)
        c = ['tar', '-xz', '--strip=2', 'twemoji-master/assets/72x72']
        subprocess.Popen(c, stdin=p.stdout).communicate()

    other = pd.read_csv(OTHER_OPINIONS, names=OTHER_OPINIONS_COLS, sep='\t')
    rounds = set(other['round'])
    for r in rounds:
        groups = set(other[other['round'] == r]['group'])
        for g in groups:
            plot_round(r, g)


if __name__ == '__main__':
    main()
