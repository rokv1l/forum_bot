
from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CommandHandler, CallbackContext

import config
from src.utils import delete_keyboard, admin_menu, get_one_button_keyboard, get_one_line_keyboard
from src.database import quest_col, users_col


def support_callback(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    questions = list(quest_col.find({'who_answer': {'tg_id': '', 'full_name': ''}}))
    if not questions:
        update.effective_chat.send_message('В данный момент нет неотвеченных вопросов')
        return admin_menu(update, context)
    
    context.user_data['questions'] = questions
    cursor = context.user_data['quest_cursor'] = 0
        
    text = f'Вопрос ({cursor + 1} из {len(questions)})'\
        f'Вопрос задал: {questions[cursor]["who_ask"]["full_name"]}\n\n'\
        f'Категория вопроса: {questions[cursor]["category"]}\n\n'\
        f'Вопрос: {questions[cursor]["question"]}'
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('<', callback_data='<'),
            InlineKeyboardButton('Ответить', callback_data='answer'),
            InlineKeyboardButton('>', callback_data='>')
        ],
        [
            InlineKeyboardButton('Назад', callback_data='Назад')
        ],
    ])
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        text,
        reply_markup=keyboard
    )
    return config.SUPPORT_SELECT_QUEST


def select_quest_callback(update, context):
    data = update.callback_query.data
    if data == 'Назад':
        if 'msg_for_del_keys' in context.user_data:
            delete_keyboard(context, update.effective_chat.id)
        return admin_menu(update, context)
    
    elif data == 'answer':
        return asnwer(update, context)
    
    else:
        pagination(update, context)


def asnwer(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
        
    cursor = context.user_data['quest_cursor']
    questions = context.user_data['questions']
    quest = context.user_data['question'] = quest_col.find_one({'_id': questions[cursor]['_id']})
    if quest['who_answer'] != {'who_answer': {'tg_id': '', 'full_name': ''}}:
        update.effective_chat.send_message('На этот вопрос уже отвечает кто-то другой, выберите себе другой вопрос')
        return support_callback(update, context)
    
    else:
        del context.user_data['quest_cursor']
        del context.user_data['questions']
        update.effective_chat.send_message('Напишите ответ и бот доставит его пользователю задавшему вопрос')
        return config.SUPPORT_ANSWER_QUEST_CONFIRM


def pagination(update, context):
    data = update.callback_query.data
    cursor = context.user_data['quest_cursor']
    questions = context.user_data['questions']
    if data == '<':
        cursor -= 1
        if cursor > len(questions):
            cursor = context.user_data['quest_cursor'] = 0
        
        text = f'Вопрос ({cursor + 1} из {len(questions)})'\
            f'Вопрос задал: {questions[cursor]["who_ask"]["full_name"]}\n\n'\
            f'Категория вопроса: {questions[cursor]["category"]}\n\n'\
            f'Вопрос: {questions[cursor]["question"]}'
               
    elif data == '>':
        cursor -= 1
        if cursor < 0:
            cursor = context.user_data['quest_cursor'] = len(questions) - 1
        
        text = f'Вопрос ({cursor + 1} из {len(questions)})'\
            f'Вопрос задал: {questions[cursor]["who_ask"]["full_name"]}\n\n'\
            f'Категория вопроса: {questions[cursor]["category"]}\n\n'\
            f'Вопрос: {questions[cursor]["question"]}'

    context.user_data['quest_cursor'] = cursor
    update.callback_query.message.edit_text(text)


def asnwer_quest_confirm_callback(update, context):
    context.user_data['sup_text'] = update.message.text 
    update.effective_chat.send_message(
        'Вы уверены что хотите отправить этот ответ?',
        reply_markup=get_one_line_keyboard(['Да', 'Нет'])
    )
    return config.SUPPORT_ANSWER_QUEST


def asnwer_quest_callback(update, context: CallbackContext):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    data = update.callback_query.data
    if data == 'Да':
        quest = context.user_data['question']
        user = users_col.find({'tg_id': update.effective_chat.id})[0]
        
        text = f'На ваш вопрос ответил {user["full_name"]}\n\nОтвет: {quest["question"]}'
        try:
            context.bot.send_message(chat_id=quest['who_ask']['tg_id'], text=text)
        except:
            update.effective_chat.send_message(
                'По какой-то причине пользователь не смог получить ваш ответ. '\
                'Это может случиться изза того что пользователь заблокировал бота'
                )
        else:
            update.effective_chat.send_message('Пользователь получил ваш ответ')
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


support_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=support_callback, pattern=r'qna_support')
    ],
    states={
        config.SUPPORT_SELECT_QUEST: [CallbackQueryHandler(callback=select_quest_callback)],
        config.SUPPORT_ANSWER_QUEST_CONFIRM: [MessageHandler(Filters.text ,asnwer_quest_confirm_callback)],
        config.SUPPORT_ANSWER_QUEST: [CallbackQueryHandler(callback=asnwer_quest_callback)],
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