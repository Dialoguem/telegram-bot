import csv
import enum
import logging
import os.path
import subprocess

import click
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler
)
from telegram.constants import ParseMode


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CSV_FILE_PATH = 'data/answers_round_{0}.csv'

avatar_groups = {
    'asparagus': 1, 'artichoke': 1, 'beet': 1, 'broccoli': 1, 'celery': 1,
    'couliflower': 1, 'eggplant': 1, 'garlic': 1, 'green beans': 1,
    'lettuce': 1, 'onion': 1, 'potato': 1, 'peas': 1, 'pepper': 1,
    'pumpkin': 1, 'radish': 1, 'squash': 1, 'sweet potato': 1, 'tomato': 1,
    'turnip': 1,
    'apple': 2, 'avocado': 2, 'banana': 2, 'blueberry': 2, 'cherry': 2,
    'coconut': 2, 'grape': 2, 'kiwi': 2, 'lemon': 2, 'mango': 2, 'melon': 2,
    'orange': 2, 'peach': 2, 'pear': 2, 'pineapple': 2, 'red apple': 2,
    'strawberry': 2, 'watermelon': 2,
    'bear': 3, 'bee': 3, 'butterfly': 3, 'cat': 3, 'cow': 3, 'crocodile': 3,
    'dog': 3, 'dolphin': 3, 'elephant': 3, 'fox': 3, 'frog': 3, 'giraffe': 3,
    'goat': 3, 'hedgehog': 3, 'lion': 3, 'monkey': 3, 'octopus': 3,
    'penguin': 3, 'sheep': 3, 'snake': 3, 'tiger': 3, 'turtle': 3
}

State = enum.Enum('State', [
    'AVATAR', 'OPINE', 'RATE_OWN', 'SHOW', 'RATE_OTHER', 'COMPROMISE', 'CHANGE'
])


def options_markup(options, options_per_row=None):
    o = [InlineKeyboardButton(o, callback_data=o) for o in options]
    if options_per_row is None:
        options_per_row = len(o)
    o = [o[i:i+options_per_row] for i in range(0, len(o), options_per_row)]
    return InlineKeyboardMarkup(o)


async def dialoguem(update, context):
    user = update.message.from_user
    context.user_data['round'] = 1
    await update.message.reply_text(
        f'Hello, {user.first_name}\\! '
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
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=options_markup(avatar_groups.keys(), options_per_row=5)
    )
    return State.AVATAR


async def avatar(update, context):
    chat_id = update.effective_chat.id
    avatar = update.callback_query.data
    context.user_data['avatar'] = avatar
    context.user_data['group'] = avatar_groups[avatar]
    await context.bot.send_message(chat_id=chat_id, text=(
        'As a participant in this discussion, you are encouraged to share '
        'your thoughts on an increasingly important topic: the '
        'environmental impact of academic events, such as schools and '
        'conferences.\n\n'
        'On one side of the debate, some may argue that environmental '
        'concerns are being overemphasized, possibly affecting the '
        'overall experience of such events. They might suggest that '
        'options like vegetarian meals and wooden utensils are '
        'unnecessary measures.\n\n'
        'On the other end of the spectrum, some argue for drastic and '
        'immediate overhaul of our traditional academic event formats, '
        'advocating for a nearly complete shift to online formats and '
        'significantly reduced event frequency, emphasizing that if the '
        "scientific community doesn't take radical steps towards "
        'environmental responsibility, who will?\n\n'
        'In the middle, there are also considerations of the '
        'post-pandemic reality and the importance of in-person '
        'networking for early-career researchers, as well as the '
        'potential mental health implications of limiting such '
        'opportunities.\n\n'
        'Please, write a short message describing '
        'your opinion about the topic.'
    ))
    return State.OPINE


async def opine(update, context):
    context.user_data['opinion'] = update.message.text.strip()
    await update.message.reply_text(
        'Okay\\. Now provide an integer number between 0 and 10 '
        'describing your opinion, '
        'where *0 represents* the belief that environmental concerns '
        'are overblown, while *10 indicates* the belief that extreme, '
        'radical changes to our event formats are urgent and '
        'necessary\\.\n\n'
        'Remember, this is a spectrum\\. '
        'All shades of opinion are welcome\\!\n\n',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=options_markup(range(11), options_per_row=6)
    )
    return State.RATE_OWN


