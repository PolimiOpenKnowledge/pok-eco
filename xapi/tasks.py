from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.conf import settings
from xapi.sender import TinCanSender


@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def send_2_tin_can():
    options = settings.TRACKING_BACKENDS['xapi']['OPTIONS']
    if options.get("SEND_CRON_ENABLED"):
        TinCanSender.send_2_tincan_by_settings()
