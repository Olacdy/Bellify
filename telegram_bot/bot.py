import asyncio
import platform
import sys

from django.conf import settings
from telegram import Bot, InlineKeyboardMarkup, Update
from telegram.error import Unauthorized
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Dispatcher, Filters, MessageHandler,
                          Updater)
from telegram_notification.celery import app

from telegram_bot.handlers.bot_handlers.echo_handler import echo_handler
from telegram_bot.handlers.bot_handlers.inline_handler import inline_handler
from telegram_bot.handlers.bot_handlers.utils import (get_lang_inline_keyboard,
                                                      log_errors)
from telegram_bot.localization import localization
from telegram_bot.models import User


@log_errors
def do_start(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
                                      update.message.from_user.username)

    reply_markup = InlineKeyboardMarkup(
        get_lang_inline_keyboard(command='start'))

    update.message.reply_text(
        text=localization[u.language]['lang_start_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


def set_up_commands(bot_instance: Bot) -> None:
    bot_instance.delete_my_commands()
    # langs_with_commands = {
    #     'en': {
    #         'start': 'Start notification bot 🚀',
    #     },
    #     'ru': {
    #         'start': 'Запустить бота 🚀',
    #     }
    # }

    # for language_code in langs_with_commands:
    #     bot_instance.set_my_commands(
    #         language_code=language_code,
    #         commands=[
    #             BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
    #         ]
    #     )


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', do_start))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo_handler))
    dp.add_handler(CallbackQueryHandler(inline_handler))

    return dp


bot = Bot(settings.TOKEN)
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except Unauthorized:
    sys.exit(1)
n_workers = 4 if settings.DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(
    bot, update_queue=None, workers=n_workers, use_context=True))


def run_pooling():
    updater = Updater(settings.TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_pool = Bot(settings.TOKEN)

    if settings.DEBUG:
        set_up_commands(bot_pool)
    bot_info = bot_pool.get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    global bot, dispatcher
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)
