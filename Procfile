release: python manage.py migrate
web: waitress-serve --port=$PORT telegram_notification.wsgi:application
honcho: honcho -f ProcfileHoncho start 