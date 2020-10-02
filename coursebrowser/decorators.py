import threading

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.shortcuts import render

from studyguide.utils import get_path_key
from osiris.utils import get_API_version


class renderThread(threading.Thread):
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def run(self):
        request = self.args[0]
        page = request.path
        channel_layer = get_channel_layer()
        unicode = request.session.get('unicode', 'tue')
        groupname = get_path_key(page, unicode)
        response = self.fn(*self.args, **self.kwargs)
        cache.set(groupname, response.content)
        async_to_sync(channel_layer.group_send)(groupname, {"type": 'update', 'text': 'DONE'})


def render_async_and_cache(fn):
    def wrapper(*args, **kw):
        request = args[0]
        page = request.path
        unicode = request.session.get('unicode', 'tue')
        groupname = get_path_key(page, unicode)
        html = cache.get(groupname)
        if html is None:
            # check if outcome is valid
            kw2 = dict(kw)
            kw2['fullrender'] = False
            if not fn(*args, **kw2):
                raise Http404()
            if get_API_version(unicode) == 2:
                response = fn(*args, **kw)
                cache.set(groupname, response.content)
                return response
            renderThread(fn, args, kw).start()
            cache.set(groupname, "rendering", 10 * 60)
            return render(request, 'waiting.html', {'channel': groupname})
        elif html == 'rendering':
            return render(request, 'waiting.html', {'channel': groupname})
        else:
            return HttpResponse(html, None, None)

    return wrapper
