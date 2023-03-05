release: django-admin migrate --noinput
web: gunicorn bellify.wsgi:application
beat: celery -A bellify beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --max-interval 300
worker: celery multi show 2 -A bellify -c=2 -l info -Q:1 telegram_events -Q:2 periodic_tasks
