from celery.decorators import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task(name="send_email")
def send_email(email, message):
    """
    sends email to the client
    """
    logger.info("sending email to - " + email + message)

    return True
