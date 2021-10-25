from datetime import datetime
from django.conf import settings
from telegram import Bot, BotCommand, Update
from telegram.error import Unauthorized
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater, Dispatcher, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from youtube.models import Channel, ChannelUserItem
from .utils import *
from telegram_notification.celery import app
from typing import Optional
import sys
import logging


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Exception occured {e}'
            print(error_message)
            raise e

    return inner


@log_errors
def add(url: str, update: Update, p: Profile, name: Optional[str] = None) -> None:
    lang_for_add = {
        'eng':
            [
                ['New channel added with name', '. \nLast video is'],
                'Unable to add a new channel, because one with the same name already exists. \nTry to come up with a new name or leave the name parameter empty.',
                'This channel is already added to Your profile! \nLast video is',
                'Sorry, can`t recognize this format.'
            ],
        'rus':
            [
                ['Новый канал под именем', 'был добавлен.\nПоследнее видео'],
                'Невозможно добавить новый канал под этим именем.\nПопробуйте придумать новое имя или оставить параметр имени пустым.',
                'Этот канал уже добавлен к вашему профилю!\nПоследнее видео',
                'Извините, нераспознанный формат.'
            ]
    }

    channel_id = get_channel_id_by_url(url)
    video_title, video_url, upload_time = get_last_video(channel_id)
    channel_name = name if name else get_channel_title(
        channel_id)
    channel, _ = Channel.objects.get_or_create(
        channel_url=url,
        defaults={
            'title': channel_name,
            'channel_id': channel_id,
            'video_title': video_title,
            'video_url': video_url,
            'video_publication_date': datetime.strptime(upload_time, "%m/%d/%Y, %H:%M:%S")
        }
    )
    if not p in channel.users.all():
        if not ChannelUserItem.objects.filter(user=p, channel_title=channel_name).exists():
            ChannelUserItem.objects.create(
                user=p, channel=channel, channel_title=channel_name)
            update.message.reply_text(
                text=f"{lang_for_add[p.language][0][0]} {channel_name} {lang_for_add[p.language][0][1]} <a href=\"{video_url}\">{video_title}</a>.",
                parse_mode='HTML'
            )
            return
        else:
            update.message.reply_text(
                text=lang_for_add[p.language][1],
                parse_mode='HTML'
            )
    else:
        update.message.reply_text(
            text=f"{lang_for_add[p.language][2]} <a href=\"{video_url}\">{video_title}</a>.",
            parse_mode='HTML'
        )


@log_errors
def remove(update: Update, p: Profile, name: str):
    lang_for_remove = {
        'eng':
            [
                'Sorry. There is no such channel added right now, maybe try using /add command.',
                'Your record was deleted successfully.'
            ],
        'rus':
            [
                'Извините, но данного канала не существует, попробуйте добавить новый с помощью /add.',
                'Ваш канал успешно удален.'
            ]
    }
    try:
        item = ChannelUserItem.objects.get(user=p, channel_title=name)
    except ChannelUserItem.DoesNotExist:
        update.message.reply_text(
            text=lang_for_remove[p.language][0],
            parse_mode='HTML'
        )
        return
    item.delete()
    update.message.reply_text(
        text=lang_for_remove[p.language][1],
        parse_mode='HTML'
    )


@log_errors
def check(update: Update, p: Profile, name: str):
    lang_for_check = {
        'eng':
        [
            'Sorry. There is no channels added right now, maybe try using /add command.',
            'No new video on this channel. \nLast video is'
        ],
        'rus':
        [
            'Извините, но данного канала не существует, попробуйте добавить новый с помощью /add.',
            'Новых видео нету на этом канале, Последнее видео'
        ]
    }
    try:
        item = ChannelUserItem.objects.get(user=p, channel_title=name)
    except ChannelUserItem.DoesNotExist:
        update.message.reply_text(
            text=lang_for_check[p.language][0],
            parse_mode='HTML'
        )
        return
    if not check_for_new_video(item.channel):
        update.message.reply_text(
            text=f'{lang_for_check[p.language][1]} <a href=\"{item.channel.video_url}\">{item.channel.video_title}</a>.',
            parse_mode='HTML'
        )


