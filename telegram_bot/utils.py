from django.conf import settings
import re
from bs4 import BeautifulSoup
import requests
from dateutil import parser
import telegram_notification.tasks as tasks
from youtube.models import Channel, ChannelUserItem
from telegram_bot.models import Profile
from typing import Optional


# Gets last video from given channel by it`s id
def get_last_video(channel_id):
    channel_id = channel_id[:1] + 'U' + channel_id[2:]
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={channel_id}&maxResults=5&key={settings.YOUTUBE_API_KEY}')
    title = api_response.json()['items'][0]['snippet']['title']
    publication_date = parser.parse(api_response.json(
    )['items'][0]['snippet']['publishedAt']).strftime("%m/%d/%Y, %H:%M:%S")
    url = f"https://www.youtube.com/watch?v={api_response.json()['items'][0]['snippet']['resourceId']['videoId']}"
    return title, url, publication_date


# Gets channel title from given channel id
def get_channel_title(channel_id):
    channel_id = channel_id[:1] + 'U' + channel_id[2:]
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={channel_id}&maxResults=5&key={settings.YOUTUBE_API_KEY}')
    channel_title = api_response.json()['items'][0]['snippet']['channelTitle']
    return channel_title


# Checks if given string is youtube channel url
def is_channel_url(string):
    return bool(re.search(r'http[s]*://(?:www.)youtube.com/(?:c|user|channel)/([\w-]+)(?:[/]*)', string))


# Checks if channels identifier is channel id
def is_id_in_url(string):
    try:
        ident = get_identifier_from_url(string)
    except:
        return False
    return bool(re.search(r'UC[\w-]+', ident))


# Gets identifier from url
def get_identifier_from_url(string):
    return re.findall(r'http[s]*://(?:www.)youtube.com/(?:c|user|channel)/([\w-]+)(?:[/]*)', string)[0]


# Gets id from channel name
def get_id_from_name(name):
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&maxResults=5&q={name}&key={settings.YOUTUBE_API_KEY}')
    return api_response.json()['items'][0]['id']['channelId']


# Gets or create profile from chat_id and username
def get_or_create_profile(chat_id, name, reset: Optional[bool] = True):
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
def send_message(chat_id, bot_message, parse_mode='HTML'):
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
        channel.video_publication_date = new_upload_time
        channel.save()
        users = [item.user for item in ChannelUserItem.objects.filter(
            channel=channel)]
        tasks.notify_users(users, channel)
        return True
    else:
        return False
