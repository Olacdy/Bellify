from telegram import Update
from telegram.ext import CallbackContext
from youtube.models import ChannelUserItem
from .utils import get_or_create_profile, log_errors, set_menu_field, add, check, remove


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    p, _ = get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode = query.data.split('_')[0]

    if mode == 'lang':
        lang_for_lang = {
            'en': 'Thanks, You\'ll continue work on English.',
            'ru': 'Спасибо, теперь работа будет продолжена на русском.'
        }

        p.language = query.data.split('_')[1]
        p.save()

        query.edit_message_text(
            text=lang_for_lang[query.data.split('_')[1]],
            parse_mode='HTML'
        )

    elif mode == 'add':
        lang_for_add = {
            'en': 'Send Your custom channel name.',
            'ru': 'Можете прислать имя, под которым хотите сохранить канал.'
        }

        if query.data.split('_')[-1] == 'yes':
            query.edit_message_text(
                text=lang_for_add[p.language],
                parse_mode='HTML'
            )
            set_menu_field(p, f"name_{query.data.split('_')[1]}")
        else:
            query.delete_message()
            add(query.data.split('_')[-1], update, p)
    elif mode == 'check':
        lang_for_check = {
            'en': 'No channel with such name.',
            'ru': 'Канала с таким именем не существует.'
        }

        if 'next' in query.data.split('_'):
            pass
        else:
            channel_id = query.data.split('_')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=p) if channel.channel.channel_id == channel_id][0]
                check(update, p, channel_name)
            except:
                query.edit_message_text(
                    text=lang_for_check[p.language],
                    parse_mode='HTML'
                )
    elif mode == 'remove':
        lang_for_remove = {
            'en': 'No channel with such name.',
            'ru': 'Канала с таким именем не существует.'
        }

        if 'next' in query.data.split('_'):
            pass
        else:
            channel_id = query.data.split('_')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=p) if channel.channel.channel_id == channel_id][0]
                remove(update, p, channel_name)
            except:
                query.edit_message_text(
                    text=lang_for_remove[p.language],
                    parse_mode='HTML'
                )
    elif mode == 'list':
        pass
