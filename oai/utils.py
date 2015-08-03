# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.timezone import make_naive, UTC

OAI_ENDPOINT_NAME='oai'

class KeyValuePair(object):

    def __init__(self, key, val):
        self.key = key
        self.val = val


def to_kv_pairs(dct):
    for k in dct:
        yield KeyValuePair(k, dct[k])


def nstr(t):
    if t:
        return t
    return ''


def ndt(d):
    if d:
        return make_naive(d, UTC()).isoformat()
    return ''


class OaiRequestError(Exception):

    def __init__(self, code, reason):
        self.code = code
        self.reason = reason

    def __str__(self):
        return self.reason
