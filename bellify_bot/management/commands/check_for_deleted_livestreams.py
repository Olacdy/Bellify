from django.core.management import BaseCommand
from django.utils.timezone import now
from youtube.models import YouTubeChannel, YouTubeVideo
from youtube.utils import check_if_video_is_exists


class Command(BaseCommand):
    help = 'Checks YouTube channels for deleted livestreams'

    def handle(self, *args, **options):
        for channel in YouTubeChannel.objects.all():
            for livestream in channel.livestreams.all():
                if (now() - livestream.ended_at).total_seconds() > 3600 and not livestream.is_checked_for_deleted:
                    livestream.set_checked()

                    saved_livestream = YouTubeVideo.objects.filter(
                        channel=channel, video_id__exact=livestream.livestream_id).first()

                    if not check_if_video_is_exists(livestream.livestream_url):
                        livestream.delete()
                        saved_livestream.delete() if saved_livestream else None
                        channel.increment_deleted_livestreams()
