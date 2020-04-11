from django.core.mail import send_mail
from celery.decorators import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task(name="send_welcome_email")
def send_welcome_email(email, name):
    """
    sends email to the client
    """
    logger.info("sending email to - " + email)

    return send_mail(
        "Welcome!",
        "Welcome to our side " + name,
        'sajal.4591@gmail.com',
        [email],
        fail_silently=False
    )