async def rate_own(update, context):
    avatar = context.user_data['avatar']
    group = context.user_data['group']
    opinion = context.user_data['opinion']
    rating = update.callback_query.data

    path = CSV_FILE_PATH.format(context.user_data['round'])
    with open(path, 'a') as csvfile:
        csv.writer(csvfile).writerow([avatar, group, opinion, rating])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Thank you for providing your opinion! '
            'They have been recorded and '
            'will be shown anonymously to the rest of the assembly.'
        ),
        reply_markup=options_markup(['Show opinions of other participants'])
    )
    return State.SHOW


async def show(update, context):
    with open(CSV_FILE_PATH.format(context.user_data['round'])) as f:
        opinions = len(f.readlines())
    participants = click.get_current_context().params['participants']
    if opinions < participants:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Opinions are not available yet. Please try again later.',
            reply_markup=options_markup(['Show opinions'])
        )
        return State.SHOW
    else:
        return await show_next(update, context)


async def show_next(update, context):
    round = context.user_data['round']
    avatar = context.user_data['avatar']
    group = context.user_data['group']
    with open(CSV_FILE_PATH.format(round)) as f:
        opinions = f.readlines()
    try:
        with open(f'data/round_{round}/{avatar}.csv') as f:
            rated = len(f.readlines())
    except FileNotFoundError:
        rated = 0
    opinions = [
        (a, o) for a, g, o, _ in csv.reader(opinions)
        if a != avatar and int(g) == group
    ]
    if rated < len(opinions):
        avatar, opinion = opinions[rated]
        context.user_data['rated'] = avatar
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f'{avatar} said:\n\n'
                f'{opinion}\n\n'
                'Please provide a rating between 0 and 10 of this opinion:'
            ),
            reply_markup=options_markup(range(11), options_per_row=6)
        )
        return State.RATE_OTHER
    else:
        context.user_data['round'] += 1
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Do you want to change your opinion and its rating?',
            reply_markup=options_markup(['Yes', 'No'])
        )
        return State.CHANGE


async def rate_other(update, context):
    chat_id = update.effective_chat.id
    round = context.user_data['round']
    avatar = context.user_data['avatar']
    rated = context.user_data['rated']
    rating = update.callback_query.data
    if not os.path.isdir(f'data/round_{round}'):
        subprocess.run(['mkdir', f'data/round_{round}'])
    with open(f'data/round_{round}/{avatar}.csv', 'a') as f:
        csv.writer(f).writerow([rated, rating])
    await context.bot.send_message(
        chat_id=chat_id,
        text='Now indicate if you would be willing to compromise with it:',
        reply_markup=options_markup(['Yes', 'No'])
    )
    return State.COMPROMISE


async def compromise(update, context):
    round = context.user_data['round']
    avatar = context.user_data['avatar']
    rated = context.user_data['rated']
    compromise = update.callback_query.data
    with open(f'data/round_{round}/{avatar}_answer.csv', 'a') as f:
        csv.writer(f).writerow([rated, compromise])
    return await show_next(update, context)


async def change(update, context):
    chat_id = update.effective_chat.id
    change = update.callback_query.data
    if change == 'Yes':
        await context.bot.send_message(chat_id=chat_id, text=(
            'Okay. Please, write a short message describing '
            'your opinion about the topic of the assembly.'
        ))
        return State.OPINE
    else:
        return await rate_own(update, context)


async def unknown(update, _):
    await update.message.reply_text("Sorry, I didn't understand that command.")


@click.command()
@click.argument('token')
@click.argument('participants', type=click.IntRange(0, (len(avatar_groups))))
def main(token, participants):
    app = ApplicationBuilder().token(token).build()

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('dialoguem', dialoguem)],
        states={
            State.AVATAR: [CallbackQueryHandler(avatar)],
            State.OPINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, opine)
            ],
            State.RATE_OWN: [CallbackQueryHandler(rate_own)],
            State.SHOW: [CallbackQueryHandler(show)],
            State.RATE_OTHER: [CallbackQueryHandler(rate_other)],
            State.COMPROMISE: [CallbackQueryHandler(compromise)],
            State.CHANGE: [CallbackQueryHandler(change)]
        },
        fallbacks=[]
    ))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()


if __name__ == '__main__':
    main()
