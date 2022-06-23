import asyncio
import platform
import sys
from typing import Dict

from django.conf import settings
from telegram import (Bot, BotCommand, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.error import Unauthorized
from telegram.ext import (CallbackContext, CallbackQueryHandler, PreCheckoutQueryHandler,
                          CommandHandler, Dispatcher, Filters, MessageHandler,
                          Updater)
from telegram_notification.celery import app

from telegram_bot.handlers.bot_handlers.echo_handler import echo_handler
from telegram_bot.handlers.bot_handlers.inline_handler import inline_handler
from telegram_bot.handlers.bot_handlers.utils import (_get_keyboard,
                                                      get_lang_inline_keyboard,
                                                      log_errors)
from telegram_bot.localization import localization
from telegram_bot.models import User


@log_errors
def start_callback(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
                                      update.message.from_user.username)

    reply_markup = InlineKeyboardMarkup(
        get_lang_inline_keyboard(command='start'))

    if u.language:
        update.message.reply_text(
            text=localization[u.language]['lang_start_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=f"{localization['en']['lang_start_command'][0]}\n{localization['ru']['lang_start_command'][0]}",
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def keyboard_callback(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
                                      update.message.from_user.username)

    reply_markup = ReplyKeyboardMarkup(_get_keyboard(u))

    update.message.reply_text(
        text=localization[u.language]['keyboard_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup
    )


@log_errors
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.pre_checkout_query.from_user.id,
                                      update.pre_checkout_query.from_user.username)

    query = update.pre_checkout_query

    payload_data = query.invoice_payload.split(
        f'{settings.SPLITTING_CHARACTER}')

    if payload_data[0] == 'youtube':
        if payload_data[-1] == 'premium':
            u.status = 'P'
        elif payload_data[-1].isdigit():
            u.max_youtube_channels_number += int(payload_data[-1])
        u.save()
        query.answer(ok=True)
    elif payload_data[0] == 'twitch':
        u.max_twitch_channels_number += int(payload_data[-1])
        u.save()
        query.answer(ok=True)
    else:
        query.answer(
            ok=False, error_message=localization[u.language]['upgrade'][7])


@log_errors
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
                                      update.message.from_user.username)

    update.message.reply_text(localization[u.language]['upgrade'][8])


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'keyboard': 'Get the keyboard ⌨️',
        },
        'ru': {
            'keyboard': 'Получить клавиатуру ⌨️',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', start_callback))
    dp.add_handler(CommandHandler('keyboard', keyboard_callback))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo_handler))
    dp.add_handler(CallbackQueryHandler(inline_handler))
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(MessageHandler(
        Filters.successful_payment, successful_payment_callback))

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
