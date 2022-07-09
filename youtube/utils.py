import asyncio
import re
from typing import List, Optional, Union

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from django.conf import settings
from fake_headers import Headers


# Gets videos info and channels title from given channel feeds urls
def get_channels_and_videos_info(urls: List[str], live_urls: List[str]):
    async def get_all(urls, live_urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url, live_url):
                async with session.get(url, headers=Headers().generate()) as response:
                    html = soup.BeautifulSoup(await response.text(), 'xml')
                    for entry in html.find_all("entry"):
                        video_title = entry.find("title").text
                        video_url = f"https://www.youtube.com/watch?v={entry.videoId.text}"
                        channel_title = entry.find("author").find("name").text
                        if not (entry.statistics['views'] == '0' and entry.starRating['count'] != '0') and video_url != live_url:
                            return video_title, video_url, channel_title
            return await asyncio.gather(*[
                fetch(url, live_url) for url, live_url in zip(urls, live_urls)
            ])
    return sync.async_to_sync(get_all)(urls, live_urls)


# Get channels live title and urls
def get_channels_live_title_and_url(urls: List[str]):
    async def get_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url):
                async with session.get(url, headers=Headers().generate()) as response:
                    text = await response.text()
                    html = soup.BeautifulSoup(text, 'lxml')
                    try:
                        return html.find("meta", {"name": "title"})['content'], html.find("link", {"rel": "canonical"})['href'], any(re.findall(r'(\"isUpcoming\":true)', text))
                    except TypeError:
                        return html.find("meta", property="og:title")['content'], html.find("link", {"rel": "canonical"})['href'], any(re.findall(r'(\"isUpcoming\":true)', text))
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    return sync.async_to_sync(get_all)(urls)


# Checks if given string is youtube channel url
def is_youtube_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:c|user|channel)/([\%\w-]+)(?:[/]*)', string))


# Returns channel url from channel id
def get_url_from_id(channel_id: str) -> Union[str, None]:
    return f'https://www.youtube.com/channel/{channel_id}' if channel_id else None


# Scrapes channel id from url
def scrape_id_by_url(url: str) -> Union[str, bool]:
    session = requests.Session()
    response = session.get(url)
    if "uxe=" in response.request.url:
        session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
        response = session.get(url)
    session.close()

    html = soup.BeautifulSoup(response.text, 'lxml')
    try:
        return html.find('meta', {'itemprop': 'channelId'})['content']
    except:
        return False
