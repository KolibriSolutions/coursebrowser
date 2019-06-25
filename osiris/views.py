import urllib.parse

from django.core.cache import cache
from django.http import JsonResponse, Http404
from django.shortcuts import render

from .decorators import osirisapi
from .utils import get_config


def index(request):
    return render(request, 'osiris/index.html')


def unicodes(request):
    config = get_config()
    codesdict = {}
    for key, value in config.items():
        if value['active']:
            codesdict[key] = value['name']

    return JsonResponse(codesdict)


@osirisapi
def getCourseInfo(request, code, year, api=None, http=True):
    # TODO: scraping is not up to date so temporarily taking this endpoint down
    if api is None:
        return Http404()

    info = cache.get('osiris_{}_courseinfo_{}_{}'.format(api.unicode, code, year))
    if info is None:
        info = api.getCourseInfo(code, year=year)
        if info is None:
            cache.set('osiris_{}_courseinfo_{}_{}'.format(api.unicode, code, year), [])
            raise Http404()
        cache.set('osiris_{}_courseinfo_{}_{}'.format(api.unicode, code, year), info)
    if not info:
        raise Http404()
    if http:
        return JsonResponse(info, safe=False)
    else:
        return info


@osirisapi
def getCourseHeader(request, code, year, api=None, http=True):
    """
    Frontend view to get course information from Osiris API as JSON.
    Also used to get information for course list.

    :param request:
    :param code:
    :param year:
    :param api:
    :param http:
    :return:
    """
    if api is None:
        return Http404()

    info = cache.get('osiris_{}_courseheader_{}_{}'.format(api.unicode, code, year))
    if info is None:
        info = api.getCourseHeader(code, year=year)
        if info is None:
            cache.set('osiris_{}_courseheader_{}_{}'.format(api.unicode, code, year), [])
            raise Http404()
        cache.set('osiris_{}_courseheader_{}_{}'.format(api.unicode, code, year), info)
    if not info:
        raise Http404()
    if http:
        return JsonResponse(info, safe=False)
    else:
        return info


@osirisapi
def getCoursesFromFaculty(request, year, department, type_shortname, api=None, http=True):
    if api is None:
        return Http404()
    department = urllib.parse.unquote_plus(department)
    if department not in [f[0] for f in api.Faculties] or type_shortname not in [t[0] for t in api.Types]:
        raise Http404()
    try:
        study = request.META.get('STUDY', None)
    except:
        study = None
    info = cache.get('osiris_{}_faculty_{}_{}_{}'.format(api.unicode, department, type_shortname, year))
    if info is None:
        info = api.getCourses(department, type_shortname, study, year=year)
        if info is None:
            raise Http404
        cache.set('osiris_{}_faculty_{}_{}_{}'.format(api.unicode, department, type_shortname, year), info)

    if http:
        return JsonResponse(info, safe=False)
    else:
        return info


@osirisapi
def get_departments(request, api=None, http=True):
    """
    Get departments from Osiris using osirisAPI

    :param request:
    :param api: set by decorator
    :param http:
    :return:
    """
    if api is None:
        return Http404()
    if http:
        return JsonResponse(api.Faculties, safe=False)
    else:
        return api.Faculties


@osirisapi
def get_type_names(request, api=None, http=True):
    if api is None:
        return Http404()
    if http:
        return JsonResponse(api.Types, safe=False)
    else:
        return api.Types


@osirisapi
def getStudies(request, api=None, http=True):
    if api is None:
        return Http404()
    if http:
        return JsonResponse(api.Studies, safe=False)
    else:
        return api.Studies
