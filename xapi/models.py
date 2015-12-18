# pylint: disable=unused-import
from django.db import models
from xmodule_django.models import CourseKeyField
from config_models.models import ConfigurationModel


class TrackingLog(models.Model):
    """This model defines the fields that are stored in the tracking log database."""

    dtcreated = models.DateTimeField('creation date')
    user_id = models.IntegerField(blank=True)
    course_id = CourseKeyField(max_length=255, blank=True)
    original_event = models.TextField(blank=True)
    statement = models.TextField(blank=True)
    tincan_key = models.CharField(max_length=512, null=True, blank=True)
    tincan_error = models.TextField(blank=True, null=True, default='')
    exported = models.BooleanField(default=False)

    class Meta(object):
        app_label = 'xapi'
        db_table = 'xapi_trackinglog'

    def __unicode__(self):
        fmt = (
            u"[{self.dtcreated}] {self.user_id}@{self.course_id}: "
        )
        return fmt.format(self=self)  # pylint: disable=redundant-keyword-arg


class XapiBackendConfig(ConfigurationModel):

    id_courses = models.TextField(
        blank=True,
        help_text="A comma separated list of course_id you want to track on LRS",
        verbose_name="ID_COURSES")

    lrs_api_url = models.URLField(
        blank=True,
        verbose_name="LRS API URL",
        help_text="The LRS endpoint API URL"
    )

    username_lrs = models.TextField(
        blank=True,
        verbose_name="USERNAME_LRS",
        help_text="username for the LRS endpoint"
    )
    password_lrs = models.TextField(
        blank=True,
        verbose_name="USERNAME_LRS",
        help_text="password for the LRS endpoint"
    )
    oai_prefix = models.CharField(
        blank=True,
        max_length=100,
        verbose_name="OAI_PREFIX",
        help_text="the oai prefix course (eg oai:it.polimi.pok:)"
    )
    user_profile_home_url = models.URLField(
        blank=True,
        verbose_name="HOMEPAGE_URL",
        help_text="homepage url for user profile (third party auth)"
    )
    base_url = models.URLField(
        blank=True,
        verbose_name="BASE_URL",
        help_text="base url for lms platform"
    )

    extracted_event_number = models.IntegerField(
        default=50,
        verbose_name="EXTRACTED_EVENT_NUMBER",
        help_text=(
            'The maximum number of extracted event to send each iteration'
        )
    )
