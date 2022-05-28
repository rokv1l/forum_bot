

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageAutoDeleteTimerChanged
from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from src.utils import admin_menu, delete_keyboard
from bot_modules.admin_modules.mailing import mailing_handler
from bot_modules.admin_modules.event import create_event_handler
from bot_modules.admin_modules.support_admin import support_admin_handler


def back_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    update.effective_chat.send_message('Вы вышли из меню администратора')
    return ConversationHandler.END


def unknown(update, context):
    update.effective_chat.send_message(
        'Вы ввели неизвестную команду.\n'\
        'Если что-то пошло не так то воспользуйтесь /exit для сброса диалогов к началу'
    )


admin_handler = ConversationHandler(
    entry_points=[
        CommandHandler('admin', admin_menu)
    ],
    states={
        config.ADMIN_MAIN_MENU: [
            mailing_handler,
            create_event_handler,
            CallbackQueryHandler(back_callback, pattern=r'Выход')
            # support_admin_handler
        ],
    },
    fallbacks=[
        MessageHandler(Filters.all, unknown)
    ]
)
