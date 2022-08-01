import asyncio
import datetime
import json
import re
from typing import List, Optional, Tuple, Union

import aiohttp
import bs4 as soup
from django.utils import timezone
import requests
from asgiref import sync
from django.conf import settings
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
                async with session.get(f'https://www.youtube.com/channel/{id}/videos?view=2&sort=dd&live_view=501&shelf_id=0', headers=HeadersYouTube().generate()) as response:
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
                return get_content(json.loads(get_json_from_html(video_text, "var ytInitialData = ", 0, "};") + "}"))
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
    response = session.get(url, headers=HeadersYouTube().generate())
    session.close()

    return response.text


# Scrapes channel id from url
def scrape_id_and_title_by_url(url: str) -> Union[str, bool]:
    text = _get_html_response_youtube(url)
    html = soup.BeautifulSoup(text, 'lxml')
    try:
        return html.find('meta', {'itemprop': 'channelId'})['content'], html.find('meta', {'property': 'og:title'})['content']
    except:
        return False, ''


# Scrapes last videos for a single channel
def scrape_last_videos(channel_id: str) -> Tuple[str, str, str]:
    video_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{channel_id}/videos?sort=dd')
    return get_content(json.loads(get_json_from_html(video_text, "var ytInitialData = ", 0, "};") + "}"))


# Scrapes livestreams for a single channel
def scrape_livesteams(channel_id: str) -> Tuple[str, str]:
    livestream_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{channel_id}/videos?view=2&sort=dd&live_view=501&shelf_id=0')
    return get_content(json.loads(get_json_from_html(livestream_text, "var ytInitialData = ", 0, "};") + "}"), mode='livestream')


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


def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(stop, pos_begin)
    return html[pos_begin:pos_end]


# Returns list of content
def get_content(partial: dict, mode: Optional[str] = 'videos') -> List[Union[Tuple[str, str, str, bool], Tuple[str, str]]]:
    def _get_video_info(video: dict) -> Tuple[str, str, str, bool]:
        video_id = video['videoId']
        video_title = video['title']['runs'][0]['text']

        is_saved_livestream = 'streamed' in video['publishedTimeText']['simpleText'].lower(
        )

        if not video['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style'].lower() in ['live', 'upcoming']:
            return video_id, video_title, is_saved_livestream
        raise

    def _get_livestream_info(livestream: dict) -> Tuple[str, str]:
        livestream_id = livestream['videoId']
        livestream_title = livestream['title']['runs'][0]['text']

        return livestream_id, livestream_title

    stack = [partial]
    content = []

    while stack:
        current_item = stack.pop(0)
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == 'gridVideoRenderer':
                    try:
                        content.append(_get_video_info(
                            value) if mode == 'videos' else _get_livestream_info(value))
                    except:
                        continue
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)

    return content
