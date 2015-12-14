
import json
import requests

from django.conf import settings
from xapi.models import TrackingLog


class TinCanSender(object):

    @classmethod
    def send_2_tincan_by_settings(cls):
        options = settings.TRACKING_BACKENDS['xapi']['OPTIONS']
        cls.send_2_tincan(
            options['URL'],
            options['USERNAME_LRS'],
            options['PASSWORD_LRS'],
            options['EXTRACTED_EVENT_NUMBER'],
            10)

    @classmethod  # pylint: disable=too-many-arguments
    def send_2_tincan(cls, api_url, username_lrs, password_lrs, extract_event_number, timeout):
        headers = {
            "Content-Type": "application/json",
            "X-Experience-API-Version": "1.0.0"
        }
        auth = (username_lrs, password_lrs)

        evt_list = TrackingLog.objects \
                              .filter(exported=False) \
                              .filter(tincan_error='') \
                              .order_by('dtcreated')[:extract_event_number]
        for evt in evt_list:
            resp = requests.post(api_url, data=evt.statement, auth=auth, headers=headers, timeout=timeout)
            try:
                evt.tincan_key = ''
                answer = json.loads(resp.content)
                if answer['result'].lower() != 'ok':
                    evt.tincan_error = resp.content
                    # print answer # uncomment for debug
                else:
                    evt.tincan_key = resp.content
                    evt.exported = True
            except:  # pylint: disable=bare-except
                evt.tincan_error = resp.content
            evt.save()
