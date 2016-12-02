import datetime
from dateutil.parser import parse
import pytz
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


def get_request_for_user(user):
    """Create a request object for user."""
    request = RequestFactory()
    request.user = user
    request.COOKIES = {}
    request.META = {}
    request.is_secure = lambda: True
    request.get_host = lambda: "edx.org"
    request.method = 'GET'
    return request


def get_course_key(course_id):
    course_key = ""
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    return course_key

def get_course_title(course_id):
    course_key = get_course_key(course_id)
    title = CourseOverview.get_from_id(course_key).display_name
    return title


def get_course_description(course_id, user_id):
    course_key = get_course_key(course_id)
    description = CourseOverview.get_from_id(course_key).short_description
    return description


def get_usage_key(course_id, module_id):
    """
    Get the usage key of sequential block
    Can be :
        i4x://test/TEST101/sequential/45b889d710424143aa7f13e7c4bc0446
        or
        block-v1:ORG+TEST101+RUNCODE+type@sequential+block@45b889d710424143aa7f13e7c4bc0446
    depending on modulestore
    """
    course_key = CourseKey.from_string(course_id)
    items = modulestore().get_items(course_key, qualifiers={'name': module_id})
    return items[0].location.to_deprecated_string()


def make_datetime_for_tincan(timepart):
    if not isinstance(timepart, datetime.datetime):
        timepart = parse(timepart)  # datetime.datetime.strptime(timepart, "%Y-%m-%dT%H:%M:%S%f%z")

    if timepart.tzinfo:
        timestamp = timepart.replace(microsecond=0)
    else:
        timestamp = pytz.utc.localize(timepart).replace(microsecond=0)
    return timestamp
