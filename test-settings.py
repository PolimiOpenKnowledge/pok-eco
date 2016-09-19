from settings import *
from path import path
from openedx.core.lib.tempdir import mkdtemp_clean
from django.conf import settings
from uuid import uuid4

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Add edx required
    'instructor_task',
    'enrollment',
    # ADD EDX-platform dependencies before test
    'xmodule_django',
    'track',
    'social.apps.django_app.default',
    'xblock_django',
    'student',

    # Real app of this package
    'ecoapi',
    'oai',
    'xapi'
)


# Copy from edx-platform
FEATURES = {}
ALL_LANGUAGES = (
    [u"en", u"English"],
    [u"it", u"Italian"],
)
XQUEUE_INTERFACE = {
        "basic_auth": [
            "edx",
            "edx"
        ],
        "django_auth": {
            "password": "password",
            "username": "lms"
        },
        "url": "http://localhost:18040"
}
TRACK_MAX_EVENT = 50000

COMMON_ROOT = os.environ.get("PYTHONENV", "") + "/edx-platform/common"
COMMON_TEST_DATA_ROOT = COMMON_ROOT + "/test/data"
TEST_ROOT = path("test_root")
print TEST_ROOT
MONGO_PORT_NUM = int(os.environ.get('MONGO_PORT_27017_TCP_PORT', '27017'))
MONGO_HOST = os.environ.get('MONGO_PORT_27017_TCP_ADDR', 'localhost')


THIS_UUID = uuid4().hex[:5]
DOC_STORE_CONFIG = {
    'host': MONGO_HOST,
    'db': 'test_xmodule',
    'collection': 'test_modulestore{0}'.format(THIS_UUID),
    'port': MONGO_PORT_NUM
    # If 'asset_collection' defined, it'll be used
    # as the collection name for asset metadata.
    # Otherwise, a default collection name will be used.
}
HOSTNAME_MODULESTORE_DEFAULT_MAPPINGS = {}
MODULESTORE_BRANCH = 'draft-preferred'
MODULESTORE = {
    'default': {
        'ENGINE': 'xmodule.modulestore.mixed.MixedModuleStore',
        'OPTIONS': {
            'mappings': {},
            'stores': [
                {
                    'NAME': 'split',
                    'ENGINE': 'xmodule.modulestore.split_mongo.split_draft.DraftVersioningModuleStore',
                    'DOC_STORE_CONFIG': DOC_STORE_CONFIG,
                    'OPTIONS': {
                        'default_class': 'xmodule.hidden_module.HiddenDescriptor',
                        'fs_root': TEST_ROOT / "data",
                        'render_template': 'edxmako.shortcuts.render_to_string',
                    }
                },
                {
                    'NAME': 'draft',
                    'ENGINE': 'xmodule.modulestore.mongo.DraftMongoModuleStore',
                    'DOC_STORE_CONFIG': DOC_STORE_CONFIG,
                    'OPTIONS': {
                        'default_class': 'xmodule.hidden_module.HiddenDescriptor',
                        'fs_root': TEST_ROOT / "data",
                        'render_template': 'edxmako.shortcuts.render_to_string',
                    }
                },
                {
                    'NAME': 'xml',
                    'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
                    'OPTIONS': {
                        'data_dir': mkdtemp_clean(dir=TEST_ROOT),  # never inadvertently load all the XML courses
                        'default_class': 'xmodule.hidden_module.HiddenDescriptor',
                    }
                }
            ]
        }
    }
}


CONTENTSTORE = {
    'ENGINE': 'xmodule.contentstore.mongo.MongoContentStore',
    'DOC_STORE_CONFIG': {
        'host': MONGO_HOST,
        'port': MONGO_PORT_NUM,
        'db': 'xcontent'
    }
}
