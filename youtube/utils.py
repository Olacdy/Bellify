import asyncio
import re
from datetime import datetime
from typing import List, Optional, Union, Tuple

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from django.conf import settings
from fake_headers import Headers


# Return list of info about YouTube channels
def get_youtube_channels_info(ids: List[str]) -> List[Tuple[str]]:
    async def get_all(ids):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(id):
                async with session.get(f'https://www.youtube.com/channel/{id}/live', headers=Headers().generate()) as response:
                    live_text = await response.text()
                async with session.get(f'https://www.youtube.com/feeds/videos.xml?channel_id={id}', headers=Headers().generate()) as response:
                    video_text = await response.text()
                live_html = soup.BeautifulSoup(live_text, 'lxml')
                videos_xml = soup.BeautifulSoup(video_text, 'xml')
                try:
                    live_title, live_url, is_upcoming = live_html.find('meta', {'name': 'title'})['content'], live_html.find(
                        'link', {'rel': 'canonical'})['href'], any(re.findall(r'(\"isUpcoming\":true)', live_text))
                except TypeError:
                    live_title, live_url, is_upcoming = None, None, None
                for entry in videos_xml.find_all('entry'):
                    video_title = entry.title.text
                    video_url = entry.link['href']
                    video_published = datetime.strptime(
                        entry.published.text, '%Y-%m-%dT%H:%M:%S%z')
                    channel_title = entry.author.find('name').text
                    if not (entry.statistics['views'] == '0' and entry.starRating['count'] != '0') and video_url != live_url:
                        return video_title, video_url, video_published, live_title, live_url, is_upcoming, channel_title
            return await asyncio.gather(*[
                fetch(id) for id in ids
            ])
    return sync.async_to_sync(get_all)(ids)


# Checks if given string is a youtube channel url
def is_youtube_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:c|user|channel)/([\%\w-]+)(?:[/]*)', string))


# Checks if given string is a youtube video url
def is_youtube_video_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?(?:youtu\.be|youtube\.com)/(?:watch\?v=|shorts/)?([\%\w-]+)(?:[/]*)', string))


# Checks if given string is a youtube url
def is_youtube_url(string: str) -> bool:
    return is_youtube_channel_url(string) or is_youtube_video_url(string)


# Returns channel url from channel id
def get_url_from_id(channel_id: str) -> Union[str, None]:
    return f'https://www.youtube.com/channel/{channel_id}' if channel_id else None


# Returns html of a page by url
def _get_html_response_youtube(url: str) -> str:
    session = requests.Session()
    session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')
    response = session.get(url, headers=Headers().generate())
    session.close()

    return response.text


# Scrapes channel videos info from id
def scrape_last_video_and_channel_title(id: str, live_url: Optional[str] = None) -> Tuple[str]:
    video_text = _get_html_response_youtube(
        f'https://www.youtube.com/feeds/videos.xml?channel_id={id}')
    videos_xml = soup.BeautifulSoup(video_text, 'xml')
    for entry in videos_xml.find_all('entry'):
        video_title = entry.title.text
        video_url = entry.link['href']
        video_published = datetime.strptime(
            entry.published.text, '%Y-%m-%dT%H:%M:%S%z')
        channel_title = entry.author.find('name').text
        if not (entry.statistics['views'] == '0' and entry.starRating['count'] != '0') and video_url != live_url:
            return video_title, video_url, video_published, channel_title


# Scrapes channel live info from id
def scrape_channel_live(id: str) -> Tuple[Union[str, None]]:
    live_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{id}/live')
    live_html = soup.BeautifulSoup(live_text, 'lxml')
    try:
        return live_html.find('meta', {'name': 'title'})['content'], live_html.find(
            'link', {'rel': 'canonical'})['href'], any(re.findall(r'(\"isUpcoming\":true)', live_text))
    except TypeError:
        return None, None, None


# Scrapes channel id from url
def scrape_id_by_url(url: str) -> Union[str, bool]:
    text = _get_html_response_youtube(url)
    html = soup.BeautifulSoup(text, 'lxml')
    try:
        return html.find('meta', {'itemprop': 'channelId'})['content']
    except:
        return False


# Checks whether the video is valid
def scrape_if_video_is_valid(url: str) -> bool:
    if url:
        text = _get_html_response_youtube(url)
        html = soup.BeautifulSoup(text, 'lxml')
        try:
            return bool(html.find('meta', {'name': 'title'})['content'])
        except:
            return False
    return True
