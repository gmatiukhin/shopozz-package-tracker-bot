import os
import logging
from datetime import timedelta

from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)

from tracklist import Tracklist

tracklist = Tracklist()

import scraper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please provide a tracking number using /track command",
    )


async def new_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and update.effective_chat is not None:
        chat_id = update.effective_chat.id
        tracking_number = context.args[0]
        resp = tracklist.add(chat_id, tracking_number)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=resp)


async def invalid_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Sorry, your track number is invalid."
    )


async def remove_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and update.effective_chat is not None:
        chat_id = update.effective_chat.id
        tracking_number = context.args[0]
        resp = tracklist.remove(chat_id, tracking_number)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=resp,
        )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I did not understand that command.",
    )


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Sorry, I do not know how to respond."
    )


async def tracking_status_check(context: ContextTypes.DEFAULT_TYPE):
    tracking_data = tracklist.user_data
    for chat_id, tracking_numbers in tracking_data.items():
        for number in tracking_numbers:
            message = scraper.get_status(number)
            if message and message != tracklist.status(number):
                await context.bot.send_message(chat_id=chat_id, text=message)
                tracklist.update_status(number, message)


if __name__ == "__main__":
    tracklist.deserialize()

    TOKEN = os.getenv("BOT_TOKEN")

    application = ApplicationBuilder().token(f"{TOKEN}").build()

    job_queue = application.job_queue
    assert job_queue is not None
    job_minute = job_queue.run_repeating(
        tracking_status_check, interval=timedelta(minutes=15)
    )

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    new_tracking_number_handler = CommandHandler(
        "track", new_tracking_number, filters.Regex(r"[A-Z]{2}\d{9}RU")
    )
    application.add_handler(new_tracking_number_handler)

    invalid_tracking_number_handler = CommandHandler("track", invalid_tracking_number)
    application.add_handler(invalid_tracking_number_handler)

    remove_tracking_number_handler = CommandHandler(
        "untrack", remove_tracking_number, filters.Regex(r"[A-Z]{2}\d{9}RU")
    )
    application.add_handler(remove_tracking_number_handler)

    # Unknown handlers
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    application.add_handler(unknown_command_handler)

    unknown_message_handler = MessageHandler(filters.ALL, unknown_message)
    application.add_handler(unknown_message_handler)

    application.run_polling()
