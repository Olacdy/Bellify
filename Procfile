release: django-admin migrate --noinput
web: gunicorn bellify.wsgi:application
beat: celery -A bellify beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --max-interval 300
worker: celery -A bellify worker -l info -Q periodic_tasks
worker: celery -A bellify worker -l info -Q telegram_events
