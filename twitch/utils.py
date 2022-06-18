import asyncio
import re
from typing import List, Union

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from django.conf import settings
from fake_headers import Headers


# Get channels live title and urls
def get_channels_is_live_and_title(urls: List[str]):
    async def get_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url):
                async with session.get(url, headers=Headers().generate()) as response:
                    text = await response.text()
                    return re.findall(r'<meta property="og:description" content=\"((.*))\"\/>', text)[0], any(re.findall(r'\"isLiveBroadcast\":true', text))
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    return sync.async_to_sync(get_all)(urls)


# Checks if given channel exists and returns title if it is
def is_twitch_channel_exists(url: str) -> Union[str, bool]:
    session = requests.Session()
    response = session.get(url)
    if "uxe=" in response.request.url:
        session.cookies.set("CONSENT", "YES+cb", domain=".twitch.tv")
        response = session.get(url)
    session.close()

    html = soup.BeautifulSoup(response.text, 'lxml')
    try:
        title = re.sub(r'\s-\sTwitch$', '',
                       html.find('meta', {'name': 'title'})['content'])
    except:
        return False
    else:
        return title


# Checks if given string is twitch channel url
def _is_twitch_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', string))


# Scrapes channel title from url
def get_channel_title_from_url(url: str) -> str:
    return re.findall(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', url)[0]


def get_channel_url_from_title(title: str) -> str:
    return f"https://www.twitch.tv/{title}"
