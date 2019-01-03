from osiris.OsirisAPI import OsirisAPI
from django.core.cache import cache
import yaml

def getConfig():
    config = cache.get('osirisconfig')
    if config is None:
        with open('osiris/osirisconfig.yaml', 'r') as stream:
            config = yaml.load(stream)
        cache.set('osirisconfig', config, 24*60*60)
    return config

def getAPi(code):
    config = getConfig()
    if code not in config:
        return
    if not config[code]['active']:
        return
    api = cache.get('apiobj_' + code)
    if api is None:
        api = OsirisAPI(config[code]['link'], code, types=config[code]['types'])
        cache.set('apiobj_' + code, api, 24*60*60)
    return api