from django.shortcuts import render, redirect
from osiriskolibri.decorators import superuser_required
from django.core.cache import cache
from osiris.util import getConfig
from django.http import Http404

def index(request):
    return render(request, 'index.html')

@superuser_required()
def clearcache(request):
    cache.clear()
    return render(request, 'base.html', {
        'Message' : 'Cache cleared!'
    })

def chooseuni(request, unicode=None):
    config = getConfig()
    if unicode is None:
        codeslst = []
        for key, value in config.items():
            if value['active']:
                codeslst.append((key, value['name']))
        return render(request, 'chooseuni.html', {'codes' : codeslst})
    if unicode not in config:
        return Http404()
    request.session['unicode'] = unicode
    request.session['uniname'] = config[unicode]['name']

    return redirect("studyguide:choosefaculty")