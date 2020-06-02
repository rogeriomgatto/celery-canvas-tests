import os

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost')

broker_url = REDIS_URL
broker_transport_options = {
    'fanout_prefix': True,
    'fanout_patterns': True,
    #'visibility_timeout': 3600,
}

result_backend = REDIS_URL
#result_extended = True

#task_track_started = True
#task_acks_late = True
#worker_prefetch_multiplier = 1
