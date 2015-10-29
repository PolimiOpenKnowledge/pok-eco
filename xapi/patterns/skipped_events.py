import re

from xapi.patterns.base import BasePattern


# Skipped events for eco
class SkippedEventRule(BasePattern):
    def match(self, evt, course_id):
        event_type = evt['event_type']
        skipped_condition = (
            # #### VIDEO
            event_type == 'stop_video' or
            event_type == 'pause_video' or
            event_type == 'seek_video' or
            event_type == 'speed_change_video' or
            event_type == 'show_transcript' or
            event_type == 'hide_transcript' or
            re.search('transcript/translation/en', event_type) or

            # #### PAGE  NAVIGATION
            # re.search('progress', event_type) or
            re.search('goto_position', event_type) or
            event_type == 'page_close' or
            # re.search('role_plays', event_type) or
            # re.search('jump_to_id', event_type) or

            # #### Problem
            event_type == 'save_problem_success' or
            re.search('save_user_state', event_type) or
            re.search('problem_save', event_type) or
            re.search('input_ajax', event_type) or
            re.search('problem_check', event_type) or
            re.search('problem_show', event_type) or
            re.search('problem_reset', event_type) or
            re.search('problem_get', event_type) or
            re.search('reset_problem', event_type) or
            event_type == 'problem_graded' or
            event_type == 'showanswer' or

            # #### Peer assessment
            # re.search('render_submission', event_type) or
            # re.search('render_student_training', event_type) or
            # re.search('spazio_docenti', event_type) or
            # re.search('render_grade', event_type) or
            # re.search('render_leaderboard', event_type) or
            # re.search('render_self_assessment', event_type) or

            re.search('list_instructor_tasks', event_type) or
            re.search('instructor', event_type) or

            # #### GENERAL
            event_type == '/change_enrollment' or
            event_type == '/create_account' or
            event_type == '/accounts/login' or
            re.search('render_message', event_type)
            # re.match('^/courses/.*', event_type)
        )
        return skipped_condition

    def convert(self, evt, course_id):
        return None, None
