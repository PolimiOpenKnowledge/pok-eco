import json
import logging
from celery.task import task
from instructor.offline_gradecalc import offline_grade_calculation
from courseware.courses import get_course_by_id
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore
# TODO: add a better task management to prevent concurrent task execution with some course_id

log = logging.getLogger('edx.celery.task')


@task()
def offline_calc(course_id):
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    offline_grade_calculation(course_key)


def _generate_course_structure(course_key):
    """
    Generates a course structure dictionary for the specified course.
    """
    try:
        course = get_course_by_id(course_key)
    except Http404:
        log.error("course with %s not found", course_key.to_deprecated_string())
        return

    end_date = course.end_datetime_text()
    course = modulestore().get_course(course_key, depth=None)
    blocks_stack = [course]
    blocks_dict = {}
    while blocks_stack:
        curr_block = blocks_stack.pop()
        children = curr_block.get_children() if curr_block.has_children else []
        key = unicode(curr_block.scope_ids.usage_id)
        block = {
            "id": key,
            "type": curr_block.category,
            "completedTimestamp": str(end_date)
            # "children": [unicode(child.scope_ids.usage_id) for child in children]
        }

        # Retrieve these attributes separately so that we can fail gracefully if the block doesn't have the attribute.
        #attrs = (('end_date', None), ('format', None), ("completedTimestamp", None), ("relativeCompletion", None))
        #for attr, default in attrs:
        #    if hasattr(curr_block, attr):
        #        block[attr] = getattr(curr_block, attr, default)
        #    else:
        #        log.warning('Failed to retrieve %s attribute of block %s. Defaulting to %s.', attr, key, default)
        #        block[attr] = default

        blocks_dict[key] = block

        # Add this blocks children to the stack so that we can traverse them as well.
        blocks_stack.extend(children)
    return {
        "moocId": "oaiprefixTODO"+course_key.to_deprecated_string(),
        "tasks": blocks_dict.values()
    }


@task(name=u'ecoapi.tasks.update_course_structure')
def update_course_structure(course_key):
    """
    Regenerates and updates the course structure (in the database) for the specified course.
    """
    # Import here to avoid circular import.
    from .models import CourseStructureCache

    # Ideally we'd like to accept a CourseLocator; however, CourseLocator is not JSON-serializable (by default) so
    # Celery's delayed tasks fail to start. For this reason, callers should pass the course key as a Unicode string.
    if not isinstance(course_key, basestring):
        raise ValueError('course_key must be a string. {} is not acceptable.'.format(type(course_key)))

    course_key = CourseKey.from_string(course_key)

    try:
        structure = _generate_course_structure(course_key)
    except Exception as ex:
        log.exception('An error occurred while generating course structure: %s', ex.message)
        raise

    structure_json = json.dumps(structure)

    cs, created = CourseStructureCache.objects.get_or_create(
        course_id=course_key,
        defaults={'structure_json': structure_json}
    )

    if not created:
        cs.structure_json = structure_json
        cs.save()
