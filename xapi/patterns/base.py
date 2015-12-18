import abc
import re

USAGE_PATTERN_ID = r'(P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/]+)'
BLOCK_PATTERN_REGEX = USAGE_PATTERN_ID.replace('P<course_key_string>', r'block-v[\d]:')


class BasePattern(object):
    """
    Abstract class for matching pattern and translation
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def match(self, evt, course_id):
        pass

    @abc.abstractmethod
    def convert(self, evt, course_id):
        pass

    @property
    def base_url(self):
        return self.backend_setting('base_url', '')

    @property
    def oai_prefix(self):
        return self.backend_setting('oai_prefix', '')

    #  pylint: disable=attribute-defined-outside-init
    def backend_setting(self, setting_name, default=None):
        """ Get a setting, from XapiBackendConfig """
        if not hasattr(self, '_config'):
            from xapi.models import XapiBackendConfig
            self._config = XapiBackendConfig.current()
        if hasattr(self._config, str(setting_name)):
            return getattr(self._config, str(setting_name))
        else:
            raise KeyError

    # pylint: disable=no-self-use
    def fix_id(self, base_url, obj_id):
        if not obj_id.startswith("https"):
            return base_url + obj_id
        return obj_id

    def get_object_id(self, path):
        match = re.search(BLOCK_PATTERN_REGEX, path)
        if match:
            return match.group(0)
        else:
            return None  # self.fix_id(self.base_url, path)
