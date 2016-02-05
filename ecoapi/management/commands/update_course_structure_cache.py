# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from ecoapi.tasks import update_course_structure


class Command(BaseCommand):
    help = 'Update course json structure cached in db'

    option_list = BaseCommand.option_list + (
        make_option(
            "-c",
            "--course_id",
            dest="course_id",
            help="specify course_id"
        ),
    )

    def handle(self, *args, **options):
        # make sure file option is present
        if options['course_id'] is None:
            raise CommandError("Option `-c=...` must be specified.")

        # Open the file, parse it and store the data, if not already present
        course_id = options['course_id']
        update_course_structure(course_id)
