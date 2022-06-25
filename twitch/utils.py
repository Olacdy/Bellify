import asyncio
import re
from typing import List, Union

import aiohttp
import bs4 as soup
import requests
from asgiref import sync
from django.conf import settings
from fake_headers import Headers


# Get channels live title and is_live
# TODO Проверить есть ли атрибут isLiveBroadcast: false, если - да, то сделать луп, который будет пытаться его получить, если - нет, сделать луп, который будет пытаться загрузить страницу
def get_channels_title_and_is_live(urls: List[str]):
    async def get_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def fetch(url):
                async with session.get(url, headers=Headers().generate()) as response:
                    text = await response.text()
                    try:
                        return re.search(
                            r'<meta property=\"og:description\" content=\"((.*?))\"/>', text).group(1), any(re.findall(r'\"isLiveBroadcast\":true', text))
                    except AttributeError as attr_error:
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


# Checks if given channel exists and returns title if it is
def get_channel_title(url: str) -> Union[str, bool]:
    for _ in range(settings.TWITCH_TRIES_NUMBER):
        html = get_html_of_twitch_url(url)
        try:
            title = re.sub(r'\s-\sTwitch$', '',
                           html.find('meta', {'name': 'title'})['content'])
        except:
            continue
        else:
            return title
    return False


def get_channel_title_and_is_live(url: str) -> Union[Union[str, bool], List[None]]:
    while True:
        html = get_html_of_twitch_url(url)

        try:
            title, is_live = html.find(
                'meta', {'name': 'description'})['content'], any(re.findall(r'\"isLiveBroadcast\":true', str(html)))
        except:
            continue
        else:
            return title, is_live


# Checks if given string is twitch channel url
def _is_twitch_channel_url(string: str) -> bool:
    return bool(re.search(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', string))


# Scrapes channel title from url
def get_channel_title_from_url(url: str) -> str:
    return re.findall(r'http[s]*://(?:www\.)?twitch.(?:com|tv)/([\%\w-]+)(?:[/]*)', url)[0]


def get_channel_url_from_title(title: str) -> str:
    return f"https://www.twitch.tv/{title}"
