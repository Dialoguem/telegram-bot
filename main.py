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

# List of allowed handles
allowed_handles_group1 = [
    'radish', 'peas', 'squash', 'sweet potato', 'pepper', 'celery', 'onion',
    'tomato', 'beet', 'artichoke', 'couliflower', 'eggplant', 'green beans',
    'turnip', 'potato', 'lettuce', 'garlic', 'pumpkin', 'asparagus', 'broccoli'
]
allowed_handles_group2 = [
    'peach', 'melon', 'grape', 'pineapple', 'banana', 'cherry', 'blueberry',
    'apple', 'red apple', 'coconut', 'lemon', 'watermelon', 'kiwi', 'pear',
    'orange', 'mango', 'strawberry', 'avocado'
]
allowed_handles_group3 = [
    'elephant', 'crocodile', 'monkey', 'octopus', 'hedgehog', 'fox', 'giraffe',
    'goat', 'cat', 'turtle', 'sheep', 'frog', 'bee', 'tiger', 'dog',
    'butterfly', 'dolphin', 'snake', 'cow', 'lion', 'bear', 'penguin'
]

State = enum.Enum(
    'State',
    ['ENTER_HANDLE', 'ANSWER_1', 'ANSWER_2', 'SHOW_ANSWERS', 'COMPROMISE']
)


# Handler for the /start command
async def start(update, context):
    user = update.message.from_user
    context.user_data['round'] = 1
    context.user_data['handle'] = None
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
        'trust in our research endeavor\\.\n\n'
        'As a participant in this discussion, you are encouraged to share '
        'your thoughts on an increasingly important topic: the '
        'environmental impact of academic events, such as schools and '
        'conferences\\.\n\n'
        'On one side of the debate, some may argue that environmental '
        'concerns are being overemphasized, possibly affecting the '
        'overall experience of such events\\. They might suggest that '
        'options like vegetarian meals and wooden utensils are '
        'unnecessary measures\\.\n\n'
        'On the other end of the spectrum, some argue for drastic and '
        'immediate overhaul of our traditional academic event formats, '
        'advocating for a nearly complete shift to online formats and '
        'significantly reduced event frequency, emphasizing that if the '
        "scientific community doesn't take radical steps towards "
        'environmental responsibility, who will?\n\n'
        'In the middle, there are also considerations of the '
        'post\\-pandemic reality and the importance of in\\-person '
        'networking for early\\-career researchers, as well as the '
        'potential mental health implications of limiting such '
        'opportunities\\.\n\n'
        "We've set up a scale from 0 to 10 for you to express your "
        'opinion: *0 represents* the belief that environmental concerns '
        'are overblown, while *10 indicates* the belief that extreme, '
        'radical changes to our event formats are urgent and '
        'necessary\\.\n\n'
        'Remember, this is a spectrum\\. '
        'All shades of opinion are welcome\\!\n\n'
        'Please enter the *avatar* that has been assigned to you, in this '
        'way you will be anonymous throughout the process:',
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return State.ENTER_HANDLE


# Handler for handling user's handle
async def enter_handle(update, context):
    handle = update.message.text.lower().strip()
    if handle in allowed_handles_group1:
        context.user_data['handle'] = handle
        context.user_data['group'] = 1
        await update.message.reply_text(
            'Great! Please, write a short message describing '
            'your attitute about the theme of the assembly. xxx:'
        )
        return State.ANSWER_1
    elif handle in allowed_handles_group2:
        context.user_data['handle'] = handle
        context.user_data['group'] = 2
        await update.message.reply_text(
            'Great! Please, write a short message describing '
            'your attitute about the theme of the assembly. xxx:'
        )
        return State.ANSWER_1
    elif handle in allowed_handles_group3:
        context.user_data['handle'] = handle
        context.user_data['group'] = 3
        await update.message.reply_text(
            'Great! Please, write a short message describing '
            'your attitute about the theme of the assembly. xxx:'
        )
        return State.ANSWER_1
    else:
        await update.message.reply_text(
            'Sorry, the avatar you have entered is not valid. '
            'Please enter a valid avatar:'
        )
        return State.ENTER_HANDLE


