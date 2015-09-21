#-*- coding: utf-8 -*-

import requests, json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError


from django.conf import settings
from xapi.models import TrackingLog
from django.db.models import Q

class Command(BaseCommand):
    help = 'Export log data to TinCan'

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        options = settings.TRACKING_BACKENDS['xapi']['OPTIONS']
        headers = {
            "Content-Type":"application/json",
            "X-Experience-API-Version":"1.0.0"
        }
        auth = (options['USERNAME_LRS'], options['PASSWORD_LRS'])

        evt_list = TrackingLog.objects.filter(exported=False).filter(tincan_error='').order_by('dtcreated')[:options['EXTRACTED_EVENT_NUMBER']]
        for evt in evt_list:
            resp = requests.post(options['URL'], data=evt.statement, auth=auth, headers=headers)
            try:
                evt.tincan_key = ''
                answer = json.loads(resp.content)
                if answer['result'].lower() != 'ok':
                    evt.tincan_error = resp.content
                    #print answer # uncomment for debug
                else:
                    evt.tincan_key = resp.content
                    evt.exported = True
            except:
                evt.tincan_error = resp.content
            evt.save()
        self.stdout.write('Data sent\n')
