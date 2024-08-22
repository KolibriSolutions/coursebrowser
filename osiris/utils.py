import yaml
from django.core.cache import cache

# from osiris.old.OsirisAPI import OsirisAPI
from osiris.OsirisAPIV2 import OsirisAPIV2


def get_config():
    config = cache.get('osirisconfig')
    if config is None:
        with open('osiris/osirisconfig.yaml', 'r') as stream:
            config = yaml.safe_load(stream)
        cache.set('osirisconfig', config, 48 * 60 * 60)
    return config


def get_API_version(university_code):
    config = get_config()
    if university_code not in config:
        return -1
    if not config[university_code]['active']:
        return -1
    version = config[university_code].get('version', 1)
    return version


def get_API(university_code):
    config = get_config()
    if university_code not in config:
        return
    if not config[university_code]['active']:
        return
    version = config[university_code].get('version', 1)
    if version == 1:
        raise NotImplemented
        # api = cache.get('apiobj_' + university_code)
        # if api is None:
            # api = OsirisAPI(config[university_code]['link'], university_code, types=config[university_code]['types'])
            # cache.set('apiobj_' + university_code, api, 24 * 60 * 60)
    elif version == 2:
        api = cache.get('apiobj_' + university_code)
        if api is None:
            api = OsirisAPIV2(config[university_code]['link'], university_code,
                              config[university_code]['faculties'], config[university_code]['types'], config[university_code])
            cache.set('apiobj_' + university_code, api, 24 * 60 * 60)
    else:
        return

    return api
