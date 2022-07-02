import asyncio
import platform
import sys
from typing import Dict

from django.conf import settings
from telegram import (Bot, BotCommand, InlineKeyboardButton,
                      InlineKeyboardMarkup, Update)
from telegram.error import Unauthorized
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Dispatcher, Filters, MessageHandler,
                          PreCheckoutQueryHandler, Updater)
from bellify.celery import app
from utils.keyboards import get_language_inline_keyboard

from bellify_bot.handlers.bot_handlers.echo_handler import echo_handler
from bellify_bot.handlers.bot_handlers.inline_handler import (
    inline_add_handler, inline_language_handler, inline_link_handler,
    inline_manage_handler, inline_pagination_handler, inline_start_handler,
    inline_tutorial_handler, inline_upgrade_handler)
from bellify_bot.handlers.bot_handlers.utils import (log_errors, manage,
                                                     upgrade)
from bellify_bot.localization import localization
from bellify_bot.models import Message, User, LANGUAGE_CHOICES


@log_errors
def start_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
                                      update.message.from_user.username)

    reply_markup = InlineKeyboardMarkup(
        get_language_inline_keyboard(command='start'))

    if not u.language:
        update.message.reply_text(
            text='\n'.join([localization[language[0]]['language_command'][0]
                           for language in LANGUAGE_CHOICES]),
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def manage_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    manage(update, u)


@log_errors
def language_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    reply_markup = InlineKeyboardMarkup(get_language_inline_keyboard())

    update.message.reply_text(
        text=localization[u.language]['language_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def help_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    localization[u.language]['help'][0][1], callback_data='tutorial'),
            ]
        ]
    )

    update.message.reply_text(
        text=localization[u.language]['help'][0][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def upgrade_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    upgrade(update.message, u)


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
    commands: Dict[str] = {
        'manage': 'Channels list ⚙️',
        'language': 'Change language 🌐',
        'help': 'Bot manual 📑',
        'upgrade': 'Upgrade profile ⭐'
    }

    langs_with_commands: Dict[str, Dict[str, str]] = {
        'ru': {
            'manage': 'Список каналов ⚙️',
            'language': 'Смена языка 🌐',
            'help': 'Мануал бота 📑',
            'upgrade': 'Прокачать профиль ⭐'
        },
        'uk': {
            'manage': 'Список каналів ⚙️',
            'language': 'Зміна мови 🌐',
            'help': 'Мануал бота 📑',
            'upgrade': 'Прокачати профіль ⭐'
        }
    }

    bot_instance.delete_my_commands()

    bot_instance.set_my_commands(
        commands=[
            BotCommand(command, description) for command, description in commands.items()
        ]
    )

    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', start_command_handler))
    dp.add_handler(CommandHandler('manage', manage_command_handler))
    dp.add_handler(CommandHandler('language', language_command_handler))
    dp.add_handler(CommandHandler('help', help_command_handler))
    dp.add_handler(CommandHandler('upgrade', upgrade_command_handler))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo_handler))
    dp.add_handler(CallbackQueryHandler(
        inline_language_handler, pattern=r'^language'))
    dp.add_handler(CallbackQueryHandler(
        inline_start_handler, pattern=r'^start'))
    dp.add_handler(CallbackQueryHandler(
        inline_tutorial_handler, pattern=r'^tutorial'))
    dp.add_handler(CallbackQueryHandler(
        inline_add_handler, pattern=r'^add'))
    dp.add_handler(CallbackQueryHandler(
        inline_link_handler, pattern=r'^link'))
    dp.add_handler(CallbackQueryHandler(
        inline_manage_handler, pattern=r'^manage'))
    dp.add_handler(CallbackQueryHandler(
        inline_upgrade_handler, pattern=r'^upgrade'))
    dp.add_handler(CallbackQueryHandler(
        inline_pagination_handler, pattern=r'^pagination'))
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
