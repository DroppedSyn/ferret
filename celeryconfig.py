from datetime import timedelta
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'db+postgresql://ritesh@/ritesh'
CELERYBEAT_SCHEDULE = {
        'fetch-direct-messages-every-min': {
            'task': 'tasks.fetchdms',
            'schedule': timedelta(minutes=2)
            },
        }
CELERY_TIMEZONE = 'UTC'