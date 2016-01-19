# -*- coding: utf-8 -*-
import json
from optparse import make_option

from django.core.management.base import BaseCommand
from tincan import Agent, Verb, Activity, Context
from xapi.models import TrackingLog


class Command(BaseCommand):
    help = 'Fix statement verb and object from string encoded to json'

    option_list = BaseCommand.option_list + (
        make_option(
            "-e",
            "--extract-event-number",
            dest="extract_event_number",
            help="Number of extract event"
        ),
    )

    def handle(self, *args, **options):
        # make sure file option is present
        if options['extract_event_number'] is None:
            extract_event_number = 100
        else:
            extract_event_number = int(options['extract_event_number'])

        evt_list = TrackingLog.objects \
                              .filter(tincan_error='WRONG_VERB_OBJECT') \
                              .order_by('dtcreated')[:extract_event_number]
        for evt in evt_list:
            statement_json = json.loads(evt.statement)
            statement = {
                'actor': Agent.from_json(json.dumps(statement_json['actor'])),
                'verb': Verb.from_json(json.dumps(statement_json['verb'])),
                'object': Activity.from_json(json.dumps(statement_json['object'])),
                'timestamp': statement_json['timestamp'],
                'context': Context.from_json(json.dumps(statement_json['context'])),
            }
            evt.statement = json.dumps(statement)
            evt.tincan_error = "CONVERTED"
            evt.save()
