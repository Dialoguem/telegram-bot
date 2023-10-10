import csv
import enum
import json
import warnings

import click
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler,
    ConversationHandler, filters, MessageHandler
)
from telegram.warnings import PTBUserWarning


warnings.filterwarnings(
    action='ignore', message=r'.*CallbackQueryHandler', category=PTBUserWarning
)

OWN_OPINIONS = 'data/own_opinions.csv'
OWN_OPINIONS_COLS = ['round', 'avatar', 'group', 'opinion', 'rating']
OTHER_OPINIONS = 'data/other_opinions.csv'
OTHER_OPINIONS_COLS = ['round', 'subject', 'object', 'rating', 'compromise']

config = dict()

State = enum.Enum('State', [
    'AVATAR', 'OPINE', 'RATE_OWN', 'SHOW', 'RATE_OTHER', 'COMPROMISE',
    'CHANGE', 'END'
])


def options_markup(options, options_per_row=None):
    o = [InlineKeyboardButton(o, callback_data=o) for o in options]
    if options_per_row is None:
        options_per_row = len(o)
    o = [o[i:i+options_per_row] for i in range(0, len(o), options_per_row)]
    return InlineKeyboardMarkup(o)


async def start(update, context):
    context.user_data['round'] = 1
    await update.message.reply_text(
        f'Hello, {update.message.from_user.first_name}\\! '
        'Welcome to the blind assembly *Dialoguem*\\.\n\n'
        'By participating in this social experiment and using the '
        'associated application, you are giving your informed consent for '
        'the collection and usage of your anonymized data for research '
        'purposes\\. We do not collect any personal information during '
        'this process\\. Your privacy and data protection are our top '
        'priorities, and we are committed to adhering to the principles '
        'outlined in the General Data Protection Regulation \\(GDPR\\)\\.'
        '\n\n'
        'The data collected will be used solely for academic research and '
        'will be anonymized to ensure your identity remains '
        'confidential\\.\n\n'
        'If you have any concerns or questions about data usage, please '
        'feel free to contact us\\. We appreciate your participation and '
        'trust in our research endeavor\\.\n\n',
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await update.message.reply_text(
        'Please enter the *avatar* that has been assigned to you, in this '
        'way you will be anonymous throughout the process:',
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return State.AVATAR


async def avatar(update, context):
    avatar = update.message.text.lower().strip()
    if avatar in config['groups']:
        context.user_data['avatar'] = avatar
        context.user_data['group'] = config['groups'][avatar]
        await context.bot.send_message(
            update.effective_chat.id,
            'As a participant in this discussion, you are encouraged to share '
            'your thoughts on an increasingly important topic: '
            f'{config["title"]}\n\n'
            f'{config["description"]}\n\n'
            'Please, write a short message describing '
            'your opinion about the topic.'
        )
        return State.OPINE
    else:
        await context.bot.send_message(
            update.effective_chat.id,
            'Sorry, the avatar you have entered is not valid. '
            'Please enter a valid avatar:'
        )
        return State.AVATAR


async def opine(update, context):
    context.user_data['opinion'] = update.message.text.strip()
    await update.message.reply_text(
        'Okay. Now provide an integer number between 0 and 10 '
        'describing your opinion, '
        f'{config["scale"]}\n\n'
        'Remember, this is a spectrum. '
        'All shades of opinion are welcome!\n\n',
        reply_markup=options_markup(range(11), options_per_row=6)
    )
    return State.RATE_OWN


async def rate_own(update, context):
    await update.callback_query.edit_message_reply_markup(None)
    context.user_data['rating'] = update.callback_query.data
    return await save_own(update, context)


async def save_own(update, context):
    with open(OWN_OPINIONS, 'a') as f:
        csv.writer(f).writerow([
            context.user_data['round'],
            context.user_data['avatar'],
            context.user_data['group'],
            context.user_data['opinion'],
            context.user_data['rating'],
        ])
    await context.bot.send_message(
        update.effective_chat.id,
        'Thank you for providing your opinion! '
        'They have been recorded and '
        'will be shown anonymously to the rest of the assembly.',
        reply_markup=options_markup(['Show opinions of other participants'])
    )
    return State.SHOW


async def show(update, context):
    await update.callback_query.edit_message_reply_markup(None)
    opinions = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS)
    opinions = opinions[opinions['round'] == context.user_data['round']]
    if len(opinions) < len(config['groups']):
        await context.bot.send_message(
            update.effective_chat.id,
            'Opinions are not available yet. Please try again later.',
            reply_markup=options_markup(['Show opinions'])
        )
        return State.SHOW
    else:
        return await show_next(update, context)


async def show_next(update, context):
    opinions = pd.read_csv(OWN_OPINIONS, names=OWN_OPINIONS_COLS)
    opinions = opinions[opinions['group'] == context.user_data['group']]

    r = context.user_data['round']
    if r > 1:
        now = sorted(opinions[opinions['round'] == r]['opinion'])
        past = sorted(opinions[opinions['round'] == r-1]['opinion'])
        if now == past:
            await context.bot.send_message(
                update.effective_chat.id,
                'Nobody has changed the opinion and, therefore, '
                'the assembly has finished. '
                'Thanks for the participation!'
            )
            return State.END

    opinions = opinions[opinions['round'] == r]
    opinions = opinions[opinions['avatar'] != context.user_data['avatar']]
    try:
        rated = pd.read_csv(OTHER_OPINIONS, names=OTHER_OPINIONS_COLS)
        rated = rated[rated['round'] == context.user_data['round']]
        rated = rated[rated['subject'] == context.user_data['avatar']]
        rated = len(rated)
    except FileNotFoundError:
        rated = 0
    if rated < len(opinions):
        avatar, opinion = opinions.iloc[rated][['avatar', 'opinion']]
        context.user_data['rated'] = {'avatar': avatar}
        await context.bot.send_message(
            update.effective_chat.id,
            f'{avatar} said:\n\n'
            f'{opinion}\n\n'
            'Please provide a rating between 0 and 10 of this opinion:',
            reply_markup=options_markup(range(11), options_per_row=6)
        )
        return State.RATE_OTHER
    else:
        context.user_data['round'] += 1
        await context.bot.send_message(
            update.effective_chat.id,
            'Do you want to change your opinion and its rating?',
            reply_markup=options_markup(['Yes', 'No'])
        )
        return State.CHANGE


async def rate_other(update, context):
    await update.callback_query.edit_message_reply_markup(None)
    context.user_data['rated']['rating'] = update.callback_query.data
    await context.bot.send_message(
        update.effective_chat.id,
        'Now indicate if you would be willing to compromise with it:',
        reply_markup=options_markup(['Yes', 'No'])
    )
    return State.COMPROMISE


async def compromise(update, context):
    await update.callback_query.edit_message_reply_markup(None)
    with open(OTHER_OPINIONS, 'a') as f:
        csv.writer(f).writerow([
            context.user_data['round'],
            context.user_data['avatar'],
            context.user_data['rated']['avatar'],
            context.user_data['rated']['rating'],
            update.callback_query.data
        ])
    return await show_next(update, context)


async def change(update, context):
    await update.callback_query.edit_message_reply_markup(None)
    if update.callback_query.data == 'Yes':
        await context.bot.send_message(
            update.effective_chat.id,
            'Okay. Please, write a short message describing '
            'your opinion about the topic of the assembly.'
        )
        return State.OPINE
    else:
        return await save_own(update, context)


async def unknown(update, _):
    await update.message.reply_text("Sorry, I didn't understand that command.")


@click.command()
@click.argument('config_file', type=click.File())
def main(config_file):
    global config
    config = json.load(config_file)
    config['groups'] = {
        avatar: group
        for group, avatars in enumerate(config['avatars'])
        for avatar in avatars
    }

    app = ApplicationBuilder().token(config['token']).build()

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            State.AVATAR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, avatar)
            ],
            State.OPINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, opine)
            ],
            State.RATE_OWN: [CallbackQueryHandler(rate_own)],
            State.SHOW: [CallbackQueryHandler(show)],
            State.RATE_OTHER: [CallbackQueryHandler(rate_other)],
            State.COMPROMISE: [CallbackQueryHandler(compromise)],
            State.CHANGE: [CallbackQueryHandler(change)],
            State.END: []
        },
        fallbacks=[]
    ))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()


if __name__ == '__main__':
    main()
