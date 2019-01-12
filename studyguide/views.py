from django.shortcuts import render
from coursebrowser.decorators import render_async_and_cache
import urllib.parse
from math import floor
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from studyguide.util import get_path_key
from osiris.views import getFaculties, getTypes, getCoursesFromFaculty
from osiris.util import getAPi
from celery import group
from osiris.tasks import task_get_course_header
from time import sleep
import itertools
from datetime import datetime

def getCourses(unicode, courses, path, year):
    if type(courses) != list:
        return []
    coursesinfo = []
    channel_layer = get_channel_layer()
    name = get_path_key(path, unicode)
    api = getAPi(unicode)

    job = group([task_get_course_header.s(api, course, year) for course in courses])
    result = job.apply_async()

    while not result.ready():
        async_to_sync(channel_layer.group_send)(name, {"type": "update", "text": str(floor(((result.completed_count() + 1) / len(courses)) * 100))})
        sleep(1)

    data = [x for x in result.get() if x is not None]
    data = list(itertools.chain.from_iterable(data))
    for c in data:
        staff = c.pop('responsiblestaff')
        try:
            owner = c.pop('owner')
            c['group'] = owner['group']
        except:
            c['group'] = '-'
        c['teacher'] = staff['name']
        try:
            c['teachermail'] = staff['email']
        except KeyError:
            c['teachermail'] = 'Unkown'
        coursesinfo.append(c)

    return coursesinfo

def chooseFaculty(request):
    now = datetime.now()
    if now.month <= 6:
        year = now.year - 1
    else:
        year = now.year
    unicode = request.session.get('unicode', 'tue')
    return render(request, 'choosefaculty.html', {
        'faculties' : getFaculties(request, uni=unicode, http=False),
        'types' : getTypes(request, uni=unicode, http=False),
        'year' : year
    })

@render_async_and_cache
def listCourses(request, faculty, type, year, fullrender=True):
    faculty = urllib.parse.unquote(faculty)
    unicode = request.session.get('unicode', 'tue')
    if not fullrender:
        api = getAPi(unicode)
        if faculty not in [f[0] for f in api.Faculties]:
            return False
        if type not in [t[0] for t in api.Types]:
            return False
        return True

    facultyname = [f[1] for f in getFaculties(request, uni=unicode, http=False) if faculty == f[0]][0]
    typename = [f[1] for f in getTypes(request, uni=unicode, http=False) if type == f[0]][0]

    return render(request, 'list.html', {
        'faculty' : facultyname,
        'type' : typename,
        'courses' : getCourses(unicode, getCoursesFromFaculty(request, year, faculty, type, uni=unicode, http=False), request.path, year),
    })