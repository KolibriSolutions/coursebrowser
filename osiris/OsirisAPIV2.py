from aiohttp import ClientSession, TCPConnector
import pypeln as pl
from datetime import datetime
import requests


class OsirisAPIV2:
    def __init__(self, OsirisBaseLink, unicode, faculties, types):
        self.search_url = f"{OsirisBaseLink}/student/osiris/student/cursussen/zoeken"
        self.course_url = f"{OsirisBaseLink}/student/osiris/owc/cursussen/"
        now = datetime.now()
        if now.month <= 6:
            self.year = now.year - 1
        else:
            self.year = now.year
        self.unicode = unicode
        self.Types = types
        self.Faculties = faculties

        # internal mapping of course code to orisis code
        self._course_mapping = {}

    def _get_requests_session(self):
        session = requests.session()
        session.headers['User-Agent'] = 'Course Browser coursebrowser.nl by KolibriSolutions'
        session.headers['From'] = 'info@kolibrisolutions.nl'
        session.headers['taal'] = 'EN'
        return session

    def _get_faculty_long_name(self, faculty):
        return [f[1] for f in self.Faculties if f[0] == faculty][0]

    def _get_type_long_name(self, type):
        return [t[1] for t in self.Types if t[0] == type][0]

    def getCourseInfo(self, code, year=None):
        pass

    def getCourseHeader(self, code, year=None):
        pass

    def getCouseRequirements(self, code, year=None):
        pass

    def getCourses(self, faculty="EE", stage="GS", study=None, year=None):
        # study argument is not used, silently drop it

        if year is None:
            year = self.year

        session = self._get_requests_session()
        search_payload = {'from': 0,
                          'size': 2500, #in practise infinite
                          'sort': [{'cursus_korte_naam.raw': {'order': 'asc'}},
                                   {'cursus': {'order': 'asc'}},
                                   {'collegejaar': {'order': 'desc'}}],
                          'post_filter': {'bool': {'must': [{},
                                                            {'terms': {'collegejaar': [year]}},
                                                            {'terms': {'faculteit_naam': [self._get_faculty_long_name(faculty)]}},
                                                            {'nested': {'path': 'blokken_nested',
                                                                        'query': {'bool': {'must': [{}]}}}}]}},
                          'query': {'bool': {'must': []}}}
        r = session.post(self.search_url, json=search_payload)
        if r.status_code != 200:
            return None
        data = r.json()
        # extract coursecode plus internal osiris code for all in result set
        type_long = self._get_type_long_name(stage)
        all_courses = [(x['_source']['cursus'], x['_source']['id_cursus']) for x in data['hits']['hits']
                       if x['_source']['cursustype_omschrijving'] == type_long]
        # this is needed for later so save it for later
        for course in all_courses:
            self._course_mapping[course[0]] = course[1]
        # only return the coursecodes
        return sorted([x[0] for x in all_courses])
