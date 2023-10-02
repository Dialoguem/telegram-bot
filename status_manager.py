import logging
import os

from telegram.ext import ApplicationBuilder, CommandHandler


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Define the command handlers
async def command1(update, _):
    file_path = 'status/status.txt'
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        if 'not' in lines[0]:
            lines[0] = lines[0].replace('not', '')
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            await update.message.reply_text(
                'Now it is possible to see and evaluate opinions'
            )
        else:
            await update.message.reply_text('Opinions are already visibles')


async def command2(update, _):
    file_path = 'status/status.txt'
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        if 'not' not in lines[0]:
            lines[0] = 'not' + lines[0]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            await update.message.reply_text(
                'Now it is NOT possible to see and evaluate opinions'
            )
        else:
            await update.message.reply_text(
                'Opinions are already NOT visibles'
            )


async def command3(update, _):
    file_path = 'status/status.txt'
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        if 'not' in lines[1]:
            lines[1] = lines[1].replace('not', '')
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            await update.message.reply_text(
                'Now it is possible to update opinions'
            )
        else:
            await update.message.reply_text(
                'It was alredy possible to update opinions'
            )


async def command4(update, _):
    file_path = 'status/status.txt'
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        if 'not' not in lines[1]:
            lines[1] = 'not' + lines[1]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
            await update.message.reply_text(
                'Now it is NOT possible to update opinions'
            )
        else:
            await update.message.reply_text(
                'It was alredy NOT possible to update opinions'
            )


async def show_file(update, _):
    file_path = 'status/status.txt'
    with open(file_path, 'r') as file:
        file_content = file.read()
        await update.message.reply_text(
            'Status of the assembly:\n\n' + file_content
        )


def main():
    token = os.environ['TOKEN_STATUS_MANAGER']
    app = ApplicationBuilder().token(token).build()

    # Add command handlers
    app.add_handler(CommandHandler('showing_opinions', command1))
    app.add_handler(CommandHandler('not_showing_opinions', command2))
    app.add_handler(CommandHandler('next_round', command3))
    app.add_handler(CommandHandler('stay_in_round', command4))
    app.add_handler(CommandHandler('showstatus', show_file))

    # Run the bot until you press Ctrl-C
    app.run_polling()


if __name__ == '__main__':
    main()
