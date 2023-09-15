from utils import AI
from log import log_conv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

class Data:
    CURRENT_EMERGENCY_ACTION = AI.get()
    START_OVER = AI.get()

class State:
    MENU = AI.get()
    SELECTING_ACTION = AI.get()
    END = ConversationHandler.END

class Actions:
    EMERGENCY = AI.get()
    CANCEL = AI.get()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    log_conv(update, "Started conversation with Bot") 
    text = (
        "You're in main menu now.\n"
        "Use buttons to navigate over service"
    )
    buttons = [
        [InlineKeyboardButton(text="Emergency actions", callback_data=str(Actions.EMERGENCY))],
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

    return State.SELECTING_ACTION

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    log_conv(update, "Stopped conversation with Bot") 
    await update.message.reply_text("Okay, bye.")
    return State.END
