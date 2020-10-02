import urllib.parse
import urllib.parse
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render, redirect

from coursebrowser.decorators import render_async_and_cache
from osiris.utils import get_API
from osiris.views import get_departments, get_type_names, get_courses_from_faculty
from .utils import get_course_info, get_path_key, prepare_courses_info_for_html


def choose_department(request):
    """
    After a university is selected, select a department within the university.

    :param request:
    :return:
    """
    now = datetime.now()
    if now.month <= 6:
        year = now.year - 1
    else:
        year = now.year
    university_code = request.session.get('unicode')
    if not university_code:
        return redirect("index:choose_university")
    return render(request, 'studyguide/choose_department.html', {
        'departments': get_departments(request, uni=university_code, http=False),
        'types': get_type_names(request, uni=university_code, http=False),
        'year': year
    })


@render_async_and_cache
def list_courses(request, department, type_shortname, year, fullrender=True):
    """
    List courses of selected university and department.

    :param request:
    :param department: department
    :param type_shortname: course type within department
    :param year:
    :param fullrender:
    :return:
    """
    department = urllib.parse.unquote(department)
    university_code = request.session.get('unicode')
    if not university_code:
        return redirect("index:choose_university")
    api = get_API(university_code)
    if not fullrender:
        if department not in [f[0] for f in api.Faculties]:
            return False
        if type_shortname not in [t[0] for t in api.Types]:
            return False
        return True

    department_name = [f[1] for f in get_departments(request, uni=university_code, http=False) if department == f[0]][0]
    type_name = [f[1] for f in get_type_names(request, uni=university_code, http=False) if type_shortname == f[0]][0]
    department_courses = get_courses_from_faculty(request, year, department, type_shortname, uni=university_code, http=False)
    if api.Version == 1: #legacy version
        channel_layer = get_channel_layer()
        name = get_path_key(request.path, university_code)

        async_to_sync(channel_layer.group_send)(name, {"type": "update", "text": 'Obtaining course information...'})
        courses = get_course_info(university_code, department_courses, request.path, year)

        return render(request, 'studyguide/list.html', {
            'department': department_name,
            'type': type_name,
            'courses': courses,
        })
    else:
        # new version
        courses = prepare_courses_info_for_html(api.getCourseHeaderMultiple(department_courses, year))
        return render(request, 'studyguide/list.html', {
            'department': department_name,
            'type': type_name,
            'courses': courses,
            'V2': True
        })