from datetime import datetime

from core.broker.celery import celery_app


@celery_app.task(name="queue.test")
def test():
    print(datetime.now())
