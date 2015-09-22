# -*- coding: utf-8 -*-

import json
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from xapi.models import TrackingLog
from xapi.xapi_tracker import XapiBackend


class Command(BaseCommand):
    help = 'Insert log data stored on the given file to the xapi log database, so they can be sent to TinCan'

    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest="filename",
            help="specify import file",
            metavar="FILE"
        ),
    )

    def handle(self, *args, **options):
        # make sure file option is present
        if options['filename'] == None:
            raise CommandError("Option `--file=...` must be specified.")

        # Open the file, parse it and store the data, if not already present
        filename = options['filename']
        raw_data = open(filename).read()
        lines = [l.strip() for l in raw_data.split('\n') if l.strip() != '']

        i = 1
        x = XapiBackend()
        for row in lines:
            event = json.loads(row)
            try:
                dt = datetime.datetime.strptime(event['time'].split('+')[0], '%Y-%m-%dT%H:%M:%S.%f')
                i = i + 1
            except ValueError:
                print 'Data error -> ',  event['time']
                continue

            # event['context']['user_id'] = 6 # used only for local test, comment in the real environment
            event['time'] = dt
            user_id = event['context']['user_id']
            if user_id == '':
                continue
            try:
                # t = TrackingLog.objects.get(dtcreated=dt) # used only for local test, comment in the real environment
                t = TrackingLog.objects.get(dtcreated=dt, user_id=user_id)  # pylint: disable=unused-variable
            except TrackingLog.DoesNotExist:
                x.send(event)
