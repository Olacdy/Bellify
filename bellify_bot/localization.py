from django.conf import settings

localization = {
    'en': {
        'notification':
        [
            'new video is out!',
            'is live now!',
            'is playing',
        ],
        'add':
        [
            'Now send Your own name for the channel.',
            ['The new channel —',
                ' has been added.', ' has been added.\nChannel is not currently live.', ' has been added.\nChannel is live now!', '\nPlaying'],
            'Cannot add a new channel because a channel with the same name already exists.\nTry coming up with a new name, or leave the name parameter blank.',
        ],
        'manage':
        [
            ['⚙️ Manage Channels ⚙️', 'Remaining', 'quota:'],
            'Sorry, but You have no added channels right now. Try to send a link.',
            'Looks like You have deleted all of Your channels.',
        ],
        'upgrade':
        [
            'Select the product that You would like to purchase.\n\nBy clicking on the button, a payment form will be generated to pay with 💳 credit card.\n\nBy choosing/approving the payment/purchase you accept the \n<a href="https://telegra.ph/Bellify-Bot--Terms-and-Conditions-06-23-2">📃 Terms and Conditions</a>.',
            'Upgrade to Premium (YouTube and Twitch live notifications)',
            ['Increase', 'quota'],
            ['Upgrade to Premium',
                f'Notifies You when YouTube and Twitch channels go live. Increases YouTube and Twitch quota by {str(settings.CHANNELS_INFO["youtube"]["premium_increase"])+" and "+str(settings.CHANNELS_INFO["twitch"]["premium_increase"])+" respectively." if not settings.CHANNELS_INFO["youtube"]["premium_increase"] == settings.CHANNELS_INFO["twitch"]["premium_increase"] else str(settings.CHANNELS_INFO["youtube"]["premium_increase"])+"."}', 'Upgrade'],
            ['Your', 'quota now equals',
                'Select the number of channels you would like to increase your quota by:'],
            [['Increase', 'channels'],
                ['Increases max amount of', 'channels'], 'Increase'],
            'Back',
            'Oops, something went wrong...',
            'Thank You! The payment was successful.'
        ],
        'help':
        [
            ['Bellify Bot manual\n\nThis bot is capable of storing and notifying users when a new video is uploaded on the YouTube channel.\n\nIn premium mode, live stream notifications functionality is available for YouTube and Twitch channels.\n\nDeveloper contacts:\nTelegram - https://t.me/golovakanta\nGmail - dbofury@gmail.com\n\nTo start tutorial click on the button below.', 'Start tutorial'],
            ['To start using this bot is recommended to complete a little tutorial. It will help You to familiarize the main functionality and using the bot right away.\n\nFirst things first, let\'s send a link to a sample YouTube channel.\nCopy the link below and send it to a bot.\n\nExample link (click on it):',
             'You have already added all of the sample channels.\n\nUse /manage command to continue the tutorial.'],
            ['At this point, You can decide whether You want to change the default channel name to Your custom one.\nChannel default name is: ',
                '\n\nWould You like to keep this name?'],
            f'To review added channels, You should use the /manage command, which is available in the "Menu" section.\n\nThe colored square next to the channel name means its type:\n\n{settings.CHANNELS_INFO["youtube"]["icon"]} - {settings.CHANNELS_INFO["youtube"]["name"]}, {settings.CHANNELS_INFO["twitch"]["icon"]} - {settings.CHANNELS_INFO["twitch"]["name"]}\n\nTry to click on the /manage.',
            'Here You can review Your channels.\n\nIf the channel has 🔔 state You will get an unmuted notification, which means a message with sound, but if the channel has 🔕 state You will get only messages, but no sound with it.\n\nTry to mute the channel and You\'ll see that icon will change its appearance (click on bell icon).',
            f'Consider that the tutorial is completed successfully.\n\nFrom now on, You can decide to leave the channel in Your list or delete it with ❌ button.\n\nBy default You have a quota for {settings.CHANNELS_INFO["youtube"]["initial_number"]} YouTube channels, You can increase it with /upgrade command.\n\nThe main feature of the bot is a new video notification, when a channel uploads a new video, You will get a notification. By upgrading to a premium, You will unlock Twitch and YouTube live stream functionality, which means notifications when channels start a live stream. Hoping You will be satisfied with this bot ❤️.\n\nTo start the tutorial again, use /help command.',
            'For now, let\'s focus on 🔔 button.',
            'If the channel is already on Your list and You have sent its link again, You will be proposed to delete it right away or do nothing.'
        ],
        'language_command':
        [
            'Please, select a language.',
            'Thanks, the work will be continued in 🇬🇧English.',
        ],
        'echo':
        [
            ['The channel will be saved under name: ',
                '\nWould You like to keep this name?'],
            'This channel is already in your list. What You like to delete it?',
            'No channel with such a name.',
            'Sorry, You are do not have a premium account, so the Twitch channels is not availiable to You at the time.\n\nYou can support the project and upgrade to premium.',
            ['Sorry, You have exceeded Your limit on the number of channels. Try to delete one of the channels You have already added.\n\nOr support the project and increase Your limit.',
             'Looks like You are already have added channels.\n\nYou can increase Your quota or use /manage command to continue the tutorial.'],
            'Doesn\'t look like a channel URL. Please review the URL You sent and try again.'
        ]
    },
    'ru': {
        'notification':
        [
            'новое видео уже вышло!',
            'сейчас стримит!',
            'играет в',
        ],
        'add':
        [
            'Можете прислать имя, под которым хотите сохранить канал.',
            ['Новый канал —', ' добавлен.',
                ' добавлен.\nКанал не транслирует.', ' добавлен.\nКанал транслирует!', '\nИграет в'],
            'Невозможно добавить новый канал под этим именем.\nПопробуйте придумать новое имя или оставить параметр имени пустым.',
        ],
        'manage':
        [
            ['⚙️ Управление Каналами ⚙️', 'Остаток', 'квоты:'],
            'Пока у Вас нет добавленных каналов. Попробуйте прислать ссылку.',
            'Похоже, Вы удалили все Ваши каналы.',
        ],
        'upgrade':
        [
            'Выберите товар, который Вы хотите приобрести.\n\nПосле нажатия на кнопку будет сгенерирована платежная форма для оплаты 💳 картой.\n\nПродолжив процесс оплаты, Вы соглашаетесь с \n<a href="https://telegra.ph/Bellify-Bot--Pravila-i-Usloviya-06-23">📃 Правилами и Условиями</a>.',
            'Перейти на Премиум (Уведомления, при начале трансляции)',
            ['Увеличить', 'квоту'],
            ['Переход на Премиум',
                f'Уведомляет Вас, когда YouTube или Twitch канал начинает трансляцию. Увеличивает YouTube и Twitch квоту на {str(settings.CHANNELS_INFO["youtube"]["premium_increase"])+" и "+str(settings.CHANNELS_INFO["twitch"]["premium_increase"])+" соответственно." if not settings.CHANNELS_INFO["youtube"]["premium_increase"] == settings.CHANNELS_INFO["twitch"]["premium_increase"] else str(settings.CHANNELS_INFO["youtube"]["premium_increase"])+"."}', 'Перейти'],
            ['Ваша', 'квота сейчас равна',
                'Выберите число каналов, на которое Вы бы хотели увеличить свою квоту:'],
            [['Увеличить', 'каналы'],
                ['Увеличивает максимальное количество', 'каналов'], 'Увеличить'],
            'Назад',
            'Ой, что-то пошло не по плану...',
            'Спасибо! Оплата прошла успешно.'
        ],
        'help':
        [
            ['Bellify Bot мануал\n\nЭтот бот сохраняет добавленные каналы и уведомляет пользователей о выходе нового видео.\n\nВ премиум моде пользователи также будут получать уведомления о начале трансляции на YouTube и Twitch каналах.\n\nКонтакты разработчика:\nTelegram - https://t.me/golovakanta\nGmail - dbofury@gmail.com\n\nЧтобы начать обучение, нажмите на кнопку ниже.', 'Начать обучение'],
            ['Для того чтобы начать пользоваться этим ботом, рекомендуется пройти небольшое обучение. Оно поможет Вам ознакомиться с основной функциональностью и пользоваться ботом без задержек.\n\nПрежде всего, давайте пришлем боту ссылку-пример.\nСкопируйте и пришлите ссылку ниже.\n\nСсылка-пример (нажмите, чтобы скопировать):',
             'Вы уже добавили все ссылки-примеры.\n\nВоспользуйтесь командой /manage, чтобы продолжить обучение.'],
            ['На этом моменте Вы можете решить, хотите ли Вы поменять имя канала установив собственное.\nИмя канала сейчас: ',
                '\n\nХотите оставить это имя?'],
            f'Чтобы просмотреть добавленные каналы, Вам нужно воспользоваться командой /manage, которая находиться в "Меню".\n\nЦветные квадраты возле имени канала означают его тип:\n\n{settings.CHANNELS_INFO["youtube"]["icon"]} - {settings.CHANNELS_INFO["youtube"]["name"]}, {settings.CHANNELS_INFO["twitch"]["icon"]} - {settings.CHANNELS_INFO["twitch"]["name"]}\n\nПопробуйте нажать на /manage.',
            'Здесь Вы можете просмотреть добавленные Вами каналы.\n\nЕсли канал имеет свойство 🔔, то Вы будете получать сообщения в обычном режиме, в противном случае, если канал имеет свойство 🔕, Вы будете получать сообщения от канала без звука.\n\nПопробуйте изменить текущее свойство нажатием на иконку колокольчика.',
            f'Считайте, что обучение успешно завершено.\n\nТеперь Вы можете либо оставить канал в Вашем списке, либо удалить его с помощью ❌.\n\nПо умолчанию, квота YouTube каналов равна {settings.CHANNELS_INFO["youtube"]["initial_number"]}, Вы можете увеличить ее з помощью команды /upgrade.\n\nГлавная особенность бота - это уведомления при выходе нового видео. В премиум режиме Вам также будет доступна возможность получать уведомления о начале трансляции на Twitch и YouTube каналах. Надеюсь, что Вам придется по душе данный бот ❤️.\n\nЧтобы повторить обучение, воспользуйтесь командой /help.',
            'Пока пробуйте нажать 🔔',
            'Если ссылка на канал, которую Вы прислали уже добавлена в Ваш список, то Вам будет предложено либо удалить этот канал, либо ничего не делать.'
        ],
        'language_command':
        [
            'Пожалуйста, выберите язык.',
            'Спасибо, работу будет продолжено на 🇷🇺Русском.',
        ],
        'echo':
        [
            ['Канал будет сохранен по именем: ',
                '\nХотите оставить это имя?'],
            'Этот канал уже есть в Вашем списке. Хотите его удалить?',
            'Канала с таким именем не существует.',
            'Извините, но Ваш аккаунт не является премиумным, поэтому добавление Twitch каналов Вам пока не доступно.\n\nВы можете поддержать проект и улучшить аккаунт.',
            ['Извините, Вы превысили Ваш лимит на количество каналов. Попробуйте удалить один из уже добавленных Вами каналов.\n\nИли поддержите проект и увеличьте Ваш лимит.',
             'Похоже, что Вы уже имеете добавленные каналы.\n\nВы можете увеличить Вашу квоту, или же воспользуйтесь командой /manage, чтобы продолжить обучение.'],
            'URL-адрес не похож на реальный URL канала. Пожалуйста, проверьте правильность URL и повторите попытку.',
        ]
    },
    'ua': {
        'notification':
        [
            'нове відео вже вийшло!',
            'зараз транслює!',
            'грає в',
        ],
        'add':
        [
            'Можете прислати ім\'я, під яким Ви хочете зберегти канал.',
            ['Новий канал —', ' додано.',
                ' додано.\nКанал не транслює.', ' додано.\nКанал транслює!', '\nГрає в'],
            'Неможливо додати новий канал під цим ім\'ям.\nСпробуйте вигадати нове ім\'я або ж залишити цей параметр незаповнюючи.',
        ],
        'manage':
        [
            ['⚙️ Керування каналами ⚙️', 'Залишок', 'квоти:'],
            'Доки у Вас немає доданих каналів. Спробуйте надіслати посилання.',
            'Схоже, що Ви видалил усі Ваші канали.',
        ],
        'upgrade':
        [
            'Оберіть товар, який Ви хочете придбати.\n\nПісля натискання на кнопку буде сгенеровано платіжну форму для сплати 💳 карткою.\n\nПродовживши процес сплати, Ви погоджуєтесь з \n<a href="https://telegra.ph/Bellify-Bot--Pravila-ta-Umovi-07-11">📃 Правилами та Умовами</a>.',
            'Перейти на Преміум (Повідомлення про трансляції)',
            ['Збільшити', 'квоту'],
            ['Перехід на Преміум',
                f'Повідомляє, коли YouTube або Twitch канал починає трансляцію. Збільшує YouTube та Twitch квоту на {str(settings.CHANNELS_INFO["youtube"]["premium_increase"])+" та "+str(settings.CHANNELS_INFO["twitch"]["premium_increase"])+" відповідно." if not settings.CHANNELS_INFO["youtube"]["premium_increase"] == settings.CHANNELS_INFO["twitch"]["premium_increase"] else str(settings.CHANNELS_INFO["youtube"]["premium_increase"])+"."}', 'Перейти'],
            ['Ваша', 'квота зараз дорівнює',
                'Оберіть число каналів, на яке Ви хотіл б збільшити свою квоту:'],
            [['Збільшити', 'канали'],
                ['Збільшити максимальну кількість', 'каналів'], 'Збільшити'],
            'Назад',
            'Ой, щось пішло не так...',
            'Дякуємо! Оплата прошла успішно.'
        ],
        'help':
        [
            ['Bellify Bot мануал\n\nЦей бот зберігає додані канали та повідомляє користувачів при виході нового відео.\n\nУ преміум режимі користувачі також будуть отримувати повідомлення про початок трансляції на YouTube та Twitch каналах.\n\nКонтакти розробника:\nTelegram - https://t.me/golovakanta\nGmail - dbofury@gmail.com\n\nДля того аби почати туторіал, натисніть на кнопку нижче.', 'Почати туторіал'],
            ['Аби почати користуватись цим ботом, рекомендовано завершити невеличкий туторіал. Він допоможе ознайомитись Вам з основною функціональністю та почати користування ботом без затримок.\n\nПерш за все, давайте надішлемо боту посилання-приклад.\nСкопіюйте та надішліть посилання нижче.\n\nПосилання-приклад (натисніть, щоб скопіювати):',
             'Ви вже додали усі посилання-приклади.\n\nДля того аби продовжити туторіал, скористайтеся командою /manage.'],
            ['На цьому етапі Ви можете вирішити, чи хочете змінити ім\'я канала, встановивши власне.\nІм\'я канала зараз: ',
                '\n\nХочете залишити це ім\'я?'],
            f'Для того аби продивитись додані Вами канали, Вам необхідно скористатись командою /manage, яка знаходиться в "Меню".\n\nКольорові квадрати біля імені каналу означають його тип:\n\n{settings.CHANNELS_INFO["youtube"]["icon"]} - {settings.CHANNELS_INFO["youtube"]["name"]}, {settings.CHANNELS_INFO["twitch"]["icon"]} - {settings.CHANNELS_INFO["twitch"]["name"]}\n\nСпробуйте натиснути на /manage.',
            'Тут Ви можете продивитись додані Вами канали.\n\nЯкщо канал має властивість 🔔, то Ви будете отримувати повідомлення у звичайному режимі, в іншому випадку, якщо канал має властивість 🔕, Ви будете отримувати повідомлення від цього каналу без звуку.\n\nСпробуйте змінити поточну властивість натисканням на дзвіночок.',
            f'Вважайте, що туторіал успішно закінчено.\n\nТеперь Ви можете або залишити канал у Вашому списку, або видалити його за допомогою ❌.\n\nЗа замовчуванням, квота YouTube каналів дорівнює {settings.CHANNELS_INFO["youtube"]["initial_number"]}, Ви можете збільшити її за допомогою команди /upgrade.\n\nГоловна особливість бота - це повідомлення при виході нового відео. У преміум режимі Вам також буде доступна можливість отримання повідомлень про початок трансляцій на Twitch та YouTube каналах. Сподіваюся, що Вам припаде до душі цей бот ❤️.\n\nЩоб повторити туторіал, скористайтесь командою /help.',
            'Поки спробуйте натиснути 🔔',
            'Якщо посилання на канал, яке Ви надіслали вже додано до Вашого списку, то Вам буде запропоновано або видалити цей канал, або нічого не робити.'
        ],
        'language_command':
        [
            'Будь-ласка оберіть мову.',
            'Дякуємо, роботу буде продовжено 🇺🇦Українською.',
        ],
        'echo':
        [
            ['Канал буде збережено під ім\'ям: ',
                '\nХочете залишити це ім\'я?'],
            'Цей канал вже є у Вашому списку. Хочете його видалити?',
            'Канала з таким ім\'ям не існує.',
            'Вибачте, але Ваш акаунт не має статусу преміум, тому додавання Twitch каналів Вам поки не доступне.\n\nВи можете підтримати проект та покращити акаунт.',
            ['Вибачте, Ви перевищили Ваш ліміт на кількість каналів. Спробуйте видалити один з вже доданих Вами каналів.\n\nАбо підтримайте проект та збільшіть Ваш ліміт.',
             'Схоже, що Ви вже маєте додані канали.\n\nВи можете збільшити Вашу квоту, або ж скористайтеся командою /manage, аби продовжити туторіал.'],
            'URL-адреса не схожа на реальний URL каналу. Будь-ласка, перевірте правильність URL та повторіть спробу.',
        ]
    }
}
