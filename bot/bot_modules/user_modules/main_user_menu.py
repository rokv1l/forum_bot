from datetime import date, datetime, time

from loguru import logger
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import config
from src.utils import delete_keyboard, admin_menu, get_one_button_keyboard, get_one_line_keyboard
from src.database import users_col, day_program_col, events_col


def start(update, context):
    if context.user_data.get('autorized') or users_col.find_one({'tg_id': update.effective_chat.id}):
        context.user_data['autorized'] = True
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('Материалы', callback_data='Материалы')],
            [InlineKeyboardButton('Расписание дня', callback_data='Расписание дня')],
            [InlineKeyboardButton('Внеобразовательная программа', callback_data='Внеобразовательная программа')],
            [InlineKeyboardButton('Тех. поддержка', callback_data='Тех. поддержка')],
            [InlineKeyboardButton('Выход', callback_data='Выход')],
        ])
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Выберите действие',
            reply_markup=keyboard
        )
        return config.USER_MENU

    update.effective_chat.send_message('Пожалуйста введи свой идентификатор что-бы я мог дать тебе доступ')
    return config.AUTH_CODE


def auth_code(update, context):
    code = update.message.text
    user = users_col.find_one({'code': code})
    if user:
        context.user_data['autorized'] = True
        users_col.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'autorized': True,
                    'tg_id': update.effective_chat.id,
                    'username': update.effective_chat.username
                }
            })
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('Материалы', callback_data='Материалы')],
            [InlineKeyboardButton('Расписание дня', callback_data='Расписание дня')],
            [InlineKeyboardButton('Внеобразовательная программа', callback_data='Внеобразовательная программа')],
            [InlineKeyboardButton('Тех. поддержка', callback_data='Тех. поддержка')],
            [InlineKeyboardButton('Выход', callback_data='Выход')],
        ])
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            f'Привет {user["full_name"]}, вы успешно авторизованны',
            reply_markup=keyboard
        )
        
    elif update.message.text == 'gkj-FYf-PYx-dwh':
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
            update.effective_chat.send_message('Вы авторизованны и наделены правами администратора, для входа в меню администратора воспользуйтесь /admin\nДля просмотра функционала пользователя воспользуйтесь /start')
        elif not not user['admin']:
            users_col.update_one({'tg_id': update.effective_chat.id}, {'$set': {'admin': True}})
            update.effective_chat.send_message('Вы наделены правами администратора, для входа в меню администратора воспользуйтесь /admin\nДля просмотра функционала пользователя воспользуйтесь /start')

    else:
        update.effective_chat.send_message('Вы ввели недействительный код, проверьте правильность написания и попробуйте еще раз')
        return config.AUTH_CODE
    
    return config.USER_MENU


def main_menu_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    data = update.callback_query.data
    if data == 'Назад':
        update.effective_chat.send_message('Вы нажали кнопку "Назад"')
        return start(update, context)
    
    elif data == 'Выход':
        update.effective_chat.send_message('Вы нажали кнопку "Выход"')
        return ConversationHandler.END

    elif data == 'Материалы':
        update.effective_chat.send_message('Вы нажали кнопку "Материалы"')
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('Карта форума', callback_data='Карта форума')],
            [InlineKeyboardButton('Программа форума', callback_data='Программа форума')],
            [InlineKeyboardButton('Правила форума', callback_data='Правила форума')],
            [InlineKeyboardButton('Материалы от спикеров', url='https://www.google.ru/')],
            [InlineKeyboardButton('Назад', callback_data='Назад')],
        ])
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Выберите интересующую вас категорию',
            reply_markup=keyboard
        )
        return config.MATERIALS

    elif data == 'Расписание дня':
        update.effective_chat.send_message('Вы нажали кнопку "Расписание дня"')
        platform = users_col.find_one({'tg_id': update.effective_chat.id})['platform']
        day_events = context.user_data['day_events'] = day_program_col.find_one({'date': date.today().isoformat(), 'platform': platform})
        text = ''
        # keyboard = []
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='Назад')]])
        if not day_events:
            context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
                'Расписание дня еще не заполнено',
                reply_markup=keyboard
            )
            return
        
        for index, event in enumerate(day_events["events"]):
            text += f"{index + 1}: {event['event_name']}\n"
            text += f"Время начала: {event['event_time']}\n\n"
            # keyboard.append(InlineKeyboardButton(index + 1, callback_data=index + 1))
            
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            text,
            reply_markup=keyboard
        )
        return 

    elif data == 'Внеобразовательная программа':
        update.effective_chat.send_message('Вы нажали кнопку "Внеобразовательная программа"')
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('Творческая программа', callback_data='Творческая программа')],
            [InlineKeyboardButton('Деловая программа', callback_data='Деловая программа')],
            [InlineKeyboardButton('Туристическая программа', callback_data='Туристическая программа')],
            [InlineKeyboardButton('Экспертные беседки', callback_data='Экспертные беседки')],
            [InlineKeyboardButton('Турниры', callback_data='Турниры')],
            [InlineKeyboardButton('Назад', callback_data='Назад')],
        ])
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Выберите интересующию вас программу',
            reply_markup=keyboard
        )
        return config.EVENTS_CAT
        
    elif data == 'Тех. поддержка':
        update.effective_chat.send_message('Вы нажали кнопку "Тех. поддержка"')
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Сформулируйте и напишите ваш вопрос в чат тех поддержки *здесь нужно вставить ссылку на чат тех поддержки*',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='Назад')]])
        )
        return 


