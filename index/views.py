from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render, redirect

from osiris.utils import get_config


def index(request):
    return render(request, 'index/index.html')


# @superuser_required()
def clearcache(request):
    cache.clear()
    return render(request, 'base.html', {
        'Message': 'Cache cleared!'
    })


def choose_university(request, university_code=None):
    """
    Choose a university and store it in session if university code is None
    Otherwise store a chosen university (by university code) in session

    :param request:
    :param university_code:  if not none, save the selected university in session.
    :return:
    """
    config = get_config()
    if university_code is None:
        universities = cache.get('universities_list')
        if not universities:
            universities = []
            for key, value in config.items():
                if value['active']:
                    universities.append((key, value['name']))
        return render(request, 'studyguide/choose_university.html', {'codes': universities})
    if university_code not in config:
        return Http404()
    # store chosen university in session
    request.session['unicode'] = university_code
    request.session['uniname'] = config[university_code]['name']
    return redirect("studyguide:choose_department")
