import asyncio
import re
from typing import List, Union

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from django.conf import settings
from fake_headers import Headers
from sqlalchemy import except_all


# Get channels live title and is_live
def get_channels_title_and_is_live(urls: List[str]):
    async def get_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url):
                async with session.get(url, headers=Headers().generate()) as response:
                    text = await response.text()
                    for _ in range(settings.TWITCH_TRIES_NUMBER):
                        try:
                            live_title, is_live = re.search(
                                r'<meta property=\"og:description\" content=\"((.*?))\"/>', text).group(1), any(re.findall(r'\"isLiveBroadcast\":true', text))
                        except AttributeError as attr_error:
                            continue
                        else:
                            return live_title, is_live
                    return None, None
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    return sync.async_to_sync(get_all)(urls)


# Returns BeautifulSoup object of given twitch channel url
def get_html_of_twitch_url(url: str) -> soup.BeautifulSoup:
    session = requests.Session()
    response = session.get(url, headers=Headers().generate(), timeout=(1, 10))
    if "uxe=" in response.request.url:
        session.cookies.set("CONSENT", "YES+cb", domain=".twitch.tv")
        response = session.get(url)
    session.close()

    return soup.BeautifulSoup(response.content, 'lxml')


# Returns channel title, live title, is_live, if it exists
def get_twitch_channel_info(url: str) -> Union[str, bool, None]:
    for _ in range(settings.TWITCH_TRIES_NUMBER):
        html = get_html_of_twitch_url(url)
        try:
            title = re.sub(r'\s-\sTwitch$', '',
                           html.find('meta', {'name': 'title'})['content'])
        except TypeError as e:
            continue
        else:
            if title:
                for _ in range(settings.TWITCH_TRIES_NUMBER):
                    html = get_html_of_twitch_url(url)

                    try:
                        live_title = html.find(
                            'meta', {'name': 'description'})['content']
                    except Exception as e:
                        continue
                    else:
                        for _ in range(settings.TWITCH_TRIES_NUMBER):
                            html = get_html_of_twitch_url(url)
                            try:
                                is_live = any(re.findall(
                                    r'\"isLiveBroadcast\":true', str(html)))
                            except Exception as e:
                                continue
                            else:
                                return title, live_title, is_live
                        return title, live_title, False
            else:
                return None


# Checks if given string is twitch channel url
def _is_twitch_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', string))


# Scrapes channel title from url
def get_channel_title_from_url(url: str) -> str:
    return re.findall(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', url)[0]


# Returns url of the Twitch channel from its title
def get_channel_url_from_title(title: str) -> str:
    return f"https://www.twitch.tv/{title}"
