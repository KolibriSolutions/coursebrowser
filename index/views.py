from django.shortcuts import render
from osiristue.decorators import superuser_required
from django.core.cache import cache

def index(request):
    return render(request, 'index.html')

@superuser_required()
def clearcache(request):
    cache.clear()
    return render(request, 'base.html', {
        'Message' : 'Cache cleared!'
    })