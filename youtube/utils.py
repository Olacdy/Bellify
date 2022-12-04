import asyncio
import json
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional, Tuple, Union

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from django.conf import settings
from django.utils.timezone import now
from fake_headers import Headers


# Custom Headers class for YouTube requests
class HeadersYouTube(Headers):
    def __init__(self):
        super().__init__()

    def generate(self) -> dict:
        headers = super().generate()
        headers['accept-language'] = 'en-US'
        return headers


# Returns list of livesteams
def get_youtube_livestreams(ids: List[str]) -> List[Tuple[str]]:
    async def get_all(ids):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(id):
                async with session.get(f'https://www.youtube.com/channel/{id}/featured', headers=HeadersYouTube().generate()) as response:
                    livestream_text = await response.text()
                return get_content(json.loads(get_json_from_html(livestream_text, "var ytInitialData = ", 0, "};") + "}"), mode='livestream')
            return await asyncio.gather(*[
                fetch(id) for id in ids
            ])
    return sync.async_to_sync(get_all)(ids)


# Returns list of videos
def get_youtube_videos(ids: List[str]) -> List[Tuple[str]]:
    async def get_all(ids):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(id):
                async with session.get(f'https://www.youtube.com/channel/{id}/videos?sort=dd', headers=HeadersYouTube().generate()) as response:
                    video_text = await response.text()
                async with session.get(f'https://www.youtube.com/channel/{id}/streams?sort=dd', headers=HeadersYouTube().generate()) as response:
                    streams_text = await response.text()
                content = get_content(json.loads(get_json_from_html(
                    video_text, "var ytInitialData = ", 0, "};") + "}"))
                content.update(get_content(json.loads(get_json_from_html(
                    streams_text, "var ytInitialData = ", 0, "};") + "}")))
                return content
            return await asyncio.gather(*[
                fetch(id) for id in ids
            ])
    return sync.async_to_sync(get_all)(ids)


# Checks if given string is a youtube channel url
def is_youtube_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:(?:c|user|channel)/([\%\w-]+)(?:[/]*)|@(\w+))', string))


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
    response = session.get(url, headers=HeadersYouTube().generate())
    session.close()

    return response.text


# Scrapes channel id from url
def scrape_id_and_title_by_url(url: str) -> Union[str, bool]:
    text = _get_html_response_youtube(url)
    html = soup.BeautifulSoup(text, 'lxml')
    try:
        author = html.find('span', {'itemprop': 'author'})
        if author:
            return html.find('meta', {'itemprop': 'channelId'})['content'], author.find('link', {'itemprop': 'name'})['content']
        else:
            return html.find('meta', {'itemprop': 'channelId'})['content'], html.find('meta', {'property': 'og:title'})['content']
    except:
        return False, ''


# Scrapes last videos for a single channel
def scrape_last_videos(channel_id: str) -> Tuple[str, str, str]:
    video_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{channel_id}/videos?sort=dd')
    streams_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{channel_id}/streams?sort=dd')
    content = get_content(json.loads(get_json_from_html(
        video_text, "var ytInitialData = ", 0, "};") + "}"))
    content.update(get_content(json.loads(get_json_from_html(
        streams_text, "var ytInitialData = ", 0, "};") + "}")))
    return content


# Scrapes livestreams for a single channel
def scrape_livesteams(channel_id: str) -> Tuple[str, str]:
    livestream_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{channel_id}/featured')
    return get_content(json.loads(get_json_from_html(livestream_text, "var ytInitialData = ", 0, "};") + "}"), mode='livestream')


def check_if_video_is_exists(video_url: str) -> bool:
    text = _get_html_response_youtube(video_url)
    html = soup.BeautifulSoup(text, 'lxml')
    return bool(html.find('meta', {'name': 'title'})['content'])


def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(stop, pos_begin)
    return html[pos_begin:pos_end]


# Returns list of content
def get_content(partial: dict, mode: Optional[str] = 'videos') -> Union[Dict[str, Tuple[str, bool]], Dict[str, str]]:
    def _get_video_info(video: dict) -> Tuple[str, str, datetime]:
        def _get_datetime_of_published(published_time_text: str) -> datetime:
            matches = re.findall(
                r'(\d+) (second(?:s)?|minute(?:s)?|hour(?:s)?|day(?:s)?|week(?:s)?|month(?:s)?|year(?:s)?)', published_time_text)
            timedelta_kwargs = {
                key if key[-1] == 's' else key + 's': int(value) for value, key in matches}
            return now() - relativedelta(**timedelta_kwargs)

        video_id = video['videoId']
        video_title = video['title']['runs'][0]['text']

        if not video['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style'].lower() in ['live', 'upcoming']:
            return video_id, video_title, _get_datetime_of_published(video['publishedTimeText']['simpleText'])
        raise

    def _get_livestream_info(livestream: dict) -> Tuple[str, str]:
        livestream_id = livestream['videoId']
        livestream_title = livestream['title']['runs'][0]['text']

        if livestream['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style'].lower() == 'live':
            return livestream_id, livestream_title
        raise

    stack = [partial]
    content = {}

    while stack:
        current_item = stack.pop(0)
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if mode == 'livestream':
                    if key == 'channelFeaturedContentRenderer':
                        try:
                            for featured_item in value['items']:
                                content_item = _get_livestream_info(
                                    featured_item['videoRenderer'])
                                content[content_item[0]] = content_item[1]
                        except:
                            continue
                    else:
                        stack.append(value)
                else:
                    if key == 'videoRenderer':
                        try:
                            content_item = _get_video_info(
                                value)
                            content[content_item[0]] = content_item[1:]
                        except:
                            continue
                    else:
                        stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)

    return content