@log_errors
def do_echo(update: Update, context: CallbackContext) -> None:
    lang_for_echo = {
        'eng':
            [
                'Now send URL of a channel:',
                'This doesn`t look like a URL 🤔. Try again.',
                'Unknown command.'
            ],
        'rus':
            [
                'Теперь можете прислать URL канала:',
                'Что-то не похоже на URL 🤔. Попробуйте еще раз.',
                'Нераспознанная команда.'
            ]
    }
    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(
        chat_id, update.message.from_user.username, False)

    if p.menu == 'add':
        user_text = update.message.text
        if is_channel_url(user_text):
            add(user_text, update, p)
            set_menu_field(p)
        else:
            set_menu_field(p, f'add_{user_text}')
            update.message.reply_text(
                text=lang_for_echo[p.language][0],
                parse_mode='HTML'
            )
    elif '_' in p.menu:
        name = p.menu.split('_')[1]
        user_text = update.message.text
        if is_channel_url(user_text):
            add(user_text, update, p, name)
            set_menu_field(p)
        else:
            update.message.reply_text(
                text=lang_for_echo[p.language][1],
                parse_mode='HTML'
            )
    elif p.menu == 'check':
        name = update.message.text
        check(update, p, name)
        set_menu_field(p)
    elif p.menu == 'remove':
        name = update.message.text
        remove(update, p, name)
        set_menu_field(p)
    else:
        update.message.reply_text(
            text=lang_for_echo[p.language][2],
            parse_mode='HTML'
        )


