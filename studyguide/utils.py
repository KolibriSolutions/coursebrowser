import itertools
from time import sleep
from urllib.parse import unquote_plus

from asgiref.sync import async_to_sync
from celery import group
from channels.layers import get_channel_layer
from math import floor

from osiris.tasks import task_get_course_header
from osiris.utils import get_API
from requests.exceptions import ReadTimeout
import copy


def get_path_key(path, unicode):
    path = unquote_plus(path)
    key = 'render_page_{}_{}'.format(unicode, path.split('?')[0].strip('/').replace('/', '_').replace('&', '_'))
    return key

def prepare_courses_info_for_html(data):
    courses_info = []
    for c in data:
        staff = c.pop('responsiblestaff')
        try:
            owner = c.pop('owner')
            c['group'] = owner['group']
        except KeyError:
            c['group'] = '-'
        c['teacher'] = staff['name']
        try:
            c['teachermail'] = staff['email']
        except KeyError:
            c['teachermail'] = 'Unkown'
        if len(c['timeslot']) == 0:
            c['quartile'] = 'Unknown'
            c['timeslot'] = 'Unknown'
            courses_info.append(c)
        elif len(c['timeslot']) == 1:
            c['quartile'] = c['timeslot'][0]['quartile']
            c['timeslot'] = c['timeslot'][0]['timeslot']
            courses_info.append(c)
        else:
            # convert multiple timeslot course to multiple courses
            for timeslot in c['timeslot']:
                c_c = copy.deepcopy(c)
                c_c['timeslot'] = timeslot['timeslot']
                c_c['quartile'] = timeslot['quartile']
                courses_info.append(c_c)

    return courses_info

def get_course_info(unicode, courses, path, year):
    if type(courses) != list:
        return []

    channel_layer = get_channel_layer()
    name = get_path_key(path, unicode)
    api = get_API(unicode)

    job = group([task_get_course_header.s(api, course, year) for course in courses])
    result = job.apply_async()

    while not result.ready():
        async_to_sync(channel_layer.group_send)(name, {"type": "update", "text": 'pb' + str(floor(((result.completed_count()) / len(courses)) * 100))})
        sleep(1)

    try:
        data = [x for x in result.get() if x is not None]
    except ReadTimeout as e:
        raise Exception("Not able to read Celery return data. Timeout: {}".format(e))
    data = list(itertools.chain.from_iterable(data))

    return prepare_courses_info_for_html(data)
