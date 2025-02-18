import logging
from pathlib import Path

import environ
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

BASE_DIR = Path(__file__).resolve().parent.parent

# READING ENV
env = environ.Env()
env.read_env()
BOT_TOKEN = env.str("BOT_TOKEN")
BOT_GROUP_ID = env.int("BOT_GROUP_ID")


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    # send user's telegram ID to the user
    msg = f"<b>Assalom-u alaykum</b>, <i>{user.first_name}</i>!\n\n Sizning ID raqamingiz: <code>{user.id}</code>"
    msg += "\n\nFarzandingizning ismi-sharifini kiriting:\n"
    msg += "Masalan: Komiljonov Sarvarbek Yunusjon o'g'li"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="HTML",
    )


def echo(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    # get message text from user
    user_input = update.message.text
    msg = f"<i>ID:</i>  <code>{user.id}</code>\n\n"
    msg += f"<i>Farzand ismi:</i>  <b>{user_input}</b>"

    context.bot.send_message(
        chat_id=BOT_GROUP_ID,
        text=msg,
        parse_mode="HTML",
    )

    # send success message to user
    msg = "<b><i>Rahmat, muvaffaqiyatli saqlandi</i></b>"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="HTML",
    )


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
