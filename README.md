# pok-eco

[![Build Status](https://travis-ci.org/marcore/pok-eco.svg?branch=master)](https://travis-ci.org/marcore/pok-eco)

POK-ECO add required integration between POK and ECO portal
In this repository you find different Django application used for this integration:

  - **oai** : Add an oai-pmh endpoint to edx to allow ECO to harvest some course information.
    At this development phase, the oai application run also in a standalone django project without
    any edx dependency . The course information and metadata are added with django admin to allow:
    - define which courses need to be harvested
    - define some specific metadata involved in ECO portal
    - use some relation information about the courses and the teachers (see also ecoapi)
  - **ecoapi** :  This app add a REST endpoint to allow ECO to get additional data like:
    - user enrollments and progress
    - teacher bio   (Teacher is a new model that this app add)
    - heartbeat for the integration
    This app has edx dependencies so it works only as an INSTALLED_APPS inside edx-platform
  - **xapi** :  This app add a Tracking backend (see ["Edx Track app"](https://github.com/edx/edx-platform/tree/master/common/djangoapps/track)) that translate edx events to a Tin Capi (xAPI) statements and push them to a LRS.Currently not all edx events are translated
    This app has edx dependencies so it works only as an INSTALLED_APPS inside edx-platform
    Moreover to use the xapi backend you need to add an additional TRACKING_BACKENDS configuration like this ("logger" is standard for edx, "xapi" is the additional part):

    ```python
    "TRACKING_BACKENDS": {
      "logger": {
        "ENGINE": "track.backends.logger.LoggerBackend",
        "OPTIONS": {
          "name": "tracking"
        }
      },
      "xapi": {
        "ENGINE": "xapi.xapi_tracker.XapiBackend",
        "OPTIONS": {
                "name": "xapi",
                "ID_COURSES": [],  # list of course_id you want to track on LRS
                "USERNAME_LRS": "",  # username for the LRS endpoint
                "PASSWORD_LRS": "",  # password for the LRS endpoint
                "URL": "http://mylrs.endpoint/xAPI/statements",  # the LRS endpoint API URL
                "HOMEPAGE_URL": "",  # homepage url for user profile (third party auth)
                "BASE_URL": "",  # base url for lms platform
                'OAI_PREFIX': '',  # the oai prefix course (eg oai:it.polimi.pok:)
                "EXTRACTED_EVENT_NUMBER": 100  # number of batch statements to extract from db and sent in a job
        }
      }
    }
    ```
    and an additional EVENT_TRACKING_BACKENDS configuration like this
    ("logger" is standard for edx, "xapi" is the additional part):

    ```python
    "EVENT_TRACKING_BACKENDS": {
        "logger": {
            "ENGINE": "eventtracking.backends.logger.LoggerBackend",
            "OPTIONS": {
                "name": "tracking",
                "max_event_size": 50000,
            }
        },
    		"xapi": {
                		"ENGINE": "xapi.xapi_tracker.XapiBackend",
                		"OPTIONS": {
                      "name": "xapi",
                      "ID_COURSES": [],  # list of course_id you want to track on LRS
                      "USERNAME_LRS": "",  # username for the LRS endpoint
                      "PASSWORD_LRS": "",  # password for the LRS endpoint
                      "URL": "http://mylrs.endpoint/xAPI/statements",  # the LRS endpoint API URL
                      "EXTRACTED_EVENT_NUMBER": 100  # number of batch statements to extract from db and     sent in a job
                		}
    		}
    }
    ```
    This backend add a translated event on a db table, then you need to add a cron job that extract
    this statements (max EXTRACTED_EVENT_NUMBER each time) and push them to LRS endpoint using the
    django command `send_data_2_tincan` .

## How to install

### Install the package
In the edxapp venvs run:

```bash
pip install git+https://github.com/marcore/pok-eco.git#egg=pok_eco
```

### Register the application

Add the application to `INSTALLED_APPS` setting :

```python
INSTALLED_APPS = (
    ...
    'oai',
    'ecoapi',
    'xapi'
)
```

### URLs entries

Add URLs entries:

```python
urlpatterns = patterns('',
    ...
    url(r'', include('oai.urls')),
    url(r'^ecoapi/', include('ecoapi.urls')),
    ...
)
```
