from django.http import HttpResponseNotFound, HttpResponseBadRequest

from .utils import get_API


def osirisapi(fn):
    """
    Insert API to Osiris in the function keywords as kw['api']

    :param fn:
    :return:
    """
    def wrapper(*args, **kw):
        university_code = kw.pop('uni', None)
        if university_code is None:
            return HttpResponseBadRequest()
        api = get_API(university_code)
        if api is None:
            return HttpResponseNotFound()
        kw['api'] = api
        return fn(*args, **kw)

    return wrapper
