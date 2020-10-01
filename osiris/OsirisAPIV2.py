from .AsyncFetcher import async_fetcher
from datetime import datetime
import requests
from general_utils import validate_course_code

class OsirisAPIV2:
    Version = 2
    request_headers = {
        'User-Agent': 'Course Browser coursebrowser.nl by KolibriSolutions',
        'From': 'info@kolibrisolutions.nl',
        'taal': 'NL'
    }

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
        self._retrieve_internal_mapping()

    ### Helper functions

    def _get_requests_session(self):
        session = requests.session()
        session.headers = self.request_headers
        return session

    def _get_faculty_long_name(self, faculty):
        return [f[1] for f in self.Faculties if f[0] == faculty][0]

    def _get_type_long_name(self, type):
        return [t[1] for t in self.Types if t[0] == type][0]

    def _retrieve_internal_mapping(self, year=None):
        if year is None:
            year = self.year
        search_payload = {'from': 0,
                          'size': 5000,  # in practise infinite
                          'sort': [{'cursus_korte_naam.raw': {'order': 'asc'}},
                                   {'cursus': {'order': 'asc'}},
                                   {'collegejaar': {'order': 'desc'}}],
                          'post_filter': {'bool': {'must': [{},
                                                            {'terms': {'collegejaar': [year]}},
                                                            {'nested': {'path': 'blokken_nested',
                                                                        'query': {'bool': {'must': [{}]}}}}]}},
                          'query': {'bool': {'must': []}}}
        session = self._get_requests_session()
        r = session.post(self.search_url, json=search_payload)
        if r.status_code != 200:
            return False
        data = r.json()
        all_courses = [(x['_source']['cursus'], x['_source']['id_cursus']) for x in data['hits']['hits']]
        self._course_mapping[year] = {}
        for course in all_courses:
            self._course_mapping[year][course[0]] = course[1]
        return True

    def _build_course_header(self, coursedict):
        courseitems = coursedict['items']

        velden = {}
        for rubriek in courseitems:
            for x in rubriek['velden']:
                if x.get('titel', ''):
                    titel = x['titel']
                else:
                    titel = x['veld']
                if titel not in velden:
                    velden[titel] = x.get('waarde', None)
                else:
                    velden[titel] += x.get('waarde', [])

        docent = [x for x in velden['Docent(en)'] \
                    if x['omschrijving'] == 'Verantwoordelijk docent']
        if len(docent) == 0:
            docent = velden['Docent(en)']

        course = {
            'code': velden['cursus'],
            'name': velden['cursus_lange_naam'],
            'responsiblestaff': {
                'name': docent[0]['velden'][0]['docent']
                # TODO: add email here
            },
            'ECTS': velden['Studiepunten (ECTS)'].split(' ')[0],
            'language': velden['Voertaal'],
            'detaillink': '#',
            'preknowledge': velden.get('Veronderstelde voorkennis'),
            'type': velden['Cursustype'],
            'owner': {
                'faculty': velden['Faculteit'],
                'group': velden['Coördinerend onderdeel']
            },
            'level': velden.get('Categorie', '-')
        }
        timeslots = []
        if 'Inschrijfperiodes' in velden:
            for x in velden['Inschrijfperiodes']:
                if 'velden' in x:
                   timeslots.append({
                       'quartile': x['omschrijving'],
                       'timeslot': [y['waarde'] for y in x['velden'] if y['titel'] == 'Timeslot(s)'][0]
                   })
        course['timeslot'] = timeslots
        course['quartile'] = list(set([x['quartile'] for x in timeslots]))

        return course

    def _get_internal_code(self, code, year):
        if not validate_course_code(code):
            return None
        if year not in self._course_mapping:
            self._retrieve_internal_mapping(year)
        else:
            # is this really necesarry?
            if code not in self._course_mapping[year]:
                self._retrieve_internal_mapping()
        if code not in self._course_mapping[year]:
            return None  # non existant code
        return str(self._course_mapping[year][code])

    ### External calls
    def getAllCourses(self, year=None):
        # V2 only
        if year is None:
            year = self.year
        if year not in self._course_mapping:
            self._retrieve_internal_mapping(year)
        return sorted([x for x in self._course_mapping[year].keys() if validate_course_code(x)])

    def getCourseInfo(self, code, year=None):
        # TODO: broken in V1, when enabled move to new V2 branch
        pass

    def getCourseHeader(self, code, year=None):
        # this is for retrieving a single course, given that its internal mapping code is present
        # for multiple courses use getCourseHeaderMultiple
        if year is None:
            year = self.year

        internal_code = self._get_internal_code(code.upper(), year)
        if internal_code is None:
            return None
        session = self._get_requests_session()
        r = session.get(self.course_url + internal_code)
        if r.status_code != 200:
            return None

        return self._build_course_header(r.json())

    def getCourseHeaderMultiple(self, codes, year=None):
        # V2 only
        if year is None:
            year = self.year
        # use asyncio to pull multiple courses

        # filter out invalid codes
        codes = [code.upper() for code in codes if self._get_internal_code(code.upper(), year) is not None]
        if len(codes) == 0:
            return []
        urls = []
        for code in codes:
            urls.append(self.course_url + self._get_internal_code(code, year))
        results = async_fetcher(urls, self.request_headers)

        results_dicts = []
        for result in results:
            # try:
            results_dicts.append(self._build_course_header(result))
            # except:
            # continue

        return sorted(results_dicts, key=lambda x: x['code'])

    def getCourses(self, faculty="EE", stage="GS", study=None, year=None):
        # study argument is not used, silently drop it

        if year is None:
            year = self.year

        session = self._get_requests_session()
        search_payload = {'from': 0,
                          'size': 2500,  # in practise infinite
                          'sort': [{'cursus_korte_naam.raw': {'order': 'asc'}},
                                   {'cursus': {'order': 'asc'}},
                                   {'collegejaar': {'order': 'desc'}}],
                          'post_filter': {'bool': {'must': [{},
                                                            {'terms': {'collegejaar': [year]}},
                                                            {'terms': {'faculteit_naam': [
                                                                self._get_faculty_long_name(faculty)]}},
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
        # only return the coursecodes
        return sorted([x[0] for x in all_courses])
