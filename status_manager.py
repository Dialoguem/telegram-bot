import logging
import os
from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Define the command handlers
def command1(update, _):
    file_path = "status/status.txt"
    with open(file_path, "r+") as file:
        lines = file.readlines()
        if "not" in lines[0]:
            lines[0] = lines[0].replace("not", "")
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            update.message.reply_text("Now it is possible to see and evaluate opinions")
        else:
            update.message.reply_text("Opinions are already visibles")

def command2(update, _):
    file_path = "status/status.txt"
    with open(file_path, "r+") as file:
        lines = file.readlines()
        if "not" not in lines[0]:
            lines[0] = "not" + lines[0]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            update.message.reply_text("Now it is NOT possible to see and evaluate opinions")
        else:
            update.message.reply_text("Opinions are already NOT visibles")

def command3(update, _):
    file_path = "status/status.txt"
    with open(file_path, "r+") as file:
        lines = file.readlines()
        if "not" in lines[1]:
            lines[1] = lines[1].replace("not", "")
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            update.message.reply_text("Now it is possible to update opinions")
        else:
            update.message.reply_text("It was alredy possible to update opinions")

def command4(update, _):
    file_path = "status/status.txt"
    with open(file_path, "r+") as file:
        lines = file.readlines()
        if "not" not in lines[1]:
            lines[1] = "not" + lines[1]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            update.message.reply_text("Now it is NOT possible to update opinions")
        else:
            update.message.reply_text("It was alredy NOT possible to update opinions")
def show_file(update, _):
    file_path = "status/status.txt"
    with open(file_path, "r") as file:
        file_content = file.read()
        update.message.reply_text("Status of the assembly:\n\n" + file_content)

def main():
    token = os.environ.get('TOKEN_STATUS_MANAGER')
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("showing_opinions", command1))
    dp.add_handler(CommandHandler("not_showing_opinions", command2))
    dp.add_handler(CommandHandler("next_round", command3))
    dp.add_handler(CommandHandler("stay_in_round", command4))
    dp.add_handler(CommandHandler("showstatus", show_file))

    # Start the bot
    updater.start_polling()
    print("Bot started!")

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
