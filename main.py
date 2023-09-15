#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
class AutoIncrementor:
    def __init__(self):
        self.counter = 0

    def get(self) -> str:
        self.counter = self.counter + 1

        return chr(self.counter)

ai = AutoIncrementor()

class MetaState:
    SHOWING = ai.get()
    STOPPING = ai.get()

class ApplicationState:
    MENU = ai.get()
    SELECTING_ACTION = ai.get()
    END = ConversationHandler.END

class ApplicationActions:
    EMERGENCY = ai.get()
    CANCEL = ai.get()

class EmergencyState:
    SELECTING_ACTION = ai.get()
    CONFIRM_CODE = ai.get()
    RESTRICT_REMOTE_ACCESS = ai.get()
    ERASE_SSD = ai.get()
    END = ai.get()

class EmergencyActions:
    RESTRICT_REMOTE_ACCESS = ai.get()
    ERASE_SSD = ai.get()

class Data:
    CURRENT_EMERGENCY_ACTION = ai.get()
    START_OVER = ai.get()


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def make_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Emergency actions", callback_data=str(ApplicationActions.EMERGENCY))],
        [InlineKeyboardButton(text="Cancel", callback_data=str(ApplicationActions.CANCEL))]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    
    text = (
        "You're in main menu now.\n"
        "Use buttons to navigate over service"
    )
    buttons = [
        [InlineKeyboardButton(text="Emergency actions", callback_data=str(ApplicationActions.EMERGENCY))],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    # TODO: Check if the user is allowed to access the bot 
    # (ENV: TELEGRAM_ALLOWED_USERS)

    # If we are starting over we don't need to send new a message
    if context.user_data.get(Data.START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(
            "Welcome to GT Emergency Telegram Bot"
        )
        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[Data.START_OVER] = False

    return ApplicationState.SELECTING_ACTION


async def emergency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    buttons = [
        [InlineKeyboardButton(text="Restrict remote access", callback_data=str(EmergencyActions.RESTRICT_REMOTE_ACCESS))],
        [InlineKeyboardButton(text="Erase SSD", callback_data=str(EmergencyActions.ERASE_SSD))],
        #[InlineKeyboardButton(text="Back", callback_data=str(ApplicationState.MENU))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)


    text = "Please select action to perform"

    if not context.user_data.get(Data.START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text=text, reply_markup=keyboard)


    context.user_data[Data.START_OVER] = False
    
    return EmergencyState.SELECTING_ACTION

async def end_emergency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[Data.START_OVER] = True
    await start(update, context)
    return ApplicationState.MENU


async def select_emergency_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    data = update.callback_query.data
    context.user_data[Data.CURRENT_EMERGENCY_ACTION] = data
    text = "Please provide confirmation code"

    await update.callback_query.answer()
    #await update.callback_query.edit_message_text(text=text)
    await update.callback_query.message.reply_text(text=text)

    return EmergencyState.CONFIRM_CODE

async def perform_emergency_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = context.user_data[Data.CURRENT_EMERGENCY_ACTION]

    buttons = [
        [InlineKeyboardButton(text="Back To Menu", callback_data=str(ApplicationActions.EMERGENCY))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    status = False

    if action == EmergencyActions.RESTRICT_REMOTE_ACCESS:
        await update.message.reply_text("Restricting remote access. Please stand by.")

        # TODO: Perform mikrotik access and actually do action

        status = True
    elif action == EmergencyActions.ERASE_SSD:
        await update.message.reply_text("Not implemented yet.")


    if status:
        text = "Done."
        await update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        text = "Fail."
        await update.message.reply_text(text=text, reply_markup=keyboard)

    return EmergencyState.END


async def confirmation_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    code = update.message.text
    success_text = "Success"
    failure_text = (
        "Invalid confirmation code.\n"
        "Type it again\nor use /stop to cancel"
    )
    if code == "1234":
        #await update.message.reply_text(text=success_text)
        return await perform_emergency_action(update, context)
    else:
        await update.message.reply_text(text=failure_text)
        return EmergencyState.CONFIRM_CODE


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text("Okay, bye.")

    return ApplicationState.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("TOKEN").build()


    emergency_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(emergency, pattern="^" + str(ApplicationActions.EMERGENCY) + "$")],
        states={
            EmergencyState.SELECTING_ACTION: [CallbackQueryHandler(select_emergency_action, pattern=f"^{EmergencyActions.RESTRICT_REMOTE_ACCESS}$|^{EmergencyActions.ERASE_SSD}$")],
            EmergencyState.CONFIRM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation_code)],
        },
        fallbacks=[
            CommandHandler("stop", stop)
        ],
        map_to_parent={
            EmergencyState.END: ApplicationState.SELECTING_ACTION,
        }
    )

    selection_handlers = [
        emergency_conv,
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ApplicationState.MENU: [CallbackQueryHandler(start, pattern=f"^{ApplicationState.END}$")],
            ApplicationState.SELECTING_ACTION: selection_handlers,
            MetaState.STOPPING: [CommandHandler("start", start)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
