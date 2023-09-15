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
        "Вы в главном меню.\n"
        "Используйте кнопки ниже для навигации."
    )
    buttons = [
        [InlineKeyboardButton(text="Экстренные действия", callback_data=str(Actions.EMERGENCY))],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    # TODO: Check if the user is allowed to access the bot 
    # (ENV: TELEGRAM_ALLOWED_USERS)

    # If we are starting over we don't need to send new a message
    if context.user_data.get(Data.START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        user = update.message.from_user
        await update.message.reply_text(
            f"{user.first_name} {user.last_name}, рады приветствовать Вас!\n"
            "Добро пожаловать в Службу Экстренного Реагирования\n"
            "от компании General Telecom\n"
        )
        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[Data.START_OVER] = False

    return State.SELECTING_ACTION

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    log_conv(update, "Stopped conversation with Bot") 
    await update.message.reply_text("Всего доброго.")
    return State.END
