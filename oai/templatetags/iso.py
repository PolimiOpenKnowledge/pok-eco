# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import make_naive, UTC

REGISTER = template.Library()


@REGISTER.filter(is_safe=True)
@REGISTER.simple_tag(name="tisoformat")
def tisoformat(date):
    return mark_safe(make_naive(date, UTC()).replace(microsecond=0).isoformat()+'Z')
