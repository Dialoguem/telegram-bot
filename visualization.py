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

config = dict()


def draw_avatar(ax, im, **kwargs):
    a = AnnotationBbox(im, boxcoords='offset points', frameon=False, **kwargs)
    ax.add_artist(a)


def draw_avatars(ax):
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    imgs = [text2img(t.get_text()) for t in ax.xaxis.get_ticklabels()]
    ax.set_xticklabels([' ' for _ in imgs])
    ax.set_yticklabels([' ' for _ in imgs])

    size = plt.rcParams['font.size']
    tick = ax.yaxis.get_major_ticks()[0]
    pad = tick.get_pad() + tick.get_tick_padding() + size/2
    for i, img in enumerate(imgs):
        img = OffsetImage(img, zoom=size/len(img))
        draw_avatar(ax, img, xy=(0, i+0.5), xybox=(-pad, 0))
        draw_avatar(ax, img, xy=(i+0.5, 0), xybox=(0, pad))


def get_pivot(round):
    other = pd.read_csv(OTHER_OPINIONS, names=OTHER_OPINIONS_COLS, sep='\t')
    other = other[other['round'] == round]
    own = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS, sep='\t')
    own = own[own['round'] == round].copy()
    own['subject'] = own['avatar']
    own['object'] = own['avatar']
    other = pd.concat([own, other])
    return other.pivot(index='object', columns='subject', values='rating')


def plot_ratings(round):
    ax = sns.heatmap(
        get_pivot(round),
        cmap=sns.color_palette('YlGnBu', 10),
        annot=True, cbar=False
    )
    draw_avatars(ax)
    plt.savefig(f'fig/ratings_{round}.pdf', bbox_inches='tight')


def text2img(text):
    img = config['emojis'][text].encode('unicode_escape').decode('utf-8')[-5:]
    return plt.imread(f'72x72/{img}.png')


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
        plot_ratings(r)


if __name__ == '__main__':
    main()
