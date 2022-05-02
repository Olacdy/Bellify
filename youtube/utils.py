import re
import asyncio
from asgiref import sync
from typing import Optional, List
import aiohttp
import bs4 as soup
from django.conf import settings
import requests
import time
from fake_headers import Headers


# Gets videos info and channels title from given channel feeds urls
def get_channels_and_videos_info(urls: List[str], video_num: Optional[int] = 0):
    async def get_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url):
                async with session.get(url, headers=Headers().generate()) as response:
                    html = soup.BeautifulSoup(await response.text(), 'xml')
                    entry = html.find_all("entry")[video_num]
                    return entry.find("title").text, f"https://www.youtube.com/watch?v={entry.videoId.text}", entry.find("author").find("name").text
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    return sync.async_to_sync(get_all)(urls)


# Get channels live title and urls
def get_channels_live_title_and_url(urls: List[str]):
    async def get_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url):
                async with session.get(url, headers=Headers().generate()) as response:
                    text = await response.text()
                    try:
                        if not any(re.findall(r'(add_upcoming_event_reminder)', text)):
                            live_id = re.findall(
                                r'\"liveStreamability\":{\"liveStreamabilityRenderer\":{\"videoId\":\"(\w+)\"', text)[0]
                            return re.findall(
                                r'<meta name=\"title\" content=\"(.*?)\"><meta', text)[0], f"https://www.youtube.com/watch?v={live_id}", False
                        else:
                            return None, None, True
                    except:
                        return None, None, None
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    return sync.async_to_sync(get_all)(urls)


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
