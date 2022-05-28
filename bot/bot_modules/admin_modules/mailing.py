from loguru import logger
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

import config
from src.utils import delete_keyboard, admin_menu, get_one_button_keyboard, get_one_line_keyboard
from src.database import users_col


def ask_message(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Введите сообщение для рассылки',
        reply_markup=get_one_button_keyboard('Назад')
    )
    return config.MESSAGE_CONFIRM


def message_confirm(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    if update.callback_query and update.callback_query.data == 'Назад':
        return admin_menu(update, context)
    
    context.user_data['message_for_mailing'] = update.message.text
    context.user_data['msg_for_del_keys'] = update.effective_chat.send_message(
        'Вы уверены что хотите сделать рассылку с этим сообщением?',
        reply_markup=get_one_line_keyboard(['Да', 'Нет'])
    )
    return config.MAILING


def mailing(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)
    
    if update.callback_query and update.callback_query.data == 'Да':
        logger.info(
            f'User making mailing. Text {context.user_data["message_for_mailing"]} '
            f'id: {update.effective_chat.id} '
            f'fullname: {update.effective_chat.full_name}'
        )
        mailing_list = list(users_col.find())
        for user in mailing_list:
            if user == update.effective_chat.id:
                continue
            try:
                context.bot.send_message(
                    chat_id=user['tg_id'],
                    text=context.user_data['message_for_mailing']
                )
            except Exception:
                update.effective_chat.send_message(
                    f'Пользователь ({user["tg_id"]}, {user["username"] + "," if user["username"] else ""}) '\
                    f'по какой-то причине не смог получить сообщение'
                )
        update.effective_chat.send_message('✅Рассылка проведена✅')
    else:
        update.effective_chat.send_message('⛔️Рассылка Отменена⛔️')
        
    return admin_menu(update, context)


def unknown(update, context):
    update.effective_chat.send_message(
        'Вы ввели неизвестную команду.\n'\
        'Если что-то пошло не так то воспользуйтесь /exit для сброса диалогов к началу'
    )


def _exit(update, context):
    if 'msg_for_del_keys' in context.user_data:
        delete_keyboard(context, update.effective_chat.id)

    update.effective_chat.send_message('Вы вышли из всех диалогов, для использования бота используйте /start')
    return ConversationHandler.END


mailing_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=ask_message, pattern=r'mailing')
    ],
    states={
        config.MESSAGE_CONFIRM: [
            MessageHandler(Filters.text, message_confirm),
            CallbackQueryHandler(callback=message_confirm)
            ],
        config.MAILING: [CallbackQueryHandler(callback=mailing)],
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