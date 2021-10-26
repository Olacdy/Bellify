from django.conf import settings
import re
from bs4 import BeautifulSoup
import requests
from dateutil import parser
import telegram_notification.tasks as tasks
from youtube.models import Channel, ChannelUserItem
from telegram_bot.models import Profile
from typing import Optional


headers = {
    'authority': 'www.youtube.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-full-version': '"95.0.4638.54"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"7.0.0"',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-bitness': '"64"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'x-client-data': 'CJC2yQEIpbbJAQjEtskBCKmdygEIjPjKAQjq8ssBCO/yywEInvnLAQjnhMwBCLaFzAEI/4XMAQiBhswBCIqIzAEIy4nMAQ==',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.youtube.com/signin_passive',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': 'GPS=1; YSC=Z9CIwZos5KY; VISITOR_INFO1_LIVE=fvmz9_N-FZg; __Secure-3PSID=DQi-v1E-vy5bPRw3LkBB4CF1z2xLQsqvktlFZjZ1cvJSjyd8D_vu_63KzcjNQ4zsjTLi-w.; __Secure-3PAPISID=e2ugJSAofPMMc6U8/Apyi1E1BUnN3b_47f; LOGIN_INFO=AFmmF2swRgIhAJqMg7lU-LudnZd5llgvBVhgJBvmH9xNDqZaCb_p3vLtAiEA2qMR_BTnkGhUKVTjIFaZYC4u0ATanggJOdCN2skqNYE:QUQ3MjNmemFGREM3eTkyVjBSc05hTlREYkc1X0dhbGItN2l6aE1yRUtWaVpubi1Ra1JhLUpSUFRiZUZaMms4djdFWnZhaVZNQVdXclNEanFIQWFpajFmUzYyRUFWQ0h6Q2UzMUVFRmJqOFVweXpaZ2NzdnIyQkFDc3lEc2VIWFFzYlhrZlltVXRLRWJFVUlmcUhhRHczMWsxZ2l3OGd3WmV3; PREF=f6=80&tz=Europe.Kiev; __Secure-3PSIDCC=AJi4QfFmiVpY_-ksjHdIHrA4dbqjoXzOsMHGcOoELL0n-3ogSxguMyBoHphPyhzYULMycT6B',
}


# Gets last video from given channel by it`s id
def get_last_video(channel_id):
    html = requests.get(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}", headers=headers)
    soup = BeautifulSoup(html.text, "lxml")
    entry = soup.find("entry")
    return entry.find("title").text, entry.find("link")["href"], parser.parse(entry.find("published").text).strftime("%m/%d/%Y, %H:%M:%S")


# Gets channel title from given channel id
def get_channel_title(channel_id):
    html = requests.get(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}", headers=headers)
    soup = BeautifulSoup(html.text, "lxml")
    entry = soup.find("entry")
    return entry.find("name").text


# Checks if given string is youtube channel url
def is_channel_url(string):
    return bool(re.search(r'http[s]*://www.youtube.com/(?:c|user|channel)/[\w-]+', string))


# Gets channel id by given channel url
def get_channel_id_by_url(channel_url):
    html = requests.get(channel_url, headers=headers)
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
