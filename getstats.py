from osiris.OsirisAPI import OsirisAPI
import yaml

if __name__ == '__main__':
    with open('osiris/osirisconfig.yaml', 'r') as stream:
        config = yaml.load(stream)
    try:
        with open('statsresults.yaml', 'r') as stream:
            stats = yaml.load(stream)
    except:
        stats = {}
    for uni in config.values():
        if uni['code'] in stats:
            continue
        print("Scraping {}".format(uni['code']))
        api = OsirisAPI(uni['link'])
        stats[uni['code']] = api.getTypesStats()

        with open('statsresults.yaml', 'w') as stream:
            yaml.dump(stats, stream, default_flow_style=False)