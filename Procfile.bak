release: django-admin migrate --noinput
web: gunicorn bellify.wsgi:application
beat: celery -A bellify beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --max-interval 300
worker: celery -A bellify worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
