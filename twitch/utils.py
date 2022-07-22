import asyncio
import itertools
import re
from typing import List, Optional, Tuple

import aiohttp
import requests
from asgiref import sync
from django.conf import settings

from twitch.models import TwitchChannel


# Returns Twitch streams info for a list of ids consisting of chunks of 100
def get_twitch_streams_info(ids: List[List[str]]) -> List[Tuple[str]]:
    token = TwitchChannel.get_or_update_bearer_token()

    async def get_all(ids: List[List[str]]):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(ids_100: List[str], token: str):
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Client-Id': settings.TWITCH_CLIENT_ID,
                }

                params = {
                    'user_id': ids_100
                }

                async with session.get('https://api.twitch.tv/helix/streams', headers=headers, params=params) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return [(response_data_item['user_id'], response_data_item['title'], response_data_item['game_name'],
                                 get_formatted_thumbnail_url(response_data_item['thumbnail_url']), True)
                                for response_data_item in response_data['data']]
                    elif response.status == 401:
                        return get_streams_info(ids_100)
            return await asyncio.gather(*[
                fetch(ids_100, token) for ids_100 in ids
            ])
    return list(itertools.chain(*sync.async_to_sync(get_all)(ids)))


# Returns channel id, login, display_name from ids or usernames
def get_users_info(ids: Optional[List[str]] = None, usernames: Optional[List[str]] = None) -> List[tuple]:
    token = TwitchChannel.get_or_update_bearer_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'Client-Id': settings.TWITCH_CLIENT_ID,
    }

    params = {
        'login' if usernames else 'id': usernames if usernames else ids
    }

    response = requests.get(
        'https://api.twitch.tv/helix/users', params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()['data']
        return [(response_data_item['id'], response_data_item['login'], response_data_item['display_name']) for response_data_item in response_data]
    elif response.status_code == 401:
        TwitchChannel.get_or_update_bearer_token()(update=True)
        return get_users_info(ids=ids, usernames=usernames)


# Returns Twitch streams info from channels ids
def get_streams_info(ids: List[str]) -> List[tuple]:
    token = TwitchChannel.get_or_update_bearer_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'Client-Id': settings.TWITCH_CLIENT_ID,
    }

    params = {
        'user_id': ids
    }

    response = requests.get(
        'https://api.twitch.tv/helix/streams', headers=headers, params=params)

    if response.status_code == 200:
        response_data = response.json()['data']
        return [(response_data_item['user_id'], response_data_item['title'], response_data_item['game_name'],
                get_formatted_thumbnail_url(response_data_item['thumbnail_url']), True)
                for response_data_item in response_data]
    elif response.status_code == 401:
        TwitchChannel.get_or_update_bearer_token()(update=True)
        return get_streams_info(ids=ids)


# Checks if given string is twitch channel url
def is_twitch_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', string))


# Scrapes channel title from url
def get_channel_title_from_url(url: str) -> str:
    return re.findall(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', url)[0]


# Returns url of the Twitch channel from its title
def get_channel_url_from_title(title: str) -> str:
    return f'https://www.twitch.tv/{title}'


# Returns formatted thumbnail url with given width and height
def get_formatted_thumbnail_url(url: str, width: Optional[int] = 1280, height: Optional[int] = 720):
    return f'{url.split("{")[0]}{width}x{height}.jpg'
