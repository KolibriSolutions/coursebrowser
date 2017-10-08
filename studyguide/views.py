from django.shortcuts import render
from OsirisApi import OsirisApi
from osiristue.decorators import render_async_and_cache
import urllib.parse
from math import floor
import channels

def getCourses(courses, path):
    if type(courses) != list:
        return []
    API = OsirisApi()
    coursesinfo = []
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
            channels.Group('render_page_{}'.format(path)).send({'text' : str(floor(((i + 1) / len(courses)) * 100))})

    return coursesinfo

def chooseFaculty(request):
    API = OsirisApi()
    return render(request, 'choosefaculty.html', {
        'faculties' : API.faculties()
    })

@render_async_and_cache
def listBC(request, faculty):
    API = OsirisApi()
    return render(request, 'listBC.html', {
        'faculty' : urllib.parse.unquote(faculty),
        'type' : 'Bachelor College',
        'courses' : getCourses(API.facultyCoursesType(faculty, 'BC'), request.path.replace('/','_'))
    })

@render_async_and_cache
def listGS(request, faculty):
    API = OsirisApi()
    return render(request, 'listGS.html', {
        'faculty' : urllib.parse.unquote(faculty),
        'type' : 'Graduate School',
        'courses' : getCourses(API.facultyCoursesType(faculty, 'GS'), request.path.replace('/','_'))
    })