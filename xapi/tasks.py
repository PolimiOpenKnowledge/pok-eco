from celery.task import task
from django.conf import settings
from xapi.sender import TinCanSender


@task(name='xapi.send_2_tin_can')
def send_2_tin_can():
    # options = settings.TRACKING_BACKENDS['xapi']['OPTIONS']
    TinCanSender.send_2_tincan_by_settings()
