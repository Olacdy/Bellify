release: django-admin migrate --noinput
web: gunicorn bellify.wsgi:application
beat: celery -A bellify beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --max-interval 300
dj: celery -A bellify worker -l INFO -Q periodic_tasks
dj2: celery -A bellify worker -l INFO -Q telegram_events