@log_errors
def do_start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    p, _ = get_or_create_profile(chat_id, username)

    keyboard = [
        [
            InlineKeyboardButton(
                '🇬🇧', callback_data=f'eng_{chat_id}_{username}'),
            InlineKeyboardButton(
                '🇷🇺', callback_data=f'rus_{chat_id}_{username}')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text='<b>Пожалуйста, выберите язык</b>\n'
             '<b>Please, choose language:</b>',
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def language_button(update: Update, context: CallbackContext) -> None:
    lang_for_lang_button = {
        'eng': 'Thanks, You`ll continue work on English',
        'rus': 'Спасибо, теперь работа будет продолжена на русском'
    }

    query = update.callback_query

    query.answer()

    p, _ = get_or_create_profile(query.data.split(
        '_')[1], query.data.split(
        '_')[2])

    p.language = query.data.split('_')[0]
    p.save()

    query.edit_message_text(
        text=lang_for_lang_button[query.data.split('_')[0]],
        parse_mode='HTML')


@log_errors
def do_remove(update: Update, context: CallbackContext):
    lang_for_remove_command = {
        'eng':
            [
                'Now send the name of an added channel.'
            ],
        'rus':
            [
                'Пришлите имя вашего канала.'
            ]
    }

    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(chat_id, update.message.from_user.username)

    if context.args:
        name = ' '.join(context.args)
        remove(update, p, name)
    else:
        set_menu_field(p, 'remove')
        update.message.reply_text(
            text=lang_for_remove_command[p.language][0],
            parse_mode='HTML'
        )


@log_errors
def do_list(update: Update, context: CallbackContext):
    lang_for_list = {
        'eng':
            [
                'List of Your added channels',
                'Sorry. There is no channels added right now, maybe try using /add command.'
            ],
        'rus':
            [
                'Список добавленных вами каналов',
                'Извините, но данного канала не существует, попробуйте добавить новый с помощью /add.',
            ]
    }

    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(chat_id, update.message.from_user.username)

    items = ChannelUserItem.objects.filter(user=p)
    if items:
        c_list = [
            f'<a href=\"{item.channel.channel_url}\"><b>{item.channel_title}</b></a> - <a href=\"{item.channel.video_url}\"><b>{item.channel.video_title}</b></a>\n' for item in items]
        update.message.reply_text(
            text=f'{lang_for_list[p.language][0]}:\n\n' + ''.join(c_list),
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    else:
        update.message.reply_text(
            text=lang_for_list[p.language][1],
            parse_mode='HTML'
        )


@log_errors
def do_check(update: Update, context: CallbackContext):
    lang_for_check_command = {
        'eng':
            [
                'Now send the name of an added channel.'
            ],
        'rus':
            [
                'Пришлите имя вашего канала.'
            ]
    }

    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(chat_id, update.message.from_user.username)

    if context.args:
        name = ' '.join(context.args)
        check(update, p, name)
    else:
        set_menu_field(p, 'check')
        update.message.reply_text(
            text=lang_for_check_command[p.language][0],
            parse_mode='HTML'
        )


@log_errors
def do_lang_change(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    keyboard = [
        [
            InlineKeyboardButton(
                '🇬🇧', callback_data=f'eng_{chat_id}_{username}'),
            InlineKeyboardButton(
                '🇷🇺', callback_data=f'rus_{chat_id}_{username}')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text='<b>Пожалуйста, выберите язык</b>\n'
             '<b>Please, choose language:</b>',
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def do_help(update: Update, context: CallbackContext):
    lang_for_help = {
        'eng':
            [
                'Notification Bot manual.\n\nTo start type /add command with some YouTube channel URL.\nNow, if everything went smoothly🤞, You should have this channel in our database.\nTry to check whether it is true and type /list command.\nTo check if there is a new video on this channel try to use /check + name of the channel command.\nThis way You can get fresh information about the latest video from this channel,\nbut don`t worry You`ll be getting notifications automatically if a new video is out there.\nTo remove some channels, just type /remove + name of the channel command.\n\nNow You are free to add any channel from YouTube and this bot will take care of notifying You about new videos.\n\nTo contact developer follow this link: https://t.me/golovakanta'
            ],
        'rus':
            [
                'Notification Bot мануал.\n\nЧтобы начать пользоваться ботом, воспользуйтесь коммандой /add плюс ссылка на ютуб канал.\nТеперь, если ничего не сломалось🤞, этот канал будет добавлен в нашу базу данных.\nПопробуйте проверить так ли это и напишите комманду /list.\nЧтобы проверить появилось ли новое видео, воспользуйтесь коммандой /check плюс имя канала, которое было в списке.\nТак вы можете получать последнюю информацию касательно последнего видео на канале,\nоднако не волнуйтесь, вы все еще будете получать сообщения от этого бота автоматически, как только мы заметим новое видео на одном из добавленных вами каналов.\nДля того чтобы удалить какой-либо канал, используйте комманду /remove плюс имя канала.\n\nТеперь, когда вы знаете основную функциональности бота, можете добавлять любой интересующий вас канал, а бот позаботится о том, чтобы снабжать вас актуальной информацией относительно последнего видео на канале.\nДля связи с разработчиком: https://t.me/golovakanta'
            ]
    }

    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(chat_id, update.message.from_user.username)

    update.message.reply_text(
        text=lang_for_help[p.language][0],
        parse_mode='HTML'
    )


@log_errors
def do_add(update: Update, context: CallbackContext):
    lang_for_add_command = {
        'eng':
        [
            'Unknown format. Try again /add + channel`s URL, name (optional).',
            'Now send channel`s name or URL, then channel`s name will be set by bot.'
        ],
        'rus':
        [
            'Нераспознанный формат. Попробуйте снова /add + URL канала, имя (необязательно).',
            'Теперь можете написать имя нового канал или же прислать URL канала, тогда оно будет определено автоматически.'
        ]
    }
    chat_id = update.message.chat_id

    p, _ = get_or_create_profile(chat_id, update.message.from_user.username)

    if context.args:
        if len(context.args) > 1:
            for arg in context.args:
                if is_channel_url(arg):
                    url = arg
                    break
            if url:
                args = context.args
                args.remove(url)
                name = ' '.join(args)
                print(url, name)
                add(url, update, p, name)
            else:
                update.message.reply_text(
                    text=lang_for_add_command[p.language][0],
                    parse_mode='HTML'
                )
        elif len(context.args) == 1 and is_channel_url(context.args[0]):
            url = context.args[0]
            add(url, update, p)
        else:
            update.message.reply_text(
                text=lang_for_add_command[p.language][0],
                parse_mode='HTML'
            )
    else:
        set_menu_field(p, 'add')
        update.message.reply_text(
            text=lang_for_add_command[p.language][1],
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


bot = Bot(settings.TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except Unauthorized:
    sys.exit(1)


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
    dp.add_handler(CommandHandler('lang', do_lang_change))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, do_echo))
    dp.add_handler(CallbackQueryHandler(language_button))

    return dp


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
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


n_workers = 0 if settings.DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
