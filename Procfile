release: django-admin migrate --noinput
web: gunicorn bellify.wsgi:application
worker: celery -A bellify worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
beat: celery -A bellify beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
