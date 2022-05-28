
from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.ext import MessageFilter

import config
from src.database import users_col


def access_control(func):
    def inner(update, context):
        auth = context.user_data.get('autorized')
        if auth:
            return func(update, context)
        
        elif not auth and auth is not None:
            return
        
        elif auth is None:
            user = users_col.find_one({'tg_id': update.effective_chat.id})
            if user:
                context.user_data['autorized'] = True
                return func(update, context)
                
            else:
                context.user_data['autorized'] = False
                
    return inner


def admin_access_control(func):
    def inner(update, context):
        auth = context.user_data.get('admin')
        if auth:
            return func(update, context)
        
        elif not auth and auth is not None:
            return
        
        elif auth is None:
            user = users_col.find_one({'tg_id': update.effective_chat.id})
            if user and user['admin']:
                context.user_data['admin'] = True
                return func(update, context)
                
            else:
                context.user_data['admin'] = False
    return inner


def get_one_line_keyboard(buttons):
    line = [InlineKeyboardButton(button, callback_data=button) for button in buttons]
    return InlineKeyboardMarkup([line])


def delete_keyboard(context, chat_id):
    try:
        context.bot.edit_message_text(
            text=context.user_data['msg_for_del_keys'].text,
            chat_id=chat_id,
            message_id=context.user_data['msg_for_del_keys'].message_id
        )
    except Exception:
        pass
    
    del context.user_data['msg_for_del_keys']


def admin_menu(update, context):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('Рассылка всем пользователям', callback_data='mailing')],
        [InlineKeyboardButton('Создать событие', callback_data='create_event')],
        [InlineKeyboardButton('Выход', callback_data='Выход')],
        # [InlineKeyboardButton('Ответить на вопросы *Тех. поддержка*', callback_data='qna_support')],
    ])
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Вы находитесь в меню администратора',
        reply_markup=keyboard
    )
    return config.ADMIN_MAIN_MENU


def restart_callback(update, context):
    context.bot.edit_message_text(
        text=update.callback_query.message.text,
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id
    )
    update.effective_chat.send_message(
        'Похоже что бот был перезагружен, все диалоги сброшены в начало.\n'\
        'Для использования бота нажмите /start'
    )
    

def get_one_button_keyboard(text):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=text)]])


def get_one_line_keyboard(buttons):
    line = [InlineKeyboardButton(button, callback_data=button) for button in buttons]
    return InlineKeyboardMarkup([line])


def get_one_line_buttons(buttons):
    line = [InlineKeyboardButton(button, callback_data=button) for button in buttons]
    return line

