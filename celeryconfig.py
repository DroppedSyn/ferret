from datetime import timedelta
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'db+postgresql://ritesh@/ritesh'
CELERYBEAT_SCHEDULE = {
        'fetch-dms-every-min': {
            'task': 'tasks.fetchdms',
            'schedule': timedelta(minutes=1)
            },
        }
CELERY_TIMEZONE = 'UTC'
