from django.core.cache import cache
from django.http import HttpResponse
import threading
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from studyguide.util import get_path_key

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
        groupname = get_path_key(page)
        response = self.fn(*self.args, **self.kwargs)
        cache.set(groupname, response.content, 4*7*24*60*60)
        async_to_sync(channel_layer.group_send)(groupname, {"type" : 'update', 'text' : 'DONE'})


def render_async_and_cache(fn):
    def wrapper(*args, **kw):
        request = args[0]
        page = request.path

        try:
            if not request.user.is_anonymous:
                return fn(*args, **kw)
        except AttributeError:
            pass
        groupname = get_path_key(page)
        html = cache.get(groupname)
        if html is None:
            renderThread(fn, args, kw).start()
            cache.set(groupname, "rendering", 10*60)
            return render(request, 'waiting.html', {'channel' : groupname})
        elif html == 'rendering':
            return render(request, 'waiting.html', {'channel': groupname})
        else:
            return HttpResponse(html, None, None)

    return wrapper

def superuser_required():
    def is_superuser(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            else:
                raise PermissionDenied("Access Denied: for admins only.")
        return False

    return user_passes_test(
        is_superuser,
        login_url='/admin/',
        redirect_field_name='next',
    )

