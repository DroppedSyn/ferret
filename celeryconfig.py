from datetime import timedelta
BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672'
CELERY_RESULT_BACKEND = 'db+postgresql://rann@/rann'
CELERYBEAT_SCHEDULE = {
#        'fetch-direct-messages-every-2min': {
#            'task': 'tasks.fetchdms',
#            'schedule': timedelta(minutes=2)
#            },

	'refresh-followers-db-every-2min': {
	    'task': 'tasks.refresh_followers',
	    'schedule': timedelta(minutes=2)
	    },
#        'check-if-follows-every2min': {
#            'task': 'tasks.check_if_follows',
#            'schedule': timedelta(minutes=2)
#            },
        }
CELERY_TIMEZONE = 'UTC'
