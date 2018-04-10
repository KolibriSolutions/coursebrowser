from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseForbidden
from .util import getConfig, getAPi

def osirisapi(fn):
    def wrapper(*args, **kw):
        unicode = kw.pop('uni', None)
        if unicode is None:
            return HttpResponseBadRequest()
        api = getAPi(unicode)
        if api is None:
            return HttpResponseNotFound()
        kw['api'] = api
        return fn(*args, **kw)

    return wrapper