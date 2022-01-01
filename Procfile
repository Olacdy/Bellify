release: django-admin migrate --noinput
web: gunicorn telegram_notification.wsgi:application
worker: celery -A telegram_notification worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
beat: celery -A telegram_notification beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
