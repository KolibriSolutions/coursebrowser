from __future__ import absolute_import
from coursebrowser.celery import app
import requests
from bs4 import BeautifulSoup
from django.core.cache import cache
import logging
logger = logging.getLogger('django')
@app.task
def get_link(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        return None

@app.task
def task_scrape_codes_per_study(api, faculty, stage, study, year):
    api.initSession()
    codes = set()
    r = api.session.get(api.CatalogusListCoursesStudy.format(faculty=faculty, stage=stage, study=study, year=year),
                         proxies=api.proxies, timeout=api.TimeOut)
    soup = BeautifulSoup(r.text, 'lxml')
    if 'fout' in str(soup.title).lower():
        return None
    c = set()
    if len(soup.find_all('option')) > 0:
        codes = api._scraperesultpages(soup, year)
    else:
        cells = soup.find_all('a', class_='psbLink')
        for cell in cells:
            c.add(cell.text)
    return codes

@app.task
def task_get_course_header(api, course, year):
    info = cache.get('osiris_{}_courseheader_{}_{}'.format(api.unicode, course, year))

    if info is not None:
        return info
    api.initSession()
    tries = 1

    while True:
        info = api.getCourseHeader(course, year)
        if info is not None:
            break
        tries += 1
        if tries > 5:
            break
    cache.set('osiris_{}_courseheader_{}_{}'.format(api.unicode, course, year), info)

    return info
