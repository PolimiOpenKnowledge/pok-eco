from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from courseware.courses import get_course_by_id, get_course_about_section

def get_course(course_id):
    course_key = ""
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_by_id(course_key)
    return course


def get_course_title(course_id):
    course = get_course(course_id)
    title = get_course_about_section(course, "title")
    return title
