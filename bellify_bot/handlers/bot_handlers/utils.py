import itertools
from typing import Dict, List, Optional

from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from celery.utils.log import get_task_logger
from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice,
                      Message, Update)
from twitch.models import TwitchChannel, TwitchChannelUserItem
from twitch.utils import (get_streams_info,
                          get_twitch_streams_info, get_users_info)
from youtube.models import (YouTubeChannel, YouTubeChannelUserItem,
                            YouTubeLivestream, YouTubeVideo)
from youtube.utils import (get_url_from_id, get_youtube_livestreams,
                           get_youtube_videos, scrape_id_and_title_by_url,
                           scrape_last_videos, scrape_livesteams)

from utils.general_utils import (send_messages, get_html_bold, get_html_link,
                                 get_manage_message)
from utils.keyboards import (get_manage_inline_keyboard,
                             get_notification_reply_markup,
                             get_upgrade_inline_keyboard, log_errors)

logger = get_task_logger(__name__)


# Checks for streams and alerts every premium user if there is one
@log_errors
def check_twitch() -> None:
    channels: List[TwitchChannel] = TwitchChannel.get_channels_to_review()
    channels_ids = [channel.channel_id for channel in channels]
    channels_ids = [channels_ids[i * 100:(i + 1) * 100]
                    for i in range((len(channels_ids) + 100 - 1) // 100)]

    live_info = {stream_item[0]: stream_item[1:]
                 for stream_item in get_twitch_streams_info(channels_ids)}

    livestream_notification_urls = []

    for channel in channels:
        if channel.channel_id in live_info:
            stream_data = live_info[channel.channel_id]
            if stream_data[3] != channel.is_live:
                channel.update(
                    live_title=stream_data[0], game_name=stream_data[1], thumbnail_url=stream_data[2], is_live=stream_data[3])
                if channel.is_threshold_passed:
                    livestream_notification_urls.append(get_urls_to_notify(users=[item.user for item in TwitchChannelUserItem.objects.filter(channel=channel)], channel_id=channel.channel_id, url=channel.channel_url, content_title=channel.live_title,
                                                                           game_name=channel.game_name, preview_url=channel.preview_url, is_live=True))
        else:
            channel.update()

    send_messages(list(itertools.chain.from_iterable(
        livestream_notification_urls)))


# Checks for livestreams and new videos and alerts users if the are some
@log_errors
def check_youtube() -> None:
    channels: List[YouTubeChannel] = YouTubeChannel.get_channels_to_review()
    channels_premium: List[YouTubeChannel] = YouTubeChannel.get_channels_to_review_premium(
    )

    channels_videos_info = get_youtube_videos(
        [channel.channel_id for channel in channels])
    channels_livestreams_info = get_youtube_livestreams(
        [channel.channel_id for channel in channels_premium])

    livestream_notification_urls = []
    video_notification_urls = []

    for channel_premium, channel_livestreams_info_item in zip(channels_premium, channels_livestreams_info):
        for livestream in YouTubeLivestream.get_new_livestreams(channel_premium, channel_livestreams_info_item):
            if livestream.is_new:
                livestream_notification_urls.append(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel_premium, user__status='P')], channel_id=channel_premium.channel_id, url=livestream.livestream_url,
                    content_title=livestream.livestream_title, is_live=True))
                livestream.notified()

    for channel, channel_videos_info_item in zip(channels, channels_videos_info):
        if channel_videos_info_item:
            for video in YouTubeVideo.get_new_videos(channel, channel_videos_info_item):
                if video.is_new:
                    video_notification_urls.append(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                        channel=channel, user__status='B')], channel_id=channel.channel_id, url=video.video_url,
                        content_title=video.video_title, is_reuploaded=video.is_reuploaded))

                if video.is_new or video.iterations_skipped > 0:
                    if video.is_ended_livestream and channel.check_for_deleting_livestreams and not video.is_able_to_notify:
                        video.skip_iteration()
                    else:
                        video_notification_urls.append(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                            channel=channel, user__status='P')], channel_id=channel.channel_id, url=video.video_url,
                            content_title=video.video_title, is_reuploaded=video.is_reuploaded,
                            is_ended_livestream=video.is_ended_livestream, is_might_be_deleted=channel.is_deleting_livestreams))
                        video.notified()

    send_messages(list(itertools.chain.from_iterable(
        video_notification_urls + livestream_notification_urls)))


# Checks channel url type and call add function accordingly
@log_errors
def add(channel_id: str, channel_type: str, message: Message, user: User, name: Optional[str] = None) -> None:
    if 'YouTube' in channel_type:
        _add_youtube_channel(channel_id, message, user, name)
    elif 'Twitch' in channel_type:
        _add_twitch_channel(channel_id, message, user, name)


