import re

import bs4 as soup
import requests
import scrapetube
from dateutil import parser
from django.conf import settings

from youtube.models import Channel


# Gets last video from given channel by it`s id
def get_last_video(channel_id: str):
    playlist_id = channel_id[:1] + 'U' + channel_id[2:]
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=5&key={settings.YOUTUBE_API_KEY}')
    try:
        title = api_response.json()['items'][0]['snippet']['title']
        publication_date = parser.parse(api_response.json(
        )['items'][0]['snippet']['publishedAt']).strftime("%m/%d/%Y, %H:%M:%S")
        url = f"https://www.youtube.com/watch?v={api_response.json()['items'][0]['snippet']['resourceId']['videoId']}"
    except Exception as e:
        videos = scrapetube.get_channel(channel_id)
        video_id = [video['videoId'] for video in videos][0]
        api_response = requests.get(
            f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={settings.YOUTUBE_API_KEY}')
        try:
            title = api_response.json()['items'][0]['snippet']['title']
            publication_date = parser.parse(api_response.json()['items'][0]['snippet']['publishedAt']).strftime(
                "%m/%d/%Y, %H:%M:%S")
            url = f"https://www.youtube.com/watch?v={video_id}"
        except:
            channel = Channel.objects.get(channel_id=channel_id)
            title = channel.title
            publication_date = channel.video_publication_date
            url = channel.video_url
    return title, url, publication_date


# Gets channel title from given channel id
def get_channel_title(channel_id: str):
    playlist_id = channel_id[:1] + 'U' + channel_id[2:]
    api_response = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=5&key={settings.YOUTUBE_API_KEY}')
    try:
        channel_title = api_response.json(
        )['items'][0]['snippet']['channelTitle']
    except:
        videos = scrapetube.get_channel(channel_id)
        video_id = [video['videoId'] for video in videos][0]
        api_response = requests.get(
            f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={settings.YOUTUBE_API_KEY}')
        channel_title = api_response.json(
        )['items'][0]['snippet']['channelTitle']
    return channel_title


# Checks if given string is youtube channel url
def is_channel_url(string: str):
    return bool(re.search(r'http[s]*://(?:www\.)?youtube.com/(?:c|user|channel)/([\%\w-]+)(?:[/]*)', string))


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
