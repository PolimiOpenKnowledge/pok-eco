from celery.task import task
from django.conf import settings
from xapi.sender import TinCanSender


@task
def send_2_tin_can():
    options = settings.TRACKING_BACKENDS['xapi']['OPTIONS']
    if options.get("SEND_CRON_ENABLED"):
        TinCanSender.send_2_tincan_by_settings()
