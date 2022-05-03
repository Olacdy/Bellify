localization = {
    'en': {
        'commands': {'manage_command_text': "⚙️Manage Channels⚙️",
                     'language_command_text': "🗣️Language🗣️",
                     'help_command_text': "📑Help📑",
                     'upgrade_command_text': "⭐Upgrade⭐"},
        'notification':
        [
            ['New video from', 'is out!'],
            'is live now!',
        ],
        'add':
        [
            'Send Your custom channel name.',
            ['The new channel added with the name',
                '.\nThe last video is', '.\nChannel is live now!'],
            'Cannot add a new channel because a channel with the same name already exists.\nTry coming up with a new name, or leave the name parameter blank.',
        ],
        'manage':
        [
            '⚙️Manage Channels⚙️',
            'Sorry, but You have no added channels right now. Try to send a link.',
            'Looks like You have deleted all of Your channels.',
        ],
        'help':
        [
            """
Notification Bot manual. 

To add a channel to the list and further receive notifications about the release of new videos, use the /add command, then send a link to the channel (You can also just send a link to the channel, without the /add command). 
Specify the name under which You would like to save this channel, or skip this step. 

Now that a channel has been added to Your list, You will be notified when a new video is posted on it. 

If You would like to stop receiving notifications from this channel, use the /remove command and select the channel You want to remove.

To immediately check the channel for a new video on it, use the /check command. The selected channel will be checked, and if a new video is released, You will receive an alert with a link to a new video.

You can view the list of channels You have added using the /list command.

You can change the language of the bot using the /lang command.

To contact the developer: https://t.me/golovakanta.
"""
        ],
        'lang_start_command':
        [
            'Please, select a language.',
            'Thanks, You will continue to work in 🇬🇧.',
        ],
        'keyboard_command':
        [
            'Sending a keyboard...'
        ],
        'echo':
        [
            'Do You want to change the channel\'s name?',
            'This channel is already in your list. What You like to delete it?',
            'This channel is not on Your list. Would You like to add it?',
            'No channel with such a name.',
            'Sorry, You have exceeded Your limit on the number of channels. Try to delete one of the channels You have already added.\n\nOr support the project and increase Your limit.',
            'Doesn\'t look like a real channel URL, please try again.'
        ]
    },
    'ru': {
        'commands': {'manage_command_text': "⚙️Управление Каналами⚙️",
                     'language_command_text': "🗣️Язык🗣️",
                     'help_command_text': "📑Помощь📑",
                     'upgrade_command_text': "⭐Прокачать⭐"},
        'notification':
        [
            ['Новое видео от', 'уже вышло!'],
            'сейчас стримит!',
        ],
        'add':
        [
            'Можете прислать имя, под которым хотите сохранить канал.',
            ['Новый канал под именем', ' был добавлен.\nПоследнее видео',
                ' был добавлен.\nНа канале проходит трансляция!'],
            'Невозможно добавить новый канал под этим именем.\nПопробуйте придумать новое имя или оставить параметр имени пустым.',
        ],
        'manage':
        [
            '⚙️Управление Каналами⚙️',
            'Пока у Вас нет добавленных каналов. Поробуйте прислать ссылку.',
            'Похоже, Вы удалили все Ваши каналы.',
        ],
        'help':
        [
            """
Notification Bot мануал.

Для добавления канала в список и дальнейшего получения уведомлений о выходе новых видео, воспользуйтесь командой /add, после чего пришлите ссылку на канал (можно также просто прислать ссылку на канал, без команды /add).
Укажите имя, под которым Вы хотели бы сохранить этот канал, или пропустите этот шаг. 

Теперь, когда канал добавлен в Ваш список, Вы будете получать оповещения о выходе нового видео на нем.

В случае если Вы хотели бы перестать получать уведомления от этого канала, воспользуйтесь командой /remove и выберите канал, который хотите удалить.

Для немедленной проверки канала на наличие нового видео на нем, воспользуйтесь командой /check. Выбранный канал будет проверен и, в случае выхода нового видео, Вы получите оповещение со ссылкой на новое видео.

Просмотреть список добавленных Вами каналов можно с помощью команды /list.

Сменить язык работы бота можно с помощью команды /lang.

Для связи с разработчиком: https://t.me/golovakanta.
"""
        ],
        'lang_start_command':
        [
            'Пожалуйста, выберите язык.',
            'Спасибо, теперь работа будет продолжена на 🇷🇺.',
        ],
        'keyboard_command':
        [
            'Присылаем клавиатуру...'
        ],
        'echo':
        [
            'Хотите сохранить канал под Вашим именем?',
            'Этот канал уже есть в Вашем списке. Хотите его удалить?',
            'Этого канала еще нет в Вашем списке, хотите его добавить?',
            'Канала с таким именем не существует.',
            'Извините, Вы превысили Ваш лимит на количество каналов. Попробуйте удалить один из уже добавленных Вами каналов.\n\nИли поддержите проект и увеличьте Ваш лимит.',
            'URL-адрес не похож на реальный URL канала. Повторите попытку.',
        ]
    }
}
