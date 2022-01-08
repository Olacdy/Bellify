import re
from datetime import datetime
from typing import Optional

import bs4 as soup
import requests
import scrapetube
import telegram_notification.tasks as tasks
from dateutil import parser
from django.conf import settings
from telegram import InlineKeyboardButton, Update
from youtube.models import Channel, ChannelUserItem

from telegram_bot.models import Profile

from .localization import localization


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Exception occured {e}'
            print(error_message)
            raise e

    return inner


# Gets last video from given channel by it`s id
def get_last_video(channel_id: str):
    playlist_id = channel_id[:1] + 'U' + channel_id[2:]
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=5&key={settings.YOUTUBE_API_KEY}')
    try:
        title = api_response.json()['items'][0]['snippet']['title']
        publication_date = parser.parse(api_response.json(
        )['items'][0]['snippet']['publishedAt']).strftime("%m/%d/%Y, %H:%M:%S")
        url = f"https://www.youtube.com/watch?v={api_response.json()['items'][0]['snippet']['resourceId']['videoId']}"
    except Exception as e:
        videos = scrapetube.get_channel(channel_id)
        video_id = [video['videoId'] for video in videos][0]
        api_response = requests.get(
            f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={settings.YOUTUBE_API_KEY}')
        try:
            title = api_response.json()['items'][0]['snippet']['title']
            publication_date = parser.parse(api_response.json()['items'][0]['snippet']['publishedAt']).strftime(
                "%m/%d/%Y, %H:%M:%S")
            url = f"https://www.youtube.com/watch?v={video_id}"
        except:
            channel = Channel.objects.get(channel_id=channel_id)
            title = channel.title
            publication_date = channel.video_publication_date
            url = channel.video_url
    return title, url, publication_date


# Gets channel title from given channel id
def get_channel_title(channel_id: str):
    playlist_id = channel_id[:1] + 'U' + channel_id[2:]
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=5&key={settings.YOUTUBE_API_KEY}')
    try:
        channel_title = api_response.json(
        )['items'][0]['snippet']['channelTitle']
    except:
        videos = scrapetube.get_channel(channel_id)
        video_id = [video['videoId'] for video in videos][0]
        api_response = requests.get(
            f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={settings.YOUTUBE_API_KEY}')
        channel_title = api_response.json(
        )['items'][0]['snippet']['channelTitle']
    return channel_title


# Checks if given string is youtube channel url
def is_channel_url(string: str):
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:c|user|channel)/([\%\w-]+)(?:[/]*)', string))


# Checks if channels identifier is channel id
def is_id_in_url(string: str):
    try:
        ident = get_identifier_from_url(string)
    except:
        return False
    return bool(re.search(r'UC[\w-]+', ident))


# Gets identifier from url
def get_identifier_from_url(string: str):
    return re.findall(r'http[s]*://(?:www\.)?youtube.com/(?:c|user|channel)/([\%\w-]+)(?:[/]*)', string)[0]


# Scrapes channel id from url
def scrape_id_by_url(url: str):
    session = requests.Session()
    response = session.get(url)
    if "uxe=" in response.request.url:
        session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
        response = session.get(url)
    session.close()

    html = soup.BeautifulSoup(response.text, 'lxml')
    return html.find('meta', {'itemprop': 'channelId'})['content']


# Gets or create profile from chat_id and username
def get_or_create_profile(chat_id: str, name: str, reset: Optional[bool] = True):
    profile_data = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': name,
            'language': 'en',
        }
    )
    if reset:
        set_menu_field(profile_data[0])
    return profile_data


# Sets value for menu field in Profile model
def set_menu_field(p: Profile, value: Optional[str] = '') -> None:
    p.menu = value
    p.save()


# Sends message to user by chat_id
def send_message(chat_id: str, bot_message: str, parse_mode: Optional[str] = 'HTML'):
    send_text = 'https://api.telegram.org/bot' + str(settings.TOKEN) + \
        '/sendMessage?chat_id=' + str(chat_id) + '&text=' + \
        bot_message + '&parse_mode=' + parse_mode
    requests.get(send_text)


