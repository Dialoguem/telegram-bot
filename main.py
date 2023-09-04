import csv
import logging
from telegram import Update, ReplyKeyboardMarkup,InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler,  CallbackQueryHandler
from telegram import ParseMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

CSV_FILE_PATH = 'answers.csv'
MAX_LINES = 1  # Maximum number of lines to show at once

# List of allowed handles
allowed_handles_group1 = ['radish', 'peas', 'squash', 'sweet potato', 'pepper', 'celery', 'onion', 'tomato', 'beet', 'artichoke', 'couliflower', 'eggplant', 'green beans', 'turnip', 'potato', 'lettuce', 'garlic', 'pumpkin', 'asparagus', 'broccoli']
allowed_handles_group2 = ['peach', 'melon', 'grape', 'pineapple', 'banana', 'cherry', 'blueberry', 'apple', 'red apple', 'coconut', 'lemon', 'watermelon', 'kiwi', 'pear', 'orange', 'mango', 'strawberry', 'avocado']
allowed_handles_group3 = ['elephant', 'crocodile', 'monkey', 'octopus', 'hedgehog', 'fox', 'giraffe', 'goat', 'cat', 'turtle', 'sheep', 'frog', 'bee', 'tiger', 'dog', 'butterfly', 'dolphin', 'snake', 'cow', 'lion', 'bear', 'penguin']
# States
ENTER_HANDLE, ANSWER_1, ANSWER_2, SHOW_ANSWERS_CONFIRMATION, SHOW_ANSWERS_INPUT = range(5)

# Keyboard options
#reply_keyboard = [['Yes', 'No']]
#markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Handler for the /start command
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    if 'handle' not in context.user_data.keys():
        context.user_data['handle'] = None
        update.message.reply_text(f"""Hello, {user.first_name}\! Welcome to the blind assembly *Dialoguem*\.\n\n
        By participating in this social experiment and using the associated application, you are giving your informed consent for the collection and usage of your anonymized data for research purposes\. We do not collect any personal information during this process\. Your privacy and data protection are our top priorities, and we are committed to adhering to the principles outlined in the General Data Protection Regulation \(GDPR\)\.
        The data collected will be used solely for academic research and will be anonymized to ensure your identity remains confidential\.
        If you have any concerns or questions about data usage, please feel free to contact us\. We appreciate your participation and trust in our research endeavor\.\n\n
        As a participant in this discussion, you are encouraged to share your thoughts on an increasingly important topic: the environmental impact of academic events, such as schools and conferences\.
        On one side of the debate, some may argue that environmental concerns are being overemphasized, possibly affecting the overall experience of such events\. They might suggest that options like vegetarian meals and wooden utensils are unnecessary measures\.
        On the other end of the spectrum, some argue for drastic and immediate overhaul of our traditional academic event formats, advocating for a nearly complete shift to online formats and significantly reduced event frequency, emphasizing that if the scientific community doesn't take radical steps towards environmental responsibility, who will?
        In the middle, there are also considerations of the post\-pandemic reality and the importance of in\-person networking for early\-career researchers, as well as the potential mental health implications of limiting such opportunities\.\n
        We've set up a scale from 0 to 10 for you to express your opinion: *0 represents* the belief that environmental concerns are overblown, while *10 indicates* the belief that extreme, radical changes to our event formats are urgent and necessary\.\n
        Remember, this is a spectrum\. All shades of opinion are welcome\!\n\n
        Please enter the *avatar* that has been assigned to you, in this way you will be anonymous throughout the process:""",parse_mode=ParseMode.MARKDOWN_V2)
        return ENTER_HANDLE
    else:
        with open('status/status.txt','r') as status_file:
            line=status_file.readline()
            line=status_file.readline()
        if 'not' in line:
            update.message.reply_text("Please, wait for instructions from human facilitators.")
        else:
            context.user_data['nex_rounds']=True
            update.message.reply_text(f"Hello, {user.first_name}! Please update your opinion if you want, or type 'keep the same opinion' if not:")
            return ANSWER_1

# Handler for handling user's handle
def enter_handle(update: Update, context: CallbackContext):
    handle = update.message.text.lower().strip()
    if handle in allowed_handles_group1:
        context.user_data['handle'] = handle
        context.user_data['group'] = 1
        update.message.reply_text("Great! Please, write a short message describing your attitute about the theme of the assembly. xxx:")
        return ANSWER_1
    elif handle in allowed_handles_group2:
        context.user_data['handle'] = handle
        context.user_data['group'] = 2
        update.message.reply_text("Great! Please, write a short message describing your attitute about the theme of the assembly. xxx:")
        return ANSWER_1
    elif handle in allowed_handles_group3:
        context.user_data['handle'] = handle
        context.user_data['group'] = 3
        update.message.reply_text("Great! Please, write a short message describing your attitute about the theme of the assembly. xxx:")
        return ANSWER_1
    else:
        update.message.reply_text("Sorry, the avatar you have entered is not valid. Please enter a valid avatar:")
        return ENTER_HANDLE

