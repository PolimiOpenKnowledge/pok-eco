# -*- coding: utf-8 -*-
from track import tracker


def merge(d1, d2):
    if isinstance(d1, dict) and isinstance(d2, dict):
        final = {}
        for k, v in d1.items()+d2.items():
            if k not in final:
                final[k] = v
            else:
                final[k] = merge(final[k], v)

                return final

    elif d2 is not None:
        return d2

    else:
        return d1


def log_event(event):
    """Capture a event by sending it to the register trackers"""
    tracker.send(event)


def server_track(request, event_type, event, page=None):  # pylint: disable=unused-argument
    """
    Log events related to server requests.
    Handle the situation where the request may be NULL, as may happen with management commands.
    """
    log_event(event)
