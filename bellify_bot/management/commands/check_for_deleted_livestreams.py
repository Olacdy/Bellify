from django.core.management import BaseCommand
from django.utils.timezone import now
from youtube.models import YouTubeChannel, YouTubeVideo


class Command(BaseCommand):
    help = 'Checks YouTube channels for deleted livestreams'

    def handle(self, *args, **options):
        for channel in YouTubeChannel.objects.all():
            for livestream in channel.livestreams.all():
                saved_livestream = YouTubeVideo.objects.filter(
                    channel=channel, video_id__exact=livestream.livestream_id).first()

                if livestream.ended_at:
                    if saved_livestream and ((now() - saved_livestream.create_at).seconds > 3600) and saved_livestream.skipped_iterations > 0:
                        channel.increment_deleted_livestreams()
                        saved_livestream.delete()
                    elif (now() - livestream.ended_at).seconds > 3600 and not livestream.counted_as_deleted:
                        livestream.count_as_deleted()
