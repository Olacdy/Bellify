from django.conf import settings

reply_commands = {
    'manage_command_text': ["⚙️ Manage Channels", "⚙️ Управление Каналами"],
    'language_command_text': ["🌐 Language", "🌐 Смена языка"],
    'help_command_text': ["📑 Help", "📑 Помощь"],
    'upgrade_command_text': ["⭐ Upgrade", "⭐ Прокачать"]
}

localization = {
    'en': {
        'commands':
        {
            'manage_command_text': reply_commands['manage_command_text'][0],
            'language_command_text': reply_commands['language_command_text'][0],
            'help_command_text': reply_commands['help_command_text'][0],
            'upgrade_command_text': reply_commands['upgrade_command_text'][0]
        },
        'notification':
        [
            ['New video from', 'is out!'],
            'is live now!',
        ],
        'add':
        [
            'Now send Your own name for the channel:',
            ['The new channel added with the name',
                '.\nThe last video is', '.\nChannel is live now!', '.\nChannel is not currently live.'],
            'Cannot add a new channel because a channel with the same name already exists.\nTry coming up with a new name, or leave the name parameter blank.',
        ],
        'manage':
        [
            reply_commands["manage_command_text"][0],
            'Sorry, but You have no added channels right now. Try to send a link.',
            'Looks like You have deleted all of Your channels.',
        ],
        'upgrade':
        [
            'Select the product that You would like to purchase.\n\nBy clicking on the button, a payment form will be generated to pay with 💳 credit card.\n\nBy choosing/approving the payment/purchase you accept the \n<a href="https://telegra.ph/Bellify-Bot--Terms-and-Conditions-06-23-2">📃 Terms and Conditions</a>.',
            'Upgrade to Premium (YouTube and Twitch live notifications)',
            ['Increase max amount of', 'channels'],
            ['Upgrade to Premium',
             """
                Notifies You when YouTube and Twitch channels go live.
                Increases max YouTube channels (+{}).
                """.format(settings.INCREASE_CHANNELS_PREMIUM['YouTube']), 'Upgrade'],
            'Select the number of channels you would like to increase your quota by:',
            [['Increase', 'channels'],
                ['Increases max amount of', 'channels'], 'Increase'],
            'Back',
            'Oops, something went wrong...',
            'Thank You! The payment was successful.'
        ],
        'help':
        [
            ['Bellify Bot manual\n\nThis bot is capable of storing and notifying users when a new video is uploaded on the YouTube channel.\n\nIn premium mode, live stream notifications functionality is available for YouTube and Twitch channels.\n\nDeveloper contacts:\nTelegram - https://t.me/golovakanta\nGmail - dbofury@gmail.com\n\nTo start tutorial click on the button below.', 'Start tutorial'],
            'To start using this bot is recommended to complete a little tutorial. It will help You to familiarize the main functionality and using the bot right away.\n\nFirst things first, let\'s send a link to a sample YouTube channel.\nCopy the link below and send it to a bot.\n\nExample link:',
            ['At this point, You can decide whether You want to change the default channel name to Your custom one.\nChannel default name is: ',
                '\n\nWould You like to change it?'],
            f'To review added channels, You should use the \n"{reply_commands["manage_command_text"][0]}" button, which is available in the keyboard section, if there is no buttons use /menu command.\n\nTry to click on it.',
            'Here You can review Your channels.\n\nIf the channel has 🔔 state You will get an unmuted notification, which means a message with sound, but if the channel has 🔕 state You will get only messages, but no sound with it.\n\nTry to mute the channel and You\'ll see that icon will change its appearance (click on bell icon).',
            f'Consider that the tutorial is done, now You can leave the channel in Your list or delete it with ❌ button.\n\nBy default You have a quota for {settings.INITIAL_CHANNELS_NUMBER["YouTube"]} YouTube channels, You can increase it with "⭐ Upgrade" button.\n\nThe main feature of the bot is a new video notification, when a channel uploads a new video, You will get a notification. By upgrading to a premium, You will unlock Twitch and YouTube live stream functionality, which means notifications when channels start a live stream. Hoping You will be satisfied with this bot ❤️.\n\nTo start the tutorial again, use "{reply_commands["help_command_text"][0]}" button.',
            'For now, let\'s focus on 🔔 button.',
            'If the channel is already on Your list and You have sent its link again, You will be proposed to delete it right away or do nothing.'
        ],
        'language_command':
        [
            'Please, select a language.',
            'Thanks, You will continue to work in 🇬🇧English.',
        ],
        'keyboard_command':
        [
            'Sending a keyboard...'
        ],
        'echo':
        [
            ['The channel will be saved under name: ',
                '\nWould You like to change it?'],
            'This channel is already in your list. What You like to delete it?',
            'No channel with such a name.',
            'Sorry, You are do not have a premium account, so the Twitch channels is not availiable to You at the time.\n\nYou can support the project and upgrade to premium.',
            'Sorry, You have exceeded Your limit on the number of channels. Try to delete one of the channels You have already added.\n\nOr support the project and increase Your limit.',
            'Doesn\'t look like a channel URL. Please review the URL You sent and try again.'
        ]
    },
    'ru': {
        'commands':
        {
            'manage_command_text': reply_commands['manage_command_text'][1],
            'language_command_text': reply_commands['language_command_text'][1],
            'help_command_text': reply_commands['help_command_text'][1],
            'upgrade_command_text': reply_commands['upgrade_command_text'][1]
        },
        'notification':
        [
            ['Новое видео от', 'уже вышло!'],
            'сейчас стримит!',
        ],
        'add':
        [
            'Можете прислать имя, под которым хотите сохранить канал.',
            ['Новый канал под именем', ' был добавлен.\nПоследнее видео',
                ' был добавлен.\nНа канале проходит трансляция!', ' был добавлен.\nКанал не проводит трансляцию.'],
            'Невозможно добавить новый канал под этим именем.\nПопробуйте придумать новое имя или оставить параметр имени пустым.',
        ],
        'manage':
        [
            reply_commands["manage_command_text"][1],
            'Пока у Вас нет добавленных каналов. Поробуйте прислать ссылку.',
            'Похоже, Вы удалили все Ваши каналы.',
        ],
        'upgrade':
        [
            'Выберите товар, который Вы хотите приобрести.\n\nПосле нажатия на кнопку будет сгенерирована платежная форма для оплаты 💳 кредитной картой.\n\nПродолжив процесс оплаты вы соглашаетесь с \n<a href="https://telegra.ph/Bellify-Bot--Pravila-i-Usloviya-06-23">📃 Правилами и Условиями</a>.',
            'Перейти на Премиум (Уведомления, при начале трансляции)',
            ['Увеличить максимальное количество', 'каналов'],
            ['Переход на Премиум',
                f'Уведомляет Вас, когда YouTube или Twitch канал начинает трансляцию. Увеличивает максимальное количество YouTube каналов (+{settings.INCREASE_CHANNELS_PREMIUM["YouTube"]}).', 'Перейти'],
            'Выберите число каналов, на которое Вы бы хотели увеличить свою квоту:',
            [['Увеличить', 'каналы'],
                ['Увеличивает максимальное количество', 'каналов'], 'Увеличить'],
            'Назад',
            'Ой, что-то пошло не по плану...',
            'Спасибо! Оплата прошла успешно.'
        ],
        'help':
        [
            ['Bellify Bot мануал\n\nЭтот бот сохраняет пользовательские каналы и уведомляет их о выходе нового видео.\n\nВ премиум моде пользователи также будут получать уведомления о начале трансляции на YouTube и Twitch каналах.\n\nКонтакты разработчика:\nTelegram - https://t.me/golovakanta\nGmail - dbofury@gmail.com\n\nЧтобы начать обучение, нажмите на кнопку снизу.', 'Начать обучение'],
            'Для того чтобы начать пользоваться этим ботом, рекомендуется пройти небольшое обучение. Оно поможет Вам ознакомиться с основной функциональностью и пользоваться ботом без задержек.\n\nПрежде всего, давайте пришлем боту ссылку-пример.\nСкопируйте и пришлите ссылку ниже.\n\nСсылка-пример:',
            ['На этом моменте Вы можете решить, хотите ли Вы поменять имя канала на Ваше собственное.\nИмя канала сейчас: ',
                '\n\nХотите его поменять?'],
            f'Чтобы просмотреть добавленные каналы, Вам нужно нажать кнопку "{reply_commands["manage_command_text"][1]}", которая находиться в секции клавиатуры, если кнопки отсутствуют, воспользуйтесь командой /menu.\n\nПопробуйте на нее нажать.',
            'Здесь Вы можете просмотреть добавленные Вами каналы.\n\nЕсли канал имеет свойство 🔔, то Вы будете получать сообщения, которые сопровождаются еще и звуком, в противном случае, если канал имеет свойство 🔕, Вы будете получать лишь сообщение, но уже без звука.\n\nПопробуйте изменить текущее свойство нажатием на иконку колокольчика.',
            f'Считайте, что обучение окончено, теперь Вы можете либо оставить канал в Вашем списке, либо удалить его с помощью ❌.\n\nПо умолчанию, квота YouTube каналов равна {settings.INITIAL_CHANNELS_NUMBER["YouTube"]}, Вы можете увеличить ее з помощью кнопки "⭐ Прокачать".\n\nГлавная особенность бота - это уведомления, при выходе нового видео. В премиум режиме Вам также будет доступна функциональность уведомлений, при начале трансляции на Twitch и YouTube каналах. Надеюсь, что Вам придется по душе данный бот ❤️.\n\nЧтобы начать обучение заново, воспользуйтесь кнопкой \n"{reply_commands["help_command_text"][1]}".',
            'Пока пробуйте нажать 🔔',
            'Если ссылка на канал, которую Вы прислали уже добавлена в Ваш список, то Вам будет предложено либо удалить этот канал, либо ничего не делать.'
        ],
        'language_command':
        [
            'Пожалуйста, выберите язык.',
            'Спасибо, теперь работа будет продолжена на 🇷🇺Русском.',
        ],
        'keyboard_command':
        [
            'Присылаем клавиатуру...'
        ],
        'echo':
        [
            ['Канал будет сохранен по именем:',
                '\nХотите сохранить канал под другим именем?'],
            'Этот канал уже есть в Вашем списке. Хотите его удалить?',
            'Канала с таким именем не существует.',
            'Извините, но Ваш аккаунт не является премиумным, поэтому добавление Twitch каналов Вам пока не доступно.\n\nВы можете поддержать проект и улучшить аккаунт.',
            'Извините, Вы превысили Ваш лимит на количество каналов. Попробуйте удалить один из уже добавленных Вами каналов.\n\nИли поддержите проект и увеличьте Ваш лимит.',
            'URL-адрес не похож на реальный URL канала. Пожалуйста, проверьте правильность URL и повторите попытку.',
        ]
    }
}
