# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from xapi.sender import TinCanSender


class Command(BaseCommand):
    help = 'Export log data to TinCan'

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        TinCanSender.send_2_tincan_by_settings()
        self.stdout.write('Data sent\n')
