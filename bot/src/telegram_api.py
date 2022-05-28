from telegram.ext import Updater

import config


updater = Updater(token=config.token, use_context=True)
dispatcher = updater.dispatcher
