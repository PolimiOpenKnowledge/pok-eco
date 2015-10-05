import abc


class BasePattern(object):
    """
    Abstract class for matching pattern and translation
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, **options):
        self.base_url = options.get('BASE_URL', '')
        self.homepage_url = options.get('HOMEPAGE_URL', '')
        self.oai_prefix = options.get('OAI_PREFIX', '')

    @abc.abstractmethod
    def match(self, evt, course_id):
        pass

    @abc.abstractmethod
    def convert(self, evt, course_id):
        pass

    def fix_id(self, base_url, obj_id):
        if not obj_id.startswith("https"):
            return base_url + obj_id
        return obj_id