# Adds Twitch channel to a given user
@log_errors
def _add_twitch_channel(channel_id: str, message: Message, user: User, name: Optional[str] = None) -> None:
    channel: TwitchChannel

    def _get_twitch_channel_message(u: User, channel_url: str, channel_name: str, game_name: str, preview_url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        name = get_html_bold(channel_name) if is_live else get_html_link(
            channel_url, channel_name)
        is_streaming = localization[u.language]['add'][1][
            1 if is_live and not 'Just Chatting' in game_name else 2 if not is_live else 3]
        game = f" {localization[u.language]['add'][1][4]} {game_name+'.'}" if (
            is_live and not 'Just Chatting' in game_name) else ''
        thumb_href = f"{get_html_link(url=preview_url) if is_live else ''}"
        return f'{general}{name}{is_streaming}{game}{thumb_href}'

    if not TwitchChannel.is_channel_exists(channel_id):
        _, channel_login, channel_title = get_users_info(
            ids=[channel_id])[0]

        channel, _ = TwitchChannel.objects.update_or_create(
            channel_id=channel_id,
            channel_title=channel_title,
            channel_login=channel_login,
        )

        stream_data = get_streams_info([channel_id])
        if stream_data:
            _, live_title, game_name, thumbnail_url, is_live = stream_data[0]
        else:
            live_title, game_name, thumbnail_url, is_live = None, None, None, False
    else:
        channel = TwitchChannel.objects.get(
            channel_id=channel_id)
        channel_title = channel.channel_title

        live_title, game_name, thumbnail_url, is_live = channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live

    channel_name = name if name else channel_title

    channel.update(live_title=live_title, game_name=game_name,
                   thumbnail_url=thumbnail_url, is_live=is_live)

    if not user in channel.users.all():
        if not TwitchChannelUserItem.objects.filter(user=user, channel_title=channel_name).exists():
            item = TwitchChannelUserItem.objects.create(
                user=user, channel=channel, channel_title=channel_name)

            message.reply_text(
                text=_get_twitch_channel_message(
                    user, channel.channel_url, item.message_title_and_type, game_name,
                    channel.channel_url if user.is_twitch_thumbnail_disabled else channel.preview_url, is_live),
                parse_mode='HTML',
                reply_markup=get_notification_reply_markup(
                    live_title if is_live else channel_name, channel.channel_url)
            )
            if not user.is_tutorial_finished:
                message.reply_text(
                    text=localization[user.language]['help'][3],
                    parse_mode='HTML',
                )
        else:
            message.reply_text(
                text=localization[user.language]['add'][2],
                parse_mode='HTML'
            )


# Adds YouTube channel to a given user
@log_errors
def _add_youtube_channel(channel_id: str, message: Message, user: User, name: Optional[str] = None) -> None:
    channel: YouTubeChannel

    def _get_youtube_channel_message(u: User, channel_name: str, url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        channel_name = get_html_bold(channel_name)
        is_streaming = localization[u.language]['add'][1][1 if not is_live else 3]
        href = f'{get_html_link(url=url)}'
        return f'{general}{channel_name}{is_streaming}{href}'

    if not YouTubeChannel.is_channel_exists(channel_id):
        _, channel_title = scrape_id_and_title_by_url(
            get_url_from_id(channel_id))

        channel, _ = YouTubeChannel.objects.update_or_create(
            channel_id=channel_id,
            channel_title=channel_title
        )

        videos = scrape_last_videos(channel_id)
        livestreams = scrape_livesteams(channel_id)

        for livestream_id in livestreams:
            YouTubeLivestream.objects.get_or_create(
                livestream_id=livestream_id,
                livestream_title=livestreams[livestream_id],
                channel=channel
            )

        for video_id in videos:
            YouTubeVideo.objects.get_or_create(
                video_id=video_id,
                video_title=videos[video_id][0],
                is_saved_livestream=videos[video_id][1],
                channel=channel
            )
    else:
        channel = YouTubeChannel.objects.get(channel_id=channel_id)
        channel_title = channel.channel_title

    channel_name = name if name else channel_title

    if not user in channel.users.all():
        if not YouTubeChannelUserItem.objects.filter(user=user, channel_title=channel_title).exists():
            item = YouTubeChannelUserItem.objects.create(
                user=user, channel=channel, channel_title=channel_name)

            ongoing_livestream = channel.ongoing_livestream
            last_video = channel.last_video

            if ongoing_livestream and user.status == 'P':
                message.reply_text(
                    text=_get_youtube_channel_message(
                        user, item.message_title_and_type, ongoing_livestream.livestream_url, True),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        ongoing_livestream.livestream_title, ongoing_livestream.livestream_url)
                )
            elif last_video:
                message.reply_text(
                    text=_get_youtube_channel_message(
                        user, item.message_title_and_type, last_video.video_url, False),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        last_video.video_title, last_video.video_url)
                )
            if not user.is_tutorial_finished:
                message.reply_text(
                    text=localization[user.language]['help'][3],
                    parse_mode='HTML',
                )
        else:
            message.reply_text(
                text=localization[user.language]['add'][2],
                parse_mode='HTML'
            )


