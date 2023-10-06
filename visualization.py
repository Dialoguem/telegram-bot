import json
import os.path
import subprocess

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


OWN_OPINIONS = 'data/own_opinions.csv'
OWN_OPINIONS_COLS = ['round', 'avatar', 'group', 'opinion', 'rating']
OTHER_OPINIONS = 'data/other_opinions.csv'
OTHER_OPINIONS_COLS = ['round', 'subject', 'object', 'rating', 'compromise']


def draw_avatar(ax, im, **kwargs):
    a = AnnotationBbox(im, boxcoords='offset points', frameon=False, **kwargs)
    ax.add_artist(a)


def draw_avatars(ax, avatars):
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    imgs = [text2img(t.get_text(), avatars) for t in ax.xaxis.get_ticklabels()]
    ax.set_xticklabels([' ' for _ in imgs])
    ax.set_yticklabels([' ' for _ in imgs])

    size = plt.rcParams['font.size']
    tick = ax.yaxis.get_major_ticks()[0]
    pad = tick.get_pad() + tick.get_tick_padding() + size/2
    for i, img in enumerate(imgs):
        img = OffsetImage(img, zoom=size/len(img))
        draw_avatar(ax, img, xy=(0, i+0.5), xybox=(-pad, 0))
        draw_avatar(ax, img, xy=(i+0.5, 0), xybox=(0, pad))


def get_pivot(own, other, round):
    other = other[other['round'] == round]
    own = own[own['round'] == round].copy()
    own['subject'] = own['avatar']
    own['object'] = own['avatar']
    other = pd.concat([own, other])
    return other.pivot(index='object', columns='subject', values='rating')


def plot_ratings(own, other, avatars, round):
    ax = sns.heatmap(
        get_pivot(own, other, round),
        cmap=sns.color_palette('YlGnBu', 10),
        annot=True, cbar=False
    )
    draw_avatars(ax, avatars)
    plt.savefig(f'fig/ratings_{round}.pdf', bbox_inches='tight')


def text2img(text, avatars):
    img = avatars[text].encode('unicode_escape').decode('utf-8')[-5:]
    return plt.imread(f'72x72/{img}.png')


@click.command()
@click.argument('avatars', type=click.File())
def main(avatars):
    avatars = {k: v for d in json.load(avatars) for k, v in d.items()}
    if not os.path.isdir('72x72'):
        url = 'https://codeload.github.com/twitter/twemoji/tar.gz/master'
        p = subprocess.Popen(['curl', url], stdout=subprocess.PIPE)
        c = ['tar', '-xz', '--strip=2', 'twemoji-master/assets/72x72']
        subprocess.Popen(c, stdin=p.stdout).communicate()

    other = pd.read_csv(OTHER_OPINIONS, names=OTHER_OPINIONS_COLS)
    own = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS)

    rounds = set(other['round'])
    for r in rounds:
        plot_ratings(own, other, avatars, r)


if __name__ == '__main__':
    main()
