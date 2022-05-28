
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageAutoDeleteTimerChanged, Update

from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from src.database import users_col
from src.utils import delete_keyboard, admin_menu, restart_callback
from src.telegram_api import updater, dispatcher
from bot_modules.user_modules.main_user_menu import main_handler
from bot_modules.admin_modules.admin import admin_handler


def admin_auth(update, context):
    user = users_col.find_one({'tg_id': update.effective_chat.id})
    if not user:
        users_col.insert_one({
            'tg_id': update.effective_chat.id,
            'username': update.effective_chat.username,
            'full_name': update.effective_chat.full_name,
            'admin': True,
            'code': '',
            'platform': ''
        })
        update.effective_chat.send_message('Вы авторизованны и наделены правами администратора, для входа в меню администратора воспользуйтесь /admin')
    elif not not user['admin']:
        users_col.update_one({'tg_id': update.effective_chat.id}, {'$set': {'admin': True}})
        update.effective_chat.send_message('Вы наделены правами администратора, для входа в меню администратора воспользуйтесь /admin')


def unknown(update, context):
    update.effective_chat.send_message('Вы ввели неизвестную командую')


def  main():
    dispatcher.add_handler(MessageHandler(Filters.regex(r'gkj-FYf-PYx-dwh'), admin_auth))
    dispatcher.add_handler(main_handler)
    dispatcher.add_handler(admin_handler)
    dispatcher.add_handler(CallbackQueryHandler(callback=restart_callback))
    dispatcher.add_handler(MessageHandler(Filters.all, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