# Handler for handling user's first answer
def answer_1(update: Update, context: CallbackContext):
    if 'answer_1' in context.user_data.keys() and 'keep' in update.message.text.lower().strip() and 'opinion' in update.message.text.lower().strip():
        update.message.reply_text("Okay, you want to keep the same opinion, now provide an integer number between 0 and 10 describing your opinion, where 0 is completely against and 10 completely in favor:")
        return ANSWER_2
    else:
        answer = update.message.text.strip()
        context.user_data['answer_1'] = answer
        update.message.reply_text("Okay, now provide an integer number between 0 and 10 describing your opinion, where 0 is completely against and 10 completely in favor:")
        return ANSWER_2

# Handler for handling user's second answer
def answer_2(update: Update, context: CallbackContext):
    answer = update.message.text.strip()
    if answer.isdigit() and int(answer) >= 0 and int(answer) <= 10:
        handle = context.user_data['handle']
        group = context.user_data['group']
        answer_1 = context.user_data['answer_1']

        # Save data to CSV
        with open('answers.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([handle, group, answer_1, answer])

            update.message.reply_text("Thank you for providing your opinion! They have been recorded and will be shown anonymously to the rest of the assembly.Now please await instructions from the human facilitators.")
            return ConversationHandler.END
    else:
        update.message.reply_text("Sorry, it should be an integer between 0 and 10, where 0 is completely against and 10 completely in favor:")
        return ANSWER_2

# Handler for the /show_answers command
def show_answers(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Check the number of lines in the CSV file
    with open(CSV_FILE_PATH, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        num_lines = sum(1 for _ in csv_reader)

    # Check if facilitators had enabled this option
    with open('status/status.txt','r') as status_file:
        line=status_file.readline()


    if num_lines < MAX_LINES or 'not' in line:
        message = "Please wait, the opinions will be available soon."
        context.bot.send_message(chat_id=chat_id, text=message)
    else:
        with open(CSV_FILE_PATH, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                inline_keyboard = []
                for i in range(11):  # Numbers from 0 to 10
                    inline_keyboard = [
                    [
                        InlineKeyboardButton(str(i), callback_data=f"{row[0]},{row[3]},{i}")
                        for i in range(6)
                    ],
                    [
                        InlineKeyboardButton(str(i), callback_data=f"{row[0]},{row[3]},{i}")
                        for i in range(6, 11)
                    ],
                    [
                    InlineKeyboardButton("Yes", callback_data=f"{row[0]},{row[3]},yes"),
                    InlineKeyboardButton("No", callback_data=f"{row[0]},{row[3]},no")
                ]
                ]
                reply_markup = InlineKeyboardMarkup(inline_keyboard)

                handle, group, answer_1, _ = row

                if handle!=context.user_data['handle'] and int(group)==int(context.user_data['group']):
                    message = f"{handle} said {answer_1}"
                    message += "\nPlease provide an evaluation betwee 0 and 10 of this opinion and indicate if you would be willing to compromise with it:"
                    context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

def handle_button_press(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data.split(',')

    # Extract the data from the callback data
    column1 = data[0]
    column2 = data[1]
    answer = data[2]


    # Save the selected values in a separate CSV file
    file_name = f"{context.user_data['handle']}.csv"
    if answer.isdigit() and int(answer) >= 0 and int(answer) <= 10:
        with open(file_name, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([column1, column2, answer])

        #message = f"Selected number {answer} for {column1}, {column2}. Saved to {file_name}."
        #context.bot.send_message(chat_id=chat_id, text=message)
    elif answer.lower() in ['yes', 'no']:
        # Save the yes/no answer in a separate CSV file
        answer_file = f"{context.user_data['handle']}_answer.csv"
        with open(answer_file, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([column1, column2, answer])
        #message = f"Selected answer {answer} for {column1}, {column2}. Saved to {answer_file}."
        #context.bot.send_message(chat_id=chat_id, text=message)
        query.message.edit_reply_markup(reply_markup=None)

    # Remove the inline keyboard from the original message


# Handler for handling unknown commands
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry, I didn't understand that command.")


def main():
    # Set up the Telegram bot. Put your bot's  token to access the HTTP API
    updater = Updater("xxx", use_context=True)
    dispatcher = updater.dispatcher

    # Define conversation handler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('dialoguem', start)],
        states={
            ENTER_HANDLE: [MessageHandler(Filters.text & ~Filters.command, enter_handle)],
            ANSWER_1: [MessageHandler(Filters.text & ~Filters.command, answer_1)],
            ANSWER_2: [MessageHandler(Filters.text & ~Filters.command, answer_2)],
                    },
        fallbacks=[]  # Empty list for fallback handlers
    )

    # Add conversation handler to the dispatcher
    dispatcher.add_handler(conversation_handler)

    # Add show answers command handler
    dispatcher.add_handler(CommandHandler('show_opinions', show_answers))

    # Add unknown command handler
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    dispatcher.add_handler(CallbackQueryHandler(handle_button_press))

    # Start the bot
    updater.start_polling()
    print("Bot started!")

    updater.idle()




if __name__ == '__main__':
    main()