# Checks for new video and alerts every user if there is one
def check_for_new_video(channel: Channel):
    new_video_title, new_video_url, new_upload_time = get_last_video(
        channel.channel_id)

    if new_video_url != channel.video_url:
        channel.video_title = new_video_title
        channel.video_url = new_video_url
        channel.video_publication_date = datetime.strptime(
            new_upload_time, "%m/%d/%Y, %H:%M:%S")
        channel.save()
        users = [item.user for item in ChannelUserItem.objects.filter(
            channel=channel)]
        tasks.notify_users(users, channel)
        return True
    else:
        return False


def get_inline_keyboard(p: Profile, command: str, page_num: int, buttons_mode: Optional[str] = 'callback_data'):
    keyboard = []
    pagination_button_set = []

    channels = [ChannelUserItem.objects.filter(
        user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

    if buttons_mode == 'url':
        for channel in channels[page_num]:
            keyboard.append([
                InlineKeyboardButton(
                    f'{channel.channel_title}', url=channel.channel.channel_url)
            ])
    else:
        for channel in channels[page_num]:
            keyboard.append([
                InlineKeyboardButton(
                    f'{channel.channel_title}', callback_data=f'{command}‽{channel.channel.channel_id}')
            ])

    pagination_button_set.append(InlineKeyboardButton(
        '❮', callback_data=f'{command}‽pagination‽{page_num - 1}')) if page_num - 1 >= 0 else None
    pagination_button_set.append(InlineKeyboardButton(
        '❯', callback_data=f'{command}‽pagination‽{page_num + 1}')) if page_num + 1 < len(channels) else None
    keyboard.append(
        pagination_button_set) if pagination_button_set else None

    return keyboard


@log_errors
def add(channel_id: str, update: Update, p: Profile, name: Optional[str] = None) -> None:
    video_title, video_url, upload_time = get_last_video(channel_id)
    channel_name = name if name else get_channel_title(
        channel_id)
    channel, _ = Channel.objects.get_or_create(
        channel_url=f'https://www.youtube.com/channel/{channel_id}',
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
            try:
                update.callback_query.message.reply_text(
                    text=f"{localization[p.language]['add_command'][2][0]} {channel_name} {localization[p.language]['add_command'][2][1]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML'
                )
            except:
                update.message.reply_text(
                    text=f"{localization[p.language]['add_command'][2][0]} {channel_name} {localization[p.language]['add_command'][2][1]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML'
                )
            return
        else:
            try:
                update.callback_query.message.reply_text(
                    text=localization[p.language]['add_command'][3],
                    parse_mode='HTML'
                )
            except:
                update.message.reply_text(
                    text=localization[p.language]['add_command'][3],
                    parse_mode='HTML'
                )
    else:
        try:
            update.callback_query.message.reply_text(
                text=f"{localization[p.language]['add_command'][4]} <a href=\"{video_url}\">{video_title}</a>",
                parse_mode='HTML'
            )
        except:
            update.message.reply_text(
                text=f"{localization[p.language]['add_command'][4]} <a href=\"{video_url}\">{video_title}</a>",
                parse_mode='HTML'
            )


@log_errors
def remove(update: Update, p: Profile, name: str) -> None:
    item = ChannelUserItem.objects.get(user=p, channel_title=name)
    item.delete()
    update.callback_query.edit_message_text(
        text=localization[p.language]['remove_command'][2],
        parse_mode='HTML'
    )


@log_errors
def check(update: Update, p: Profile, name: str) -> None:
    item = ChannelUserItem.objects.get(user=p, channel_title=name)
    if not check_for_new_video(item.channel):
        update.callback_query.edit_message_text(
            text=f'{localization[p.language]["check_command"][3]} <a href=\"{item.channel.video_url}\">{item.channel.video_title}</a>',
            parse_mode='HTML'
        )
    else:
        update.callback_query.delete_message()
