from datetime import datetime

from django import template
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template.defaultfilters import truncatechars
from django.urls.base import reverse
from django.utils import timezone
from django.utils.html import format_html

register = template.Library()


@register.filter(name="index")
def index(List, i):
    return List[int(i)]


@register.simple_tag
def GetHash():
    try:
        with open("githash", "r") as stream:
            h = stream.readlines()[0].strip('\n')
        return h
    except:
        return "None"