# Function that handles users notifications
def get_urls_to_notify(users: List[User], channel_id: str, url: str, content_title: str, game_name: Optional[str] = None, preview_url: Optional[str] = None, is_reuploaded: Optional[bool] = False, is_live: Optional[bool] = False, is_ended_livestream: Optional[bool] = False, is_might_be_deleted: Optional[bool] = False) -> None:
    def _get_message(user: User, channel_title: str, url: str, game_name: Optional[str] = None, preview_url: Optional[str] = None, is_reuploaded: Optional[bool] = False, is_live: Optional[bool] = False, is_ended_livestream: Optional[bool] = False, is_might_be_deleted: Optional[bool] = False) -> str:
        channel_title = get_html_bold(channel_title)

        if is_live:
            notification = f" — {localization[user.language]['notification'][1] if not game_name or game_name == 'Just Chatting' else localization[user.language]['notification'][2]+' '+game_name+'!'}"
            href = f"{get_html_link(url=preview_url if preview_url and not user.is_twitch_thumbnail_disabled else url)}"
            return f"{channel_title}{notification}{href}"
        else:
            if is_reuploaded:
                notification = f" — {localization[user.language]['notification'][3]}"
            elif is_ended_livestream:
                notification = f" — {localization[user.language]['notification'][4]}{(' ' + localization[user.language]['notification'][5]) if is_might_be_deleted else ''}"
            else:
                notification = f" — {localization[user.language]['notification'][0]}"
            href = f"{get_html_link(url=url)}"
            return f"{channel_title}{notification}{href}"

    def _get_url(user_id: str, message: str, disable_notification: Optional[bool] = False, reply_markup: Optional[List[List[Dict]]] = None, parse_mode: Optional[str] = 'HTML') -> str:
        return f'https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={user_id}&parse_mode={parse_mode}&text={message}&disable_notification={disable_notification}&reply_markup={reply_markup.to_json()}'

    return [_get_url(user_id=user.user_id,
                     message=_get_message(user=user, channel_title=item.message_title_and_type, url=url,
                                          game_name=game_name, preview_url=preview_url,
                                          is_reuploaded=is_reuploaded, is_live=is_live,
                                          is_ended_livestream=is_ended_livestream,
                                          is_might_be_deleted=is_might_be_deleted),
                     disable_notification=item.is_muted,
                     reply_markup=get_notification_reply_markup(
                         content_title, url)) for user, item in zip(users, [ChannelUserItem.get_channel_by_user_and_channel_id(user, channel_id) for user in users])]


# Removes given channel user item
@log_errors
def remove(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    channel.delete() if u.is_tutorial_finished and channel else None
    manage(update, u, mode='remove', page_num=page_num)


# Mutes given channel user item
@log_errors
def mute(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    channel.mute_channel() if channel else None
    manage(update, u, mode='mute', page_num=page_num)


# Returns Manage replies according to call situation
@log_errors
def manage(update: Update, u: User, mode: Optional[str] = 'echo', page_num: Optional[int] = 0) -> None:
    keyboard = get_manage_inline_keyboard(u, page_num=page_num)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)

        if 'echo' in mode:
            update.message.reply_text(
                text=get_manage_message(u, mode='echo'),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=get_manage_message(u),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            u.set_tutorial_state(True) if not u.is_tutorial_finished else None
    else:
        if 'echo' in mode:
            update.message.reply_text(
                text=localization[u.language]['manage'][1],
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=localization[u.language]['manage'][2],
                parse_mode='HTML'
            )


# First reply on Upgrade command
@log_errors
def upgrade(message: Message, u: User):
    message.reply_text(
        text=localization[u.language]['upgrade'][0],
        reply_markup=InlineKeyboardMarkup(get_upgrade_inline_keyboard(u)),
        parse_mode='HTML'
    )


# Reply on user invoice
@log_errors
def reply_invoice(update: Update, u: User, title: str, description: str, payload: str, buy_button_label: str, price: int, mode: Optional[str] = 'upgrade'):
    keyboard = [
        [
            InlineKeyboardButton(buy_button_label, pay=True)
        ],
        [
            InlineKeyboardButton(
                localization[u.language]['upgrade'][6], callback_data=f'upgrade{settings.SPLITTING_CHARACTER}back{settings.SPLITTING_CHARACTER}{mode}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_invoice(
        title=title,
        description=description,
        payload=payload,
        provider_token=settings.PROVIDER_TOKEN,
        currency=settings.CURRENCY,
        prices=[LabeledPrice(description[:-1], (price - 1)
                             if not repr(price)[-1] == '5' else price)],
        reply_markup=reply_markup
    )
