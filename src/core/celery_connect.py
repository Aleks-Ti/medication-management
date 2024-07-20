from celery import Celery

from src.core.config import redis_conf

celery = Celery("tasks", broker=redis_conf.build_connection_str())
