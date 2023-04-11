import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Union

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from bs4 import BeautifulSoup
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
                async with session.get(f'https://www.youtube.com/channel/{id}/featured',
                                       headers=HeadersYouTube().generate()) as response:
                    livestream_text = await response.text()
                try:
                    content = get_content(json.loads(get_json_from_html(
                        livestream_text, "var ytInitialData = ", 0, "};") + "}"))
                    return content
                except:
                    print("Livestreams page response content:")
                    print(livestream_text)
                    print("Initial data in JSON format from html:")
                    print(get_json_from_html(
                        livestream_text, "var ytInitialData = ", 0, "};") + "}")
            return await asyncio.gather(*[
                fetch(id) for id in ids
            ])
    return sync.async_to_sync(get_all)(ids)


def get_non_livestreams(videos: List['YouTubeVideo']) -> List['YouTubeVideo']:
    async def get_all(videos):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(video):
                async with session.get(f'https://www.youtube.com/watch?v={video.video_id}',
                                       headers=HeadersYouTube().generate()) as response:
                    video_text = await response.text()
                try:
                    if not is_livestream(json.loads(get_json_from_html(video_text, "var ytInitialData = ", 0, "};") + "}")):
                        return video
                except:
                    return
            return await asyncio.gather(*[
                fetch(video) for video in videos
            ])
    return [video for video in sync.async_to_sync(get_all)(videos) if video is not None]


# Returns list of videos
def get_youtube_videos(ids: List[str]) -> List[Tuple[str]]:
    async def get_all(ids):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(id):
                async with session.get(f'https://www.youtube.com/feeds/videos.xml?channel_id={id}',
                                       headers=HeadersYouTube().generate()) as response:
                    videos_feed = await response.text()
                soup = BeautifulSoup(videos_feed, 'xml')
                return parse_video_entries(soup.find_all('entry'))
            return await asyncio.gather(*[
                fetch(id) for id in ids
            ])
    return sync.async_to_sync(get_all)(ids)


# Checks if given string is a youtube channel url
def is_youtube_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:(?:c|user|channel)/([\%\w-]+)(?:[/]*)|@(\w+))', string))


# Checks if given string is a youtube video url
def is_youtube_video_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?(?:youtu\.be|youtube\.com)/(?:watch\?v=|shorts/|live/)?([\%\w-]+)(?:[/]*)', string))


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
            return html.find('meta', {'itemprop': 'channelId'})['content'], author.find(
                'link', {'itemprop': 'name'})['content']
        else:
            return html.find('meta', {'itemprop': 'channelId'})['content'], html.find('meta', {'property': 'og:title'})[
                'content']
    except:
        return False, ''


# Scrapes last videos for a single channel
def scrape_last_videos(channel_id: str) -> Dict[str, Tuple[str, datetime]]:
    videos_feed = requests.get(
        f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}').text
    soup = BeautifulSoup(videos_feed, 'xml')
    return parse_video_entries(soup.find_all('entry'))


def parse_video_entries(video_entries) -> Dict[str, Tuple[str, datetime]]:
    videos = {}

    for video in video_entries:
        video_id = video.find("yt:videoId").text
        video_title = video.find("title").text
        published_at = datetime.strptime(video.find(
            "published").text, '%Y-%m-%dT%H:%M:%S%z')
        rating = int(video.find("media:starRating")['count'])
        views = int(video.find("media:statistics")['views'])
        if not (rating >= views and views == 0):
            videos[video_id] = video_title, published_at

    return videos


# Scrapes livestreams for a single channel
def scrape_livesteams(channel_id: str) -> Tuple[str, str]:
    livestream_text = _get_html_response_youtube(
        f'https://www.youtube.com/channel/{channel_id}/featured')
    return get_content(json.loads(get_json_from_html(livestream_text, "var ytInitialData = ", 0, "};") + "}"))


def check_if_video_is_exists(video_url: str) -> bool:
    text = _get_html_response_youtube(video_url)
    html = soup.BeautifulSoup(text, 'lxml')
    return bool(html.find('meta', {'name': 'title'})['content'])


def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(stop, pos_begin)
    return html[pos_begin:pos_end]


# Returns list of content
def get_content(partial: dict) -> Dict[str, str]:
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
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)

    return content


# Checks youtube/v1 json data if video is a livestream
def is_livestream(video_data) -> bool:
    try:
        return video_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['isLive']
    except:
        return False


def get_only_new_livestreams(videos_to_create: List['YouTubeVideo'],
                             potential_livestreams: List['YouTubeLivestream']
                             ) -> Tuple[List['YouTubeVideo'], List['YouTubeVideo']]:
    only_videos_to_create = get_non_livestreams(videos_to_create)
    livestreams = [
        livestream for livestream in videos_to_create if livestream not in only_videos_to_create
    ]

    livestream_ids = [
        livestream.livestream_id for livestream in livestreams
    ]

    for potential_livestream in potential_livestreams:
        if not potential_livestream.livestream_id in livestream_ids:
            potential_livestream.set_ended()

    return only_videos_to_create, livestreams
