from celery.utils.log import get_task_logger

from worker.worker import app as celery_app

logger = get_task_logger(__name__)


@celery_app.task
def hello2():
    logger.info("Cron 2")

    return True
