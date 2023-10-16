#!/usr/bin/env python

import json
import os.path
import subprocess

import click


@click.command()
@click.argument('config_file', type=click.File())
def main(config_file):
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

    for e in config['emojis']:
        im = config['emojis'][e].encode('unicode_escape').decode('utf-8')[-5:]
        im = f'72x72/{im}.png'
        if not os.path.isfile(im):
            print(f'{e} not found')


if __name__ == '__main__':
    main()
