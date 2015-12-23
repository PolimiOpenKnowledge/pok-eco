# -*- coding: utf-8 -*-
import gzip
import json
from optparse import make_option
import dateutil.parser

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
        if options['filename'] is None:
            raise CommandError("Option `--file=...` must be specified.")

        # Open the file, parse it and store the data, if not already present
        filename = options['filename']
        if filename.split('.')[-1] == 'gz':
            raw_data = gzip.open(filename, 'rb').read()
        else:
            raw_data = open(filename).read()
        lines = [l.strip() for l in raw_data.split('\n') if l.strip() != '']

        x = XapiBackend()

        process_data(x, lines)


def process_data(x, lines):
    i = 0
    for row in lines:
        event = json.loads(row)
        try:
            dt = dateutil.parser.parse(event['time'])
        except ValueError:
            print 'Data error -> ', event['time']
            continue

        # event['context']['user_id'] = 6 # used only for local test, comment in the real environment
        user_id = event['context'].get('user_id')
        if user_id == '':
            continue

        # Search for events of same user in the same date (seconds precision)
        tls = TrackingLog.objects.filter(dtcreated=dt, user_id=user_id)
        if tls:
            differentMillis = True
            for t in tls:
                t_event = json.loads(t.statement)
                if t_event['timestamp'] == event['time']:
                    differentMillis = False
                    break
            if differentMillis:
                i = i + 1
                event['time'] = dt
                x.send(event)
            else:
                # Skip duplicate events
                # print "Tracking event already exists for dt: %s and user_id : %s ", event['time'], user_id
                # print event
                pass

        else:
            i = i + 1
            event['time'] = dt
            x.send(event)

    print "%s events sent to backend", str(i)
