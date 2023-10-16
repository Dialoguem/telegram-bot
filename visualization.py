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
OWN_OPINIONS_COLS = ['round', 'avatar', 'group', 'opinion', 'rating']
OTHER_OPINIONS = 'data/other_opinions.csv'
OTHER_OPINIONS_COLS = ['round', 'subject', 'object', 'rating', 'compromise']

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
            color = (1-color, 1-color, 1) if o2 > o1 else (1, 1-color, 1-color)
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
    sns.stripplot(
        data=compr[compr < own1], x='rating', y='avatar',
        color='red', marker='X',
        label='Mean of compromiseble opinions (if it is on the left)'
    )
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
    mi = min(rating, compr.min()) - 0.5
    ma = max(rating, compr.max()) + 0.5
    plt.clf()
    ax = plt.subplot()
    drawn = []
    for a, r in ratings.items():
        if r < ma and r > mi:
            size = plt.rcParams['font.size']
            height = len([d for d in drawn if d == r]) * size
            draw_avatar(ax, a, size, xy=(r, 0), xybox=(0, height))
            drawn += [r]
    for c in compr:
        center = ((rating+c)/2, 0)
        diameter = abs(c-rating)
        ax.add_patch(Arc(
            center, diameter, diameter, theta1=0, theta2=180,
            linestyle='--', edgecolor='grey'
        ))
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


def get_data(round):
    own = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS, sep='\t')
    other = pd.read_csv(OTHER_OPINIONS, names=OTHER_OPINIONS_COLS, sep='\t')
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
    return other


def get_pivot(x, values, order):
    x = x.pivot(index='object', columns='subject', values=values)
    x = x.reindex(order, axis=0)
    x = x.reindex(order, axis=1)
    x.index.name = 'object'
    x.columns.name = 'subject'
    return x


def plot_egonet_mean(ratings, compr, order, round, avatar):
    try:
        ratings = get_mean(ratings, order)['rating']
        compr = compr[avatar]
        egoplot(ratings, compr, avatar)
        plt.xlabel('Mean of ratings')
        plt.savefig(
            f'fig/egonet_mean_{round}_{avatar}.pdf', bbox_inches='tight'
        )
    except (ValueError, KeyError):
        return


def plot_egonet_subjective(ratings, compr, round, avatar):
    try:
        ratings = ratings[avatar]
        compr = compr[avatar]
        egoplot(ratings, compr, avatar)
        plt.xlabel(f'Rating given by {avatar}')
        plt.savefig(
            f'fig/egonet_subj_{round}_{avatar}.pdf', bbox_inches='tight'
        )
    except (ValueError, KeyError):
        return


def plot_graph(ratings, compr, order, round):
    ratings = get_mean(ratings, order)
    graphplot(ratings, compr)
    plt.xlabel('Mean of ratings')
    plt.savefig(f'fig/graph_{round}.pdf', bbox_inches='tight')


def plot_moves_mean(ratings1, compr1, ratings2, compr2, order, round):
    ratings1 = get_mean(ratings1, order)
    ratings2 = get_mean(ratings2, order)
    ratings1 = pd.DataFrame({a: ratings1['rating'] for a in order}, order)
    ratings2 = pd.DataFrame({a: ratings2['rating'] for a in order}, order)
    ratings1, compr1 = get_mask(ratings1, compr1, order)
    ratings2, _ = get_mask(ratings2, compr2, order)
    arrowplot(ratings1, ratings2, compr1, order)
    plt.xlabel('Mean of ratings')
    plt.savefig(f'fig/moves_mean_{round}.pdf', bbox_inches='tight')


def plot_moves_subjective(ratings1, compr1, ratings2, compr2, order, round):
    ratings1, compr1 = get_mask(ratings1, compr1, order)
    ratings2, _ = get_mask(ratings2, compr2, order)
    arrowplot(ratings1, ratings2, compr1, order)
    plt.xlabel('Rating given by self')
    plt.savefig(f'fig/moves_subj_{round}.pdf', bbox_inches='tight')


def plot_ratings(ratings, round):
    plt.clf()
    ax = sns.heatmap(
        ratings,
        cmap=sns.color_palette('YlGnBu', 11), vmin=0, vmax=10,
        annot=True, cbar=False
    )
    draw_avatars(ax, x=True, pos=0.5)
    plt.savefig(f'fig/ratings_{round}.pdf', bbox_inches='tight')


def plot_ratings_diff(ratings, round):
    plt.clf()
    ax = sns.heatmap(
        ratings.sub(np.diag(ratings), axis=0),
        cmap=sns.color_palette('coolwarm', 21), vmin=-10, vmax=10,
        annot=True, cbar=False
    )
    draw_avatars(ax, x=True, pos=0.5)
    plt.savefig(f'fig/ratings_diff_{round}.pdf', bbox_inches='tight')


def plot_round(round):
    ratings, compr, order = get_data(round)

    plot_ratings(ratings, round)
    plot_ratings_diff(ratings, round)
    plot_graph(ratings, compr, order, round)
    if round > 1:
        ratings1, compr1, _ = get_data(round-1)
        plot_moves_subjective(ratings1, compr1, ratings, compr, order, round)
        plot_moves_mean(ratings1, compr1, ratings, compr, order, round)
    for avatar in config['emojis']:
        plot_egonet_subjective(ratings, compr, round, avatar)
        plot_egonet_mean(ratings, compr, order, round, avatar)


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
        plot_round(r)


if __name__ == '__main__':
    main()
