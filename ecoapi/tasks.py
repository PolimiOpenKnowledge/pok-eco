from celery.task import task
from instructor.offline_gradecalc import offline_grade_calculation
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey
# TODO: add a better task management to prevent concurrent task execution with some course_id


@task()
def offline_calc(course_id):
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    offline_grade_calculation(course_key)
