
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageAutoDeleteTimerChanged

from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from src.utils import delete_keyboard, admin_menu, restart_callback
from src.telegram_api import updater, dispatcher
from bot_modules.user_modules.main_user_menu import main_handler
from bot_modules.admin_modules.admin import admin_handler


def unknown(update, context):
    update.effective_chat.send_message('Вы ввели неизвестную командую')


def  main():
    dispatcher.add_handler(main_handler)
    dispatcher.add_handler(admin_handler)
    dispatcher.add_handler(CallbackQueryHandler(callback=restart_callback))
    dispatcher.add_handler(MessageHandler(Filters.all, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
