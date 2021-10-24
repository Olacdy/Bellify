release: python manage.py migrate
bot: python manage.py bot
web: waitress-serve --port=$PORT telegram_notification.wsgi:application; celery -A telegram_notification worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo; celery -A telegram_notification beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler