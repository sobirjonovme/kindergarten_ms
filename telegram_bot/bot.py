import logging

from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

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

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="HTML",
    )


def echo(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    # send user's telegram ID to the user
    msg = f"<b>Assalom-u alaykum</b>, <i>{user.first_name}</i>!\n\n Sizning ID raqamingiz: <code>{user.id}</code>"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="HTML",
    )


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

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
