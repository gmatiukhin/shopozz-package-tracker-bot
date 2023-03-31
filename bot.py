import os
from datetime import timedelta
import traceback
import json
import html

from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)
from telegram.constants import ParseMode

from tracklist import Tracklist

tracklist = Tracklist()

import scraper

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(filename="./bot.log", mode="w"),
        logging.StreamHandler(),
    ],
)

DEVELOPER_CHAT_ID = 563638147


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please provide a tracking number using /track command.\nYou can use /untrack to stop receiving status updates.",
    )


async def new_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and update.effective_chat is not None:
        chat_id = update.effective_chat.id
        tracking_number = context.args[0]
        logging.info(f"New tracking number {tracking_number}; chat {chat_id}")
        resp = tracklist.add(chat_id, tracking_number)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=resp)


async def invalid_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    chat_id = update.effective_chat.id
    logging.info(f"Invalid tracking number; user {chat_id}")
    await context.bot.send_message(
        chat_id=chat_id, text="Sorry, your track number is invalid."
    )


async def remove_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and update.effective_chat is not None:
        chat_id = update.effective_chat.id
        tracking_number = context.args[0]
        logging.info(f"Remove tracking number {tracking_number}; chat {chat_id}")
        resp = tracklist.remove(chat_id, tracking_number)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=resp,
        )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    chat_id = update.effective_chat.id
    logging.info(f"Unknown command; chat {chat_id}")
    await context.bot.send_message(
        chat_id=chat_id,
        text="Sorry, I did not understand that command.",
    )


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    chat_id = update.effective_chat.id
    logging.info(f"Unknown message; chat {chat_id}")
    await context.bot.send_message(
        chat_id=chat_id, text="Sorry, I do not know how to respond."
    )


async def tracking_status_check(context: ContextTypes.DEFAULT_TYPE):
    tracking_data = tracklist.tracking_data
    for tracking_number, chats in tracking_data.items():
        status, timestamp = scraper.get_status(tracking_number)
        curr_status = tracklist.status(tracking_number)
        curr_timestamp = tracklist.timestamp(tracking_number)
        if status and status != curr_status and timestamp != curr_timestamp:
            logging.info(f"New status for package {tracking_number}")
            message = f"Package {tracking_number}\n\n{status}"
            for chat_id in chats:
                await context.bot.send_message(chat_id=chat_id, text=message)
                logging.info(
                    f"Sent unpdate about package {tracking_number} to chat {chat_id}"
                )
            tracklist.update_status(tracking_number, status, timestamp)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logging.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    assert context.error is not None
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


if __name__ == "__main__":
    tracklist.deserialize()

    TOKEN = os.getenv("BOT_TOKEN")

    application = ApplicationBuilder().token(f"{TOKEN}").build()

    job_queue = application.job_queue
    assert job_queue is not None
    job_minute = job_queue.run_repeating(
        tracking_status_check, interval=timedelta(minutes=5)
    )

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    new_tracking_number_handler = CommandHandler(
        "track", new_tracking_number, filters.Regex(r"[A-Z]{2}\d{9}RU")
    )
    application.add_handler(new_tracking_number_handler)

    invalid_new_tracking_number_handler = CommandHandler(
        "track", invalid_tracking_number
    )
    application.add_handler(invalid_new_tracking_number_handler)

    remove_tracking_number_handler = CommandHandler(
        "untrack", remove_tracking_number, filters.Regex(r"[A-Z]{2}\d{9}RU")
    )
    application.add_handler(remove_tracking_number_handler)
    invalid_remove_tracking_number_handler = CommandHandler(
        "untrack", invalid_tracking_number
    )
    application.add_handler(invalid_remove_tracking_number_handler)

    # Unknown handlers
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    application.add_handler(unknown_command_handler)

    unknown_message_handler = MessageHandler(filters.ALL, unknown_message)
    application.add_handler(unknown_message_handler)

    application.add_error_handler(error_handler)

    application.run_polling()
