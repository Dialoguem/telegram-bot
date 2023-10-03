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
    'AVATAR', 'OPINE', 'RATE_OWN', 'SHOW', 'COMPROMISE', 'CHANGE'
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
    chat_id = update.effective_chat.id
    avatar = context.user_data['avatar']
    group = context.user_data['group']
    opinion = context.user_data['opinion']
    rating = update.callback_query.data

    path = CSV_FILE_PATH.format(context.user_data['round'])
    with open(path, 'a') as csvfile:
        csv.writer(csvfile).writerow([avatar, group, opinion, rating])

    await context.bot.send_message(chat_id=chat_id, text=(
        'Thank you for providing your opinion! '
        'They have been recorded and '
        'will be shown anonymously to the rest of the assembly. '
        'Now please await instructions from the human facilitators.'
    ))
    return State.SHOW


async def show(update, context):
    participants = click.get_current_context().params['participants']
    chat_id = update.effective_chat.id

    path = CSV_FILE_PATH.format(context.user_data['round'])
    with open(path, 'r') as csv_file:
        num_lines = len(csv_file.readlines())

    if num_lines < participants:
        message = 'Please wait, the opinions will be available soon.'
        await context.bot.send_message(chat_id=chat_id, text=message)
        return State.SHOW
    else:
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                inline_keyboard = [
                    [
                        InlineKeyboardButton(
                            str(i), callback_data=f'{row[0]},{row[3]},{i}'
                        )
                        for i in range(6)
                    ],
                    [
                        InlineKeyboardButton(
                            str(i), callback_data=f'{row[0]},{row[3]},{i}'
                        )
                        for i in range(6, 11)
                    ],
                    [
                        InlineKeyboardButton(
                            'Yes', callback_data=f'{row[0]},{row[3]},yes'
                        ),
                        InlineKeyboardButton(
                            'No', callback_data=f'{row[0]},{row[3]},no'
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(inline_keyboard)

                avatar, group, answer_1, _ = row

                if (avatar != context.user_data['avatar']
                        and int(group) == int(context.user_data['group'])):
                    message = (
                        f'{avatar} said {answer_1}\n'
                        'Please provide an evaluation betwee 0 and 10 of '
                        'this opinion and indicate if you would be willing '
                        'to compromise with it:'
                    )
                    await context.bot.send_message(
                        chat_id=chat_id, text=message,
                        reply_markup=reply_markup
                    )
        return State.COMPROMISE


async def compromise(update, context):
    participants = click.get_current_context().params['participants']
    query = update.callback_query
    data = query.data.split(',')

    # Extract the data from the callback data
    column1 = data[0]
    column2 = data[1]
    answer = data[2]

    # Save the selected values in a separate CSV file
    h = context.user_data['avatar']
    r = context.user_data['round']
    if not os.path.isdir(f'data/round_{r}'):
        subprocess.run(['mkdir', f'data/round_{r}'])
    ans_int = f'data/round_{r}/{h}.csv'
    ans_bool = f'data/round_{r}/{h}_answer.csv'
    if answer.isdigit() and int(answer) >= 0 and int(answer) <= 10:
        with open(ans_int, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([column1, column2, answer])
    elif answer.lower() in ['yes', 'no']:
        # Save the yes/no answer in a separate CSV file
        with open(ans_bool, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([column1, column2, answer])
        await query.message.edit_reply_markup(reply_markup=None)
    # Remove the inline keyboard from the original message

    try:
        with open(ans_int) as f:
            ans_int = len(f.readlines())
    except FileNotFoundError:
        ans_int = 0
    try:
        with open(ans_bool) as f:
            ans_bool = len(f.readlines())
    except FileNotFoundError:
        ans_bool = 0
    if ans_int < participants - 1 or ans_bool < participants - 1:
        return State.COMPROMISE
    else:
        context.user_data['round'] += 1
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Do you want to change your opinion?',
            reply_markup=options_markup(['Yes', 'No'])
        )
        return State.CHANGE


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
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                'Okay, you want to keep the same opinion\\. '
                'Now provide an integer number between 0 and 10 '
                'describing your opinion, '
                'where *0 represents* the belief that environmental concerns '
                'are overblown, while *10 indicates* the belief that extreme, '
                'radical changes to our event formats are urgent and '
                'necessary\\.\n\n'
            ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return State.RATE_OWN


# Handler for handling unknown commands
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
            State.SHOW: [CommandHandler('show_opinions', show)],
            State.COMPROMISE: [CallbackQueryHandler(compromise)],
            State.CHANGE: [CallbackQueryHandler(change)]
        },
        fallbacks=[]
    ))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()


if __name__ == '__main__':
    main()
