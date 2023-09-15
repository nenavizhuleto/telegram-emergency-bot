#!/usr/bin/env python

import os
from config import config
from log import logger
import emergency
import application

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



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()


    emergency_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(emergency.start, pattern=f"^{application.Actions.EMERGENCY}$")],
        states={
            emergency.State.SELECTING_ACTION: [
                CallbackQueryHandler(emergency.select_action, 
                                     pattern=f"^{emergency.Actions.RESTRICT_REMOTE_ACCESS}$|^{emergency.Actions.ERASE_SSD}$")
            ],
            emergency.State.CONFIRM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, emergency.confirmation_code)],
        },
        fallbacks=[
            CallbackQueryHandler(emergency.end, pattern=f"^{emergency.Actions.MENU}$"),
            CallbackQueryHandler(emergency.start, pattern=f"^{emergency.Actions.BACK}$")
        ],
        map_to_parent={
            emergency.State.END: application.State.SELECTING_ACTION
        }
    )

    selection_handlers = [
        emergency_conv,
        CallbackQueryHandler(emergency.end, pattern=f"^{emergency.Actions.MENU}$"),
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", application.start)],
        states={
            application.State.MENU: [CallbackQueryHandler(application.start, pattern=f"^{application.State.END}$|^{emergency.Actions.MENU}$")],
            application.State.SELECTING_ACTION: selection_handlers,
        },
        fallbacks=[
            CommandHandler("stop", application.stop),
            #CallbackQueryHandler(application.start, pattern=f"^{emergency.Actions.MENU}$")
        ]
    )

    app.add_handler(conv_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
