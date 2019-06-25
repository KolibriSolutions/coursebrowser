import yaml
from django.core.cache import cache

from osiris.OsirisAPI import OsirisAPI


def get_config():
    config = cache.get('osirisconfig')
    if config is None:
        with open('osiris/osirisconfig.yaml', 'r') as stream:
            config = yaml.load(stream)
        cache.set('osirisconfig', config, 48 * 60 * 60)
    return config


def get_API(university_code):
    config = get_config()
    if university_code not in config:
        return
    if not config[university_code]['active']:
        return
    api = cache.get('apiobj_' + university_code)
    if api is None:
        api = OsirisAPI(config[university_code]['link'], university_code, types=config[university_code]['types'])
        cache.set('apiobj_' + university_code, api, 24 * 60 * 60)
    return api