def materials_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    data = update.callback_query.data
    if data == 'Назад':
        update.effective_chat.send_message('Вы нажали кнопку "Назад"')
        return start(update, context)
    
    if data == 'Карта форума':
        update.effective_chat.send_message('Вы нажали кнопку "Карта форума"')
        with open('/bot/files/forum_map.txt', 'rb') as file:
            update.effective_chat.send_document(file, filename=file.name)
        
    elif data == 'Программа форума':
        update.effective_chat.send_message('Вы нажали кнопку "Программа форума"')
        with open('/bot/files/forum_program.txt', 'rb') as file:
            update.effective_chat.send_document(file, filename=file.name)
        
    elif data == 'Правила форума':
        update.effective_chat.send_message('Вы нажали кнопку "Правила форума"')
        with open('/bot/files/forum_rules.txt', 'rb') as file:
            update.effective_chat.send_document(file, filename=file.name)
    
    # elif data == 'Материалы от спикеров':
    #     update.effective_chat.send_message('Вы нажали кнопку "Материалы от спикеров"')
    #     update.effective_chat.send_message('Здесь будет ссылка на виртуальный диск')
            
    return start(update, context)


def events_cat_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
        
    data = update.callback_query.data
    if data == 'Назад':
        update.effective_chat.send_message('Вы нажали кнопку "Назад"')
        return start(update, context)
    else:
        update.effective_chat.send_message(f'Вы нажали кнопку "{data}"')
        context.user_data['selected_event_cat'] = data
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('30 мая', callback_data='30.05.22'), InlineKeyboardButton('31 мая', callback_data='31.05.22')],
            [InlineKeyboardButton('1 июня', callback_data='01.06.22'), InlineKeyboardButton('2 июня', callback_data='02.06.22') ],
            [InlineKeyboardButton('3 июня', callback_data='03.06.22')],
            [InlineKeyboardButton('Назад', callback_data='Назад')],
        ])
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            'Выберите интересующий вас день',
            reply_markup=keyboard
        )
        return config.EVENTS_DAY


def events_day_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
        
    data = update.callback_query.data
    if data == 'Назад':
        update.effective_chat.send_message('Вы нажали кнопку "Назад"')
        return start(update, context)
    else:
        update.effective_chat.send_message(f'Вы выбрали дату "{data}"')
        context.user_data['selected_event_date'] = data
        category = context.user_data['selected_event_cat']
        
        start_dt = datetime.strptime(data + f' 00:00', '%d.%m.%y %H:%M')
        end = datetime.strptime(data + ' 23:59', '%d.%m.%y %H:%M')
        
        events = list(events_col.find({'category': category, 'dt': {"$gte": start_dt, "$lt": end}}))
        if not events:
            update.effective_chat.send_message(f'Для "{category}" на {data} еще не созданно ниодного события, попробуйте проверить позже')
            return start(update, context)
            
        context.user_data['selected_events'] = events
        text = ''
        keyboard = []
        line = []
        for index, event in enumerate(events):
            text += f'{index + 1}: {event["name"]}\nВремя: {event["dt"].time().isoformat()[:-3]}\n\n'
            line.append(InlineKeyboardButton(index + 1, callback_data=index + 1))
            if len(line) >= 5:
                keyboard.append(line.copy())
                line = []
                
            if index + 1 == len(events):
                keyboard.append(line.copy())
            
        keyboard.append([InlineKeyboardButton('Назад', callback_data='Назад')])
        context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return config.EVENTS_EVENT


def events_event_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
        
    data = update.callback_query.data
    event = context.user_data['selected_events'][int(data) - 1]
    context.user_data['selected_event'] = event
    text = f'Вы выбрали: {event["name"]}\n\n'\
        f'Описание: {event["desc"]}\n\n'\
        f'Дата проведения {event["dt"].date()}\n\n'\
        f'Время начала {event["dt"].time().isoformat()[:-3]}\n\n'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('Записаться на участие', callback_data='Записаться на участие')],
        [InlineKeyboardButton('Назад', callback_data='Назад')],
    ])
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        text,
        reply_markup=keyboard
    )
    return config.EVENT_CONFIRM


def event_confirm_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
        
    data = update.callback_query.data
    if data == 'Записаться на участие':
        if update.effective_chat.id in context.user_data['selected_event']['users']:
            update.effective_chat.send_message('Вы уже записаны на участие в этом событии')
        else:
            update.effective_chat.send_message('Вы успешно записались на участие')
            context.user_data['selected_event']['users'].append(update.effective_chat.id)
            events_col.update_one({'_id': context.user_data['selected_event']['_id']}, {'$set': {'users': context.user_data['selected_event']['users']}})
        return start(update, context)

    elif data == 'Назад':
        update.effective_chat.send_message('Вы нажали кнопку "Назад"')
        return start(update, context)


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


main_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        config.AUTH_CODE: [MessageHandler(Filters.text, auth_code)],
        config.USER_MENU: [CallbackQueryHandler(main_menu_callback)],
        config.MATERIALS: [CallbackQueryHandler(materials_callback)],
        config.EVENTS_CAT: [CallbackQueryHandler(events_cat_callback)],
        config.EVENTS_DAY: [CallbackQueryHandler(events_day_callback)],
        config.EVENTS_EVENT: [CallbackQueryHandler(events_event_callback)],
        config.EVENT_CONFIRM: [CallbackQueryHandler(event_confirm_callback)],
    },
    fallbacks=[
        CommandHandler('exit', _exit),
        MessageHandler(Filters.all, unknown)
        ],
    map_to_parent={}
)
