import logging
import sys

from django.conf import settings
from telegram import (Bot, BotCommand, InlineKeyboardButton,
                      InlineKeyboardMarkup, Update, user)
from telegram.error import Unauthorized
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Dispatcher, Filters, MessageHandler,
                          Updater)
from telegram_notification.celery import app
from youtube.models import ChannelUserItem, Channel

from telegram_bot.inline_handler import inline_handler
from telegram_bot.localization import localization
from youtube.utils import is_channel_url, scrape_id_by_url
from telegram_bot.handlers.bot_handlers.utils import get_inline_keyboard, log_errors, add
from telegram_bot.models import User, Message


@log_errors
def do_echo(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    try:
        echo_data = u.menu.split('‽')
    except Exception as e:
        echo_data = []

    if 'add' in echo_data:
        if is_channel_url(user_text):
            channel_id = scrape_id_by_url(user_text)

            keyboard = [
                [
                    InlineKeyboardButton(
                        'Yes' if u.language == 'en' else 'Да', callback_data=f'add‽{channel_id}‽yes'),
                    InlineKeyboardButton(
                        'No' if u.language == 'en' else 'Нет', callback_data=f'add‽{channel_id}')
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            User.set_menu_field(u)

            update.message.reply_text(
                text=localization[u.language]['echo'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            update.message.reply_text(
                text=localization[u.language]['echo'][1],
                parse_mode='HTML'
            )
    elif 'name' in echo_data:
        channel_id = u.menu.split('‽')[-1]
        add(channel_id, update, u, user_text)
    else:
        if is_channel_url(user_text):
            channel_id = scrape_id_by_url(user_text)
            channel = Channel.objects.filter(channel_url=user_text).first()
            if ChannelUserItem.objects.filter(user=u, channel=channel).exists():
                keyboard = [
                    [
                        InlineKeyboardButton(
                            'Check' if u.language == 'en' else 'Проверить', callback_data=f'echo‽{channel_id}‽check'),
                        InlineKeyboardButton(
                            'Remove' if u.language == 'en' else 'Удалить', callback_data=f'echo‽{channel_id}‽remove')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(
                    text=localization[u.language]['echo'][2],
                    parse_mode='HTML',
                    reply_markup=reply_markup)
            else:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            'Yes' if u.language == 'en' else 'Да', callback_data=f'echo‽{channel_id}‽yes'),
                        InlineKeyboardButton(
                            'No' if u.language == 'en' else 'Нет', callback_data=f'echo‽{channel_id}‽no')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(
                    text=localization[u.language]['echo'][3],
                    parse_mode='HTML',
                    reply_markup=reply_markup)
        else:
            pass


@log_errors
def do_start(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
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
        text=localization[u.language]['lang_start_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_remove(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    if ChannelUserItem.objects.filter(user=u):
        reply_markup = InlineKeyboardMarkup(
            get_inline_keyboard(u, 'remove', 0))

        update.message.reply_text(
            text=localization[u.language]['remove_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=localization[u.language]['remove_command'][1],
            parse_mode='HTML',
        )


@log_errors
def do_list(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    if ChannelUserItem.objects.filter(user=u):
        reply_markup = InlineKeyboardMarkup(
            get_inline_keyboard(u, 'list', 0, 'url'))

        update.message.reply_text(
            text=localization[u.language]['list_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=localization[u.language]['list_command'][1],
            parse_mode='HTML',
        )


@log_errors
def do_check(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    if ChannelUserItem.objects.filter(user=u):
        reply_markup = InlineKeyboardMarkup(get_inline_keyboard(u, 'check', 0))

        update.message.reply_text(
            text=localization[u.language]['check_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=localization[u.language]['check_command'][1],
            parse_mode='HTML',
        )


@log_errors
def do_lang(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(update.message.chat_id,
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
        text=localization[u.language]['lang_start_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_help(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    update.message.reply_text(
        text=localization[u.language]['help_command'][0],
        parse_mode='HTML'
    )


@log_errors
def do_add(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    User.set_menu_field(u, 'add')

    update.message.reply_text(
        text=localization[u.language]['add_command'][0],
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
