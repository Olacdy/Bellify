import re
from datetime import datetime
import streamlink
from typing import Optional
import aiohttp
import bs4 as soup
import requests
from dateutil import parser
import time
from fake_headers import Headers


# Gets last video info and channels title from given channel id
async def get_channel_and_video_info(session: aiohttp.ClientSession, channel_id: str, video_num: Optional[int] = 0):
    async with session.get(f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}', headers=Headers().generate()) as response:
        html = soup.BeautifulSoup(await response.text(), 'xml')
        entry = html.find_all("entry")[video_num]
        return entry.find("title").text, f"https://www.youtube.com/watch?v={entry.videoId.text}", datetime.strptime(parser.parse(entry.find("published").text).strftime("%m/%d/%Y, %H:%M:%S"), "%m/%d/%Y, %H:%M:%S"), entry.find("author").find("name").text


# Checks if channels is live
async def is_channel_live(session: aiohttp.ClientSession, channel_id: str):
    async with session.get(f'https://www.youtube.com/channel/{channel_id}/live', headers=Headers().generate()) as response:
        html = soup.BeautifulSoup(await response.text(), "lxml")
        try:
            html.select_one("meta[content][name='title']")['content']
            return not any('add_upcoming_event_reminder' in script.get_text() for script in html.find_all("script"))
        except:
            return False


# Gets live broadcast title from given channel id
async def get_channel_live_title_and_url(session: aiohttp.ClientSession, channel_id: str):
    async with session.get(f'https://www.youtube.com/channel/{channel_id}/live', headers=Headers().generate()) as response:
        html = soup.BeautifulSoup(await response.text(), "lxml")
        try:
            live_id = re.findall(
                r'\"liveStreamability\":{\"liveStreamabilityRenderer\":{\"videoId\":\"(\w+)\"', str(html))[0]
            return html.select_one("meta[content][name='title']")['content'], f"https://www.youtube.com/watch?v={live_id}"
        except:
            return None, None


# Checks if given string is youtube channel url
def _is_youtube_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:c|user|channel)/([\%\w-]+)(?:[/]*)', string))


# Checks if given string is twitch channel url
def _is_twitch_channel_url(string: str) -> bool:
    # TODO Twitch url checker
    return False


# Checks if given string is url
def get_channel_url_type(string: str):
    if _is_youtube_channel_url(string):
        return 'Youtube'
    elif _is_twitch_channel_url(string):
        return 'Twitch'
    else:
        return None


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
