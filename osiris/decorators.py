from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse

from .utils import get_API, get_API_version


def osirisapi(fn):
    """
    Insert API to Osiris in the function keywords as kw['api']

    :param fn:
    :return:
    """
    def wrapper(*args, **kw):
        university_code = kw.pop('uni', None)
        if university_code is None:
            return JsonResponse({'error': 'invalid unicode'}, status=400)
        api = get_API(university_code)
        if api is None:
            return JsonResponse({'error': 'invalid unicode'}, status=400)
        kw['api'] = api
        return fn(*args, **kw)

    return wrapper

def v2api(fn):
    """
    validates if V2 api is enabled for this uni

    needs to be inner call before osirisapi since depends on unicode
    :param fn:
    :return:
    """
    def wrapper(*args, **kw):
        university_code = kw.get('uni', None)
        if university_code is None:
            return JsonResponse({'error': 'invalid unicode'}, status=400)
        if get_API_version(university_code) < 2:
            return JsonResponse({'error': 'api V2 endpoint not available for this unicode'})
        return fn(*args, **kw)

    return wrapper