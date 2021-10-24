from django.conf import settings
import re
from bs4 import BeautifulSoup
import requests
from dateutil import parser
from youtube.models import Channel, ChannelUserItem
from telegram_profile.models import Profile


# Gets last video from given channel by it`s id
def get_last_video(channel_id):
    html = requests.get(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
    soup = BeautifulSoup(html.text, "lxml")
    entry = soup.find("entry")
    return entry.find("title").text, entry.find("link")["href"], parser.parse(entry.find("published").text).strftime("%m/%d/%Y, %H:%M:%S")


# Gets channel title from given channel id
def get_channel_title(channel_id):
    html = requests.get(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
    soup = BeautifulSoup(html.text, "lxml")
    entry = soup.find("entry")
    return entry.find("name").text


# Checks if given string is youtube channel url
def is_channel_url(string):
    return bool(re.search(r'http[s]*://www.youtube.com/(?:c|user|channel)/[\w-]+', string))


# Gets channel id by given channel url
def get_channel_id_by_url(channel_url):
    html = requests.get(channel_url)
    soup = BeautifulSoup(html.text, "lxml")
    columns = soup.find('script', text=re.compile(
        r'\"externalId\":\"([\w-]+)\"'))
    try:
        channel_id = re.findall(
            r'\"externalId\":\"([\w-]+)\"', str(columns))[0]
    except:
        return
    return channel_id


# Gets or create profile from chat_id and username
def get_or_create_profile(chat_id, name):
    return Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': name,
            'language': 'eng',
        }
    )


# Sends message to user by chat_id
def send_message(chat_id, bot_message, parse_mode='HTML'):
    send_text = 'https://api.telegram.org/bot' + str(settings.TOKEN) + \
        '/sendMessage?chat_id=' + str(chat_id) + '&text=' + \
        bot_message + '&parse_mode=' + parse_mode
    requests.get(send_text)
