from django.core.management.base import BaseCommand
from django.conf import settings
from bs4 import BeautifulSoup
import requests
from dateutil import parser
from .utils import *


class Command(BaseCommand):
    help = 'Test command'

    def handle(self, *args, **options):
        channel_id = get_channel_id_by_url(
            'https://www.youtube.com/channel/UCvUSZ6IdVB7Re-wniMH80HQ')
        print(f'Channel id: {channel_id}')
        # video_title, video_url, video_published_date = get_last_video(
        #     channel_id)
        # print(video_title)
        # print(video_url)
        # print(video_published_date)
