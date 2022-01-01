from django.conf import settings
from telegram import Bot, BotCommand, Update
from telegram.error import Unauthorized
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater, Dispatcher, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from youtube.models import ChannelUserItem
from .utils import *
from telegram_notification.celery import app
import sys
from .inline_handler import inline_handler
import logging


@log_errors
def do_echo(update: Update, context: CallbackContext) -> None:
    lang_for_echo = {
        'en':
            [
                'This doesn\'t look like a URL 🤔. Try again.',
                'Do You want to change channel\'s name?'
            ],
        'ru':
            [
                'Что-то не похоже на URL 🤔. Попробуйте еще раз.',
                'Хотите ли вы изменить имя канала?'
            ]
    }

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
                text=lang_for_echo[p.language][1],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            update.message.reply_text(
                text=lang_for_echo[p.language][0],
                parse_mode='HTML'
            )
    elif 'name' in p.menu.split('‽'):
        user_text = update.message.text
        channel_id = p.menu.split('‽')[-1]
        add(channel_id, update, p, user_text)


@log_errors
def do_start(update: Update, context: CallbackContext) -> None:
    lang_for_start_command = {
        'en':
            [
                'Please, select a language.'
            ],
        'ru':
            [
                'Пожалуйста, выберите язык.'
            ]
    }
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
        text=lang_for_start_command[p.language][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_remove(update: Update, context: CallbackContext) -> None:
    lang_for_remove_command = {
        'en':
            [
                'Select a channel that You would like to remove.',
                'Sorry. There is no channels added right now, maybe try using /add command.'
            ],
        'ru':
            [
                'Выберите канал, который вы хотите удалить.',
                'Извините, пока у вас нет никаких каналов, попробуйте добавить новый с помощью /add.'
            ]
    }

    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    keyboard = []

    for channel in ChannelUserItem.objects.filter(user=p)[0: settings.PAGINATION_SIZE]:
        keyboard.append([
            InlineKeyboardButton(
                f'{channel.channel_title}', callback_data=f'remove‽{channel.channel.channel_id}')
        ])

    keyboard.append([InlineKeyboardButton('❯', callback_data=f'remove‽pagination‽{1}')]) if len(
        ChannelUserItem.objects.filter(user=p)) > settings.PAGINATION_SIZE else None

    reply_markup = InlineKeyboardMarkup(keyboard)

    if ChannelUserItem.objects.filter(user=p):
        update.message.reply_text(
            text=lang_for_remove_command[p.language][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=lang_for_remove_command[p.language][1],
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def do_list(update: Update, context: CallbackContext) -> None:
    lang_for_list_command = {
        'en':
            [
                'List of Your added channels',
                'Sorry. There is no channels added right now, maybe try using /add command.'
            ],
        'ru':
            [
                'Список добавленных вами каналов',
                'Извините, пока у вас нет никаких каналов, попробуйте добавить новый с помощью /add.',
            ]
    }

    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    keyboard = []

    for channel in ChannelUserItem.objects.filter(user=p)[0: settings.PAGINATION_SIZE]:
        keyboard.append([
            InlineKeyboardButton(
                f'{channel.channel_title}', url=channel.channel.channel_url)
        ])

    keyboard.append([InlineKeyboardButton('❯', callback_data=f'list‽pagination‽{1}')]) if len(
        ChannelUserItem.objects.filter(user=p)) > settings.PAGINATION_SIZE else None

    reply_markup = InlineKeyboardMarkup(keyboard)

    if ChannelUserItem.objects.filter(user=p):
        update.message.reply_text(
            text=lang_for_list_command[p.language][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=lang_for_list_command[p.language][1],
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def do_check(update: Update, context: CallbackContext) -> None:
    lang_for_check_command = {
        'en':
            [
                'Select a channel that You would like to check.',
                'Sorry. There is no channels added right now, maybe try using /add command.'
            ],
        'ru':
            [
                'Выберите канал, который вы хотите проверить.',
                'Извините, пока у вас нет никаких каналов, попробуйте добавить новый с помощью /add.',
            ]
    }

    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    keyboard = []

    for channel in ChannelUserItem.objects.filter(user=p)[0: settings.PAGINATION_SIZE]:
        keyboard.append([
            InlineKeyboardButton(
                f'{channel.channel_title}', callback_data=f'check‽{channel.channel.channel_id}')
        ])

    keyboard.append([InlineKeyboardButton('❯', callback_data=f'check‽pagination‽{1}')]) if len(
        ChannelUserItem.objects.filter(user=p)) > settings.PAGINATION_SIZE else None

    reply_markup = InlineKeyboardMarkup(keyboard)

    if ChannelUserItem.objects.filter(user=p):
        update.message.reply_text(
            text=lang_for_check_command[p.language][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=lang_for_check_command[p.language][1],
            parse_mode='HTML',
            reply_markup=reply_markup)


@log_errors
def do_lang(update: Update, context: CallbackContext) -> None:
    lang_for_lang_command = {
        'en':
            [
                'Please, select language.'
            ],
        'ru':
            [
                'Пожалуйста, выберите язык.'
            ]
    }
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
        text=lang_for_lang_command[p.language][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_help(update: Update, context: CallbackContext) -> None:
    lang_for_help = {
        'en':
            [
                'Notification Bot manual.\n\nTo start type /add command with some YouTube channel URL.\nNow, if everything went smoothly🤞, You should have this channel in our database.\nTry to check whether it is true and type /list command.\nTo check if there is a new video on this channel try to use /check + name of the channel command.\nThis way You can get fresh information about the latest video from this channel,\nbut don`t worry You`ll be getting notifications automatically if a new video is out there.\nTo remove some channels, just type /remove + name of the channel command.\n\nNow You are free to add any channel from YouTube and this bot will take care of notifying You about new videos.\n\nTo contact developer follow this link: https://t.me/golovakanta'
            ],
        'ru':
            [
                'Notification Bot мануал.\n\nЧтобы начать пользоваться ботом, воспользуйтесь коммандой /add плюс ссылка на ютуб канал.\nТеперь, если ничего не сломалось🤞, этот канал будет добавлен в нашу базу данных.\nПопробуйте проверить так ли это и напишите комманду /list.\nЧтобы проверить появилось ли новое видео, воспользуйтесь коммандой /check плюс имя канала, которое было в списке.\nТак вы можете получать последнюю информацию касательно последнего видео на канале,\nоднако не волнуйтесь, вы все еще будете получать сообщения от этого бота автоматически, как только мы заметим новое видео на одном из добавленных вами каналов.\nДля того чтобы удалить какой-либо канал, используйте комманду /remove плюс имя канала.\n\nТеперь, когда вы знаете основные функциональности бота, вы можете добавлять любой интересующий вас канал, а бот позаботится о том, чтобы снабжать вас актуальной информацией относительно последнего видео на канале.\nДля связи с разработчиком: https://t.me/golovakanta'
            ]
    }

    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(chat_id, update.message.from_user.username)

    update.message.reply_text(
        text=lang_for_help[p.language][0],
        parse_mode='HTML'
    )


@log_errors
def do_add(update: Update, context: CallbackContext) -> None:
    lang_for_add_command = {
        'en':
            [
                'Now send channel\'s URL.'
            ],
        'ru':
            [
                'Теперь можете прислать URL канала.'
            ]
    }

    p, _ = get_or_create_profile(
        update.message.chat_id, update.message.from_user.username)

    set_menu_field(p, 'add')

    update.message.reply_text(
        text=lang_for_add_command[p.language][0],
        parse_mode='HTML'
    )


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands = {
        'en': {
            'start': 'Start notification bot 🚀',
            'add': '+ Channel url, name (optional)',
            'remove': '+ Channel name',
            'check': '+ Channel name',
            'list': 'List of saved channels',
            'help': 'Useguide for bot',
            'lang': 'For language change'
        },
        'ru': {
            'start': 'Запустить бота 🚀',
            'add': '+ Ссылка на канал, имя канала (необязательно)',
            'remove': '+ Имя канала',
            'check': '+ Имя канала',
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
    """
    Adding handlers for events from Telegram
    """
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
    """ Run bot in pooling mode """
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
