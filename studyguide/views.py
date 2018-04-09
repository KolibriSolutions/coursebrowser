from django.shortcuts import render
from OsirisApi import OsirisApi
from osiristue.decorators import render_async_and_cache
import urllib.parse
from math import floor
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from studyguide.util import get_path_key

def getCourses(courses, path):
    if type(courses) != list:
        return []
    API = OsirisApi()
    coursesinfo = []
    channel_layer = get_channel_layer()
    name = get_path_key(path)
    for i, course in enumerate(courses):
        info = API.course(course)
        if info is not None:
            for c in info:
                staff = c.pop('responsiblestaff')
                owner = c.pop('owner')
                c['teacher'] = staff['name']
                c['teachermail'] = staff['email']
                c['group'] = owner['group']
                coursesinfo.append(c)
            async_to_sync(channel_layer.group_send)(name, {"type": "update", "text" : str(floor(((i + 1) / len(courses)) * 100))})

    return coursesinfo

def chooseFaculty(request):
    API = OsirisApi()
    return render(request, 'choosefaculty.html', {
        'faculties' : API.faculties()
    })

@render_async_and_cache
def listBC(request, faculty):
    faculty = urllib.parse.unquote(faculty)
    API = OsirisApi()
    return render(request, 'listBC.html', {
        'faculty' : [f[1] for f in API.faculties() if faculty == f[0]][0],
        'type' : 'Bachelor College',
        'courses' : getCourses(API.facultyCoursesType(faculty, 'BC'), request.path)
    })

@render_async_and_cache
def listGS(request, faculty):
    faculty = urllib.parse.unquote(faculty)
    API = OsirisApi()
    return render(request, 'listGS.html', {
        'faculty' : [f[1] for f in API.faculties() if faculty == f[0]][0],
        'type' : 'Graduate School',
        'courses' : getCourses(API.facultyCoursesType(faculty, 'GS'), request.path)
    })

def coursetree(request, faculty, type):
    faculty = urllib.parse.unquote(faculty)
    API = OsirisApi()
    return render(request, 'treegraph.html', {
        'faculty' : faculty,
        'type' : type,
        'visjs' : API.facultyTree(faculty, type)
    })