import logging
import sys

from django.conf import settings
from telegram import (Bot, BotCommand, InlineKeyboardButton,
                      InlineKeyboardMarkup, Update)
from telegram.error import Unauthorized
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Dispatcher, Filters, MessageHandler,
                          Updater)
from telegram_notification.celery import app
from youtube.models import ChannelUserItem

from .inline_handler import inline_handler
from .localization import localization
from .utils import *


@log_errors
def do_echo(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)

    if 'add' in p.menu.split('‽'):
        user_text = update.message.text
        if is_channel_url(user_text):
            channel_id = scrape_id_by_url(user_text)

            keyboard = [
                [
                    InlineKeyboardButton(
                        'Yes' if p.language == 'en' else 'Да', callback_data=f'add‽{channel_id}‽yes'),
                    InlineKeyboardButton(
                        'No' if p.language == 'en' else 'Нет', callback_data=f'add‽{channel_id}')
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            set_menu_field(p)

            update.message.reply_text(
                text=localization[p.language]['echo'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            update.message.reply_text(
                text=localization[p.language]['echo'][1],
                parse_mode='HTML'
            )
    elif 'name' in p.menu.split('‽'):
        user_text = update.message.text
        channel_id = p.menu.split('‽')[-1]
        add(channel_id, update, p, user_text)


@log_errors
def do_start(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(update.message.chat_id,
                                 update.message.from_user.username)

    keyboard = [
        [
            InlineKeyboardButton(
                '🇬🇧', callback_data=f'lang‽en'),
            InlineKeyboardButton(
                '🇷🇺', callback_data=f'lang‽ru')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text=localization[p.language]['lang_start_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_remove(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    reply_markup = InlineKeyboardMarkup(get_inline_keyboard(p, 'remove', 0))

    if ChannelUserItem.objects.filter(user=p):
        update.message.reply_text(
            text=localization[p.language]['remove_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=localization[p.language]['remove_command'][1],
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def do_list(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    reply_markup = InlineKeyboardMarkup(
        get_inline_keyboard(p, 'list', 0, 'url'))

    if ChannelUserItem.objects.filter(user=p):
        update.message.reply_text(
            text=localization[p.language]['list_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=localization[p.language]['list_command'][1],
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def do_check(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    reply_markup = InlineKeyboardMarkup(get_inline_keyboard(p, 'check', 0))

    if ChannelUserItem.objects.filter(user=p):
        update.message.reply_text(
            text=localization[p.language]['check_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=localization[p.language]['check_command'][1],
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def do_lang(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(update.message.chat_id,
                                 update.message.from_user.username)

    keyboard = [
        [
            InlineKeyboardButton(
                '🇬🇧', callback_data=f'lang‽en'),
            InlineKeyboardButton(
                '🇷🇺', callback_data=f'lang‽ru')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text=localization[p.language]['lang_start_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_help(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    update.message.reply_text(
        text=localization[p.language]['help_command'][0],
        parse_mode='HTML'
    )


@log_errors
def do_add(update: Update, context: CallbackContext) -> None:
    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    set_menu_field(p, 'add')

    update.message.reply_text(
        text=localization[p.language]['add_command'][0],
        parse_mode='HTML'
    )


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands = {
        'en': {
            'start': 'Start notification bot 🚀',
            'add': 'Add channel by it\'s URL',
            'remove': 'Remove channel from list',
            'check': 'Check channel from list',
            'list': 'List of saved channels',
            'help': 'Useguide for bot',
            'lang': 'For language change'
        },
        'ru': {
            'start': 'Запустить бота 🚀',
            'add': 'Добавление канала с помощью URL',
            'remove': 'Удалить канал из списка',
            'check': 'Проверить канал из списка',
            'list': 'Список сохраненных каналов',
            'help': 'Справка',
            'lang': 'Смена языка'
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
    dp.add_handler(CommandHandler('add', do_add))
    dp.add_handler(CommandHandler('remove', do_remove))
    dp.add_handler(CommandHandler('check', do_check))
    dp.add_handler(CommandHandler('list', do_list))
    dp.add_handler(CommandHandler('help', do_help))
    dp.add_handler(CommandHandler('start', do_start))
    dp.add_handler(CommandHandler('lang', do_lang))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, do_echo))
    dp.add_handler(CallbackQueryHandler(inline_handler))

    return dp


bot = Bot(settings.TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except Unauthorized:
    sys.exit(1)
n_workers = 0 if settings.DEBUG else 4
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
