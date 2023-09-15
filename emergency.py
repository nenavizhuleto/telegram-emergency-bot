from utils import AI
from log import logger, log_conv
from application import Data
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

class State:
    SELECTING_ACTION = AI.get()
    CONFIRM_CODE = AI.get()
    RESTRICT_REMOTE_ACCESS = AI.get()
    ERASE_SSD = AI.get()
    END = AI.get()

class Actions:
    RESTRICT_REMOTE_ACCESS = AI.get()
    ERASE_SSD = AI.get()
    BACK = AI.get()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    log_conv(update, "Entered emergency menu")
    buttons = [
        [InlineKeyboardButton(text="Отключить удаленный доступ", callback_data=str(Actions.RESTRICT_REMOTE_ACCESS))],
        [InlineKeyboardButton(text="SSD: Удалить данные", callback_data=str(Actions.ERASE_SSD))],
        #[InlineKeyboardButton(text="Back", callback_data=str(ApplicationState.MENU))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)


    text = "Какое действие необходимо выполнить?"

    if not context.user_data.get(Data.START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text=text, reply_markup=keyboard)


    context.user_data[Data.START_OVER] = False
    
    return State.SELECTING_ACTION

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    log_conv(update, "Exited emergency menu")
    context.user_data[Data.START_OVER] = True
    await start(update, context)
    return application.State.MENU


async def select_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    log_conv(update, "Selecting emergency action")
    data = update.callback_query.data
    context.user_data[Data.CURRENT_EMERGENCY_ACTION] = data
    text = "Введите код подтверждения следующим сообщением."

    await update.callback_query.answer()
    #await update.callback_query.edit_message_text(text=text)
    await update.callback_query.message.reply_text(text=text)

    return State.CONFIRM_CODE

async def perform_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = context.user_data[Data.CURRENT_EMERGENCY_ACTION]

    buttons = [
        [InlineKeyboardButton(text="Назад к списку действий", callback_data=str(Actions.BACK))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    status = False

    if action == Actions.RESTRICT_REMOTE_ACCESS:
        log_conv(update, "Selected to restrict remote access")
        await update.message.reply_text("Отключаем удаленный доступ. Пожалуйста ожидайте...")

        # TODO: Perform mikrotik access and actually do action

        status = True
    elif action == Actions.ERASE_SSD:
        log_conv(update, "Selected to erase ssd")
        await update.message.reply_text("Функция находится в разработке.")


    if status:
        text = "Успешно."
        log_conv(update, "Operation finished successfully")
        await update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        text = "Ошибка."
        log_conv(update, "Operation failed")
        await update.message.reply_text(text=text, reply_markup=keyboard)

    return State.END


async def confirmation_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    code = update.message.text
    log_conv(update, f"Typed confirmation code: {code}")
    failure_text = (
        "Код подтверждения неверный.\n"
        "Введите снова\nили используйте команду /stop для отмены"
    )
    if code == "1234":
        log_conv(update, f"Confirmation successful")
        #await update.message.reply_text(text=success_text)
        return await perform_action(update, context)
    else:
        log_conv(update, f"Confirmation failed")
        await update.message.reply_text(text=failure_text)
        return State.CONFIRM_CODE


