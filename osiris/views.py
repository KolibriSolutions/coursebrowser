import urllib.parse

from django.core.cache import cache
from django.http import JsonResponse, Http404
from django.shortcuts import render

from .decorators import osirisapi, v2api
from .utils import get_config, get_API_version


def index(request):
    return render(request, 'osiris/api.html')


def unicodes(request):
    config = get_config()
    codesdict = {}
    for key, value in config.items():
        if value['active']:
            codesdict[key] = {
                'name': value['name'],
                'apiversion': get_API_version(key)
            }

    return JsonResponse(codesdict)


### V1 endpoints

@osirisapi
def get_course_info(request, code, year, api=None, http=True):
    # TODO: scraping is not up to date so temporarily taking this endpoint down

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
def get_course_header(request, year, code, api=None, http=True):
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
def get_courses_from_faculty(request, year, department, type_shortname, api=None, http=True):
    department = urllib.parse.unquote_plus(department)
    if department not in [f[0] for f in api.Faculties] or type_shortname not in [t[0] for t in api.Types]:
        raise Http404('Invalid department')
    try:
        study = request.META.get('STUDY', None)
    except:
        study = None  # it is usually None.
    info = cache.get('osiris_{}_faculty_{}_{}_{}'.format(api.unicode, department, type_shortname, year))
    if info is None:
        info = api.getCourses(department, type_shortname, study, year=year)
        if info is None:
            raise Http404('No data returned from Osiris')
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
    if http:
        return JsonResponse(api.Types, safe=False)
    else:
        return api.Types


@osirisapi
def get_studies(request, api=None, http=True):
    if http:
        return JsonResponse(api.Studies, safe=False)
    else:
        return api.Studies


### V2 endpoints
@v2api
@osirisapi
def get_all_courses(request, year, api=None, http=True):
    info = cache.get(f'osiris_{api.unicode}_{year}_allcourses')
    if info is None:
        info = api.getAllCourses(year=year)
        if info is None:
            raise Http404()
        cache.set(f'osiris_{api.unicode}_{year}_allcourses', info)
    if http:
        return JsonResponse(info, safe=False)
    else:
        return info