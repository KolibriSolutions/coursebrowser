from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from django.core.cache import cache
from .util import getConfig, getAPi
from .decorators import osirisapi

def index(request):
    return render(request, 'osiris/index.html')

def unicodes(request):
    config = getConfig()
    codesdict = {}
    for key, value in config.items():
        if value['active']:
            codesdict[key] = value['name']

    return JsonResponse(codesdict)

@osirisapi
def getCourse(request, code, api=None, http=True):
    if api is None:
        return Http404()

    info = cache.get('osiris_{}_course_{}'.format(api.unicode, code))
    if info is None:
        info = api.getCourseInfo(code)
        if info is None:
            cache.set('osiris_{}_course_{}'.format(api.unicode, code), [], 24 * 60 * 60)
            raise Http404()
        cache.set('osiris_{}_course_{}'.format(api.unicode, code), info, 24*60*60)
    if not info:
        raise Http404()
    if http:
        return JsonResponse(info, safe=False)
    else:
        return info

@osirisapi
def getCoursesFromFaculty(request, faculty, type, api=None, http=True):
    if api is None:
        return Http404()

    if faculty not in [f[0] for f in api.Faculties] or type not in [t[0] for t in api.Types]:
        raise Http404()
    info = cache.get('osiris_{}_faculty_{}_{}'.format(api.unicode, faculty, type))
    if info is None:
        info = api.getCourses(faculty, type)
        if info is None:
            raise Http404
        cache.set('osiris_{}_faculty_{}_{}'.format(api.unicode, faculty, type), info, 24*60*60)

    if http:
        return JsonResponse(info, safe=False)
    else:
        return info

@osirisapi
def getFaculties(request, api=None, http=True):
    if api is None:
        return Http404()
    if http:
        return JsonResponse(api.Faculties, safe=False)
    else:
        return api.Faculties

@osirisapi
def getTypes(request, api=None, http=True):
    if api is None:
        return Http404()
    if http:
        return JsonResponse(api.Types, safe=False)
    else:
        return api.Types
