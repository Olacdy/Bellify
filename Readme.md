# Project configuration

## .Env file

Insert values according to their name and description in the .env.example file

## Python enviroment and pipenv

Create pipenv enviroment with python 3.9, and install dependencies with:

`pipenv install`

## Local use

To start using locally, apply all migrations to database with:

`python manage.py migrate`

Then start the server with:

`python manage.py runserver`

Start bot in pooling mode:

`python manage.py bot_pooling`

To start celery, start Redis service and insert the URL into .env file, then start the beat for periodic tasks:

`celery -A bellify beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --max-interval 300`

Start worker to notify users:

`celery -A bellify worker -l INFO -Q periodic_tasks`

Add `--pool=solo` in the end if using Windows.

## Production

To run project in production, the server must have Dokku installed in it. All steps are similar to local use, except You dont need to run the commands.
Enviroment configuration is through Dokku's app enviroment.
