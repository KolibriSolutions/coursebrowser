from django.shortcuts import render
from coursebrowser.decorators import render_async_and_cache
import urllib.parse
from math import floor
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from studyguide.util import get_path_key
from osiris.views import getCourseHeader, getFaculties, getTypes, getCoursesFromFaculty
from osiris.util import getAPi
from django.http import Http404

def getCourses(unicode, courses, path):
    if type(courses) != list:
        return []
    coursesinfo = []
    channel_layer = get_channel_layer()
    name = get_path_key(path, unicode)
    for i, course in enumerate(courses):
        tries = 1
        info = None
        while True:
            try:
                info = getCourseHeader(None, course, uni=unicode, http=False)
                break
            except Http404:
                print("Course {} retry fetching".format(course))
                tries += 1
            if tries > 3:
                break
        if info is not None:
            for c in info:
                staff = c.pop('responsiblestaff')
                try:
                    owner = c.pop('owner')
                    c['group'] = owner['group']
                except:
                    c['group'] = '-'
                c['teacher'] = staff['name']
                c['teachermail'] = staff['email']
                coursesinfo.append(c)
            async_to_sync(channel_layer.group_send)(name, {"type": "update", "text" : str(floor(((i + 1) / len(courses)) * 100))})
        else:
            continue

    return coursesinfo

def chooseFaculty(request):
    unicode = request.session.get('unicode', 'tue')
    return render(request, 'choosefaculty.html', {
        'faculties' : getFaculties(request, uni=unicode, http=False),
        'types' : getTypes(request, uni=unicode, http=False),
    })

@render_async_and_cache
def listCourses(request, faculty, type, fullrender=True):
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
        'courses' : getCourses(unicode, getCoursesFromFaculty(request, faculty, type, uni=unicode, http=False), request.path),
    })