# Handler for handling user's first answer
async def answer_1(update, context):
    if ('answer_1' in context.user_data.keys()
            and 'keep' in update.message.text.lower().strip()
            and 'opinion' in update.message.text.lower().strip()):
        await update.message.reply_text(
            'Okay, you want to keep the same opinion, '
            'now provide an integer number between 0 and 10 '
            'describing your opinion, '
            'where 0 is completely against and 10 completely in favor:'
        )
        return State.ANSWER_2
    else:
        answer = update.message.text.strip()
        context.user_data['answer_1'] = answer
        await update.message.reply_text(
            'Okay, now provide an integer number between 0 and 10 '
            'describing your opinion, '
            'where 0 is completely against and 10 completely in favor:'
        )
        return State.ANSWER_2


# Handler for handling user's second answer
async def answer_2(update, context):
    answer = update.message.text.strip()
    if answer.isdigit() and int(answer) >= 0 and int(answer) <= 10:
        handle = context.user_data['handle']
        group = context.user_data['group']
        answer_1 = context.user_data['answer_1']

        # Save data to CSV
        path = CSV_FILE_PATH.format(context.user_data['round'])
        with open(path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([handle, group, answer_1, answer])

            await update.message.reply_text(
                'Thank you for providing your opinion! '
                'They have been recorded and '
                'will be shown anonymously to the rest of the assembly. '
                'Now please await instructions from the human facilitators.'
            )
            return State.SHOW_ANSWERS
    else:
        await update.message.reply_text(
            'Sorry, it should be an integer between 0 and 10, '
            'where 0 is completely against and 10 completely in favor:'
        )
        return State.ANSWER_2


# Handler for the /show_answers command
async def show_answers(update, context):
    participants = click.get_current_context().params['participants']
    chat_id = update.effective_chat.id

    # Check the number of lines in the CSV file
    path = CSV_FILE_PATH.format(context.user_data['round'])
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        num_lines = sum(1 for _ in csv_reader)

    if num_lines < participants:
        message = 'Please wait, the opinions will be available soon.'
        await context.bot.send_message(chat_id=chat_id, text=message)
        return State.SHOW_ANSWERS
    else:
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                inline_keyboard = []
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

                handle, group, answer_1, _ = row

                if (handle != context.user_data['handle']
                        and int(group) == int(context.user_data['group'])):
                    message = (
                        f'{handle} said {answer_1}\n'
                        'Please provide an evaluation betwee 0 and 10 of '
                        'this opinion and indicate if you would be willing '
                        'to compromise with it:'
                    )
                    await context.bot.send_message(
                        chat_id=chat_id, text=message,
                        reply_markup=reply_markup
                    )
        return State.COMPROMISE


async def handle_button_press(update, context):
    participants = click.get_current_context().params['participants']
    query = update.callback_query
    data = query.data.split(',')

    # Extract the data from the callback data
    column1 = data[0]
    column2 = data[1]
    answer = data[2]

    # Save the selected values in a separate CSV file
    h = context.user_data['handle']
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=(
            'Please update your opinion if you want, '
            'or type "keep the same opinion" if not:'
        ))
        return State.ANSWER_1


# Handler for handling unknown commands
async def unknown(update, _):
    await update.message.reply_text("Sorry, I didn't understand that command.")


@click.command()
@click.argument('token')
@click.argument('participants', type=click.IntRange(0, (
    len(allowed_handles_group1)
    + len(allowed_handles_group2)
    + len(allowed_handles_group3)
)))
def main(token, participants):
    app = ApplicationBuilder().token(token).build()

    # Define conversation handler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('dialoguem', start)],
        states={
            State.ENTER_HANDLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_handle)
            ],
            State.ANSWER_1: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, answer_1)
            ],
            State.ANSWER_2: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, answer_2)
            ],
            State.SHOW_ANSWERS: [
                CommandHandler('show_opinions', show_answers)
            ],
            State.COMPROMISE: [
                CallbackQueryHandler(handle_button_press)
            ],
        },
        fallbacks=[]  # Empty list for fallback handlers
    )

    # Add conversation handler to the dispatcher
    app.add_handler(conversation_handler)

    # Add unknown command handler
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()


if __name__ == '__main__':
    main()
