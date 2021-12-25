from telegram import Update
from telegram.ext import CallbackContext
from .utils import get_or_create_profile, log_errors


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    p, _ = get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode = query.data.split('_')[0]

    if mode == 'lang':
        lang_for_lang = {
            'en': 'Thanks, You`ll continue work on English.',
            'ru': 'Спасибо, теперь работа будет продолжена на русском.'
        }

        p.language = query.data.split('_')[1]
        p.save()

        query.edit_message_text(
            text=lang_for_lang[query.data.split('_')[1]],
            parse_mode='HTML')
