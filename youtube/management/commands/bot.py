from django.core.management.base import BaseCommand
from django.conf import settings
from bs4 import BeautifulSoup
import requests
from dateutil import parser


class Command(BaseCommand):
    help = 'Test command'

    def handle(self, *args, **options):
        html = requests.get(
            f"https://www.youtube.com/feeds/videos.xml?channel_id=UCDxhdabUnR_cgTezoHRlZVg")
        soup = BeautifulSoup(html.text, "lxml")
        entry = soup.find("entry")
        print(entry)
        entry.find("title").text, entry.find("link")["href"], parser.parse(
            entry.find("published").text).strftime("%m/%d/%Y, %H:%M:%S")
