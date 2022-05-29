import re
from datetime import datetime

from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

import config
from src.utils import delete_keyboard, admin_menu, get_one_button_keyboard, get_one_line_keyboard
from src.database import events_col


def ask_event_name(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Введите имя события',
        reply_markup=get_one_button_keyboard('Назад')
    )
    return config.EVENT_DESC


def ask_event_desc(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    if update.callback_query and update.callback_query.data == 'Назад':
        return admin_menu(update, context)
    
    new_event_name = update.message.text
    context.user_data['new_event_name'] = new_event_name
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Введите описание события',
        reply_markup=get_one_button_keyboard('Назад')
    )
    return config.EVENT_DT


def ask_event_dt(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    if update.callback_query and update.callback_query.data == 'Назад':
        return admin_menu(update, context)
    
    context.user_data['new_event_desc'] = update.message.text
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Введите дату и время проведения события в формате ДД.ММ.ГГ ЧЧ.ММ (например 29.05.22 12.00)',
        reply_markup=get_one_button_keyboard('Назад')
    )
    return config.EVENT_CATEGORY


def ask_event_cat(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    if update.callback_query and update.callback_query.data == 'Назад':
        return admin_menu(update, context)
        
    new_event_dt = update.message.text
    if not re.match(r'^\d\d\.\d\d\.\d\d\ \d\d\.\d\d$', new_event_dt):
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Вы ввели дату и время в неверном формате, попробуйте еще раз соблюдая формат ДД.ММ.ГГ ЧЧ.ММ (например 29.05.22 12.00)',
        reply_markup=get_one_button_keyboard('Назад')
        )
        return config.EVENT_CATEGORY
    
    try:
        new_event_dt = datetime.strptime(new_event_dt, '%d.%m.%y %H.%M')
        
    except Exception:
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Вы ввели невозможную комбинацию даты и времени, попробуйте еще раз',
        reply_markup=get_one_button_keyboard('Назад')
        )
        return config.EVENT_CATEGORY
    
    context.user_data['new_event_dt'] = new_event_dt.isoformat()
    keyboard = InlineKeyboardMarkup([
        # [InlineKeyboardButton('Творческая программа', callback_data='Творческая программа')],
        # [InlineKeyboardButton('Деловая программа', callback_data='Деловая программа')],
        # [InlineKeyboardButton('Туристическая программа', callback_data='Туристическая программа')],
        [InlineKeyboardButton('Турниры', callback_data='Турниры')],
        [InlineKeyboardButton('Экспертные беседки', callback_data='Экспертные беседки')],
        [InlineKeyboardButton('Мероприятия от партнеров', callback_data='Мероприятия от партнеров')],
        [InlineKeyboardButton('Назад', callback_data='Назад')],
    ])
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Введите одну из категорий события',
        reply_markup=keyboard
    )
    return config.CREATE_EVENT_CONFIRM


def create_event_confirm_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    data = update.callback_query.data
    if data == 'Назад':
        return admin_menu(update, context)
    
    context.user_data['new_event_cat'] = data
    
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Вы уверены что введенные вами данные верны?\n\n'\
        f'Категория: {context.user_data["new_event_cat"]}\n\n'\
        f'Имя: {context.user_data["new_event_name"]}\n\n'\
        f'Описание: {context.user_data["new_event_desc"]}\n\n'\
        f'Дата и время: {context.user_data["new_event_dt"].replace("T", " ")[:-3]}',
        reply_markup=get_one_line_keyboard(['Да', 'Нет'])
    )
    return config.CREATE_EVENT
    

def create_event_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    data = update.callback_query.data
    if data == 'Нет':
        update.effective_chat.send_message('⛔️Создание события отменено⛔️')
        return admin_menu(update, context)

    try:
        event = {}
        event['category'] = context.user_data['new_event_cat']
        event['name'] = context.user_data['new_event_name']
        event['desc'] = context.user_data['new_event_desc']
        event['dt'] = datetime.fromisoformat(context.user_data['new_event_dt'])
        event['users'] = []
        events_col.insert_one(event)
    except Exception:
        update.effective_chat.send_message('Произошла ошибка при добавлении события в базу, попробуйте еще раз через 5 минут')
        return admin_menu(update, context)
    
    update.effective_chat.send_message('✅Событие успешно созданно✅')
    return admin_menu(update, context)

        

def unknown(update, context):
    update.effective_chat.send_message(
        'Вы ввели неизвестную команду.\n'\
        'Если что-то пошло не так то воспользуйтесь /exit для сброса диалогов к началу'
    )


def _exit(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    update.effective_chat.send_message('Вы вышли из всех диалогов, для использования бота нажмите /start')
    return ConversationHandler.END


create_event_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=ask_event_name, pattern=r'create_event')
    ],
    states={
        config.EVENT_DESC: [
            MessageHandler(Filters.text, ask_event_desc),
            CallbackQueryHandler(callback=ask_event_desc)
            ],
        config.EVENT_DT: [
            MessageHandler(Filters.text, ask_event_dt),
            CallbackQueryHandler(callback=ask_event_dt)
            ],
        config.EVENT_CATEGORY: [
            MessageHandler(Filters.text, ask_event_cat),
            CallbackQueryHandler(callback=ask_event_cat)
            ],
        config.CREATE_EVENT_CONFIRM: [CallbackQueryHandler(callback=create_event_confirm_callback)],
        config.CREATE_EVENT: [CallbackQueryHandler(callback=create_event_callback)],
    },
    fallbacks=[
        CommandHandler('exit', _exit),
        MessageHandler(Filters.all, unknown)
        ],
    map_to_parent={
        config.ADMIN_MAIN_MENU: config.ADMIN_MAIN_MENU,
        ConversationHandler.END: ConversationHandler.END
    }
)
