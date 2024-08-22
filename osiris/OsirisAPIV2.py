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

    def __init__(self, OsirisBaseLink, unicode, faculties, types, config_raw):
        self.search_url = f"{OsirisBaseLink}/student/osiris/student/cursussen/zoeken"
        self.course_url = f"{OsirisBaseLink}/student/osiris/owc/cursussen/"
        now = datetime.now()
        if now.month <= 6:
            self.year = now.year - 1
        else:
            self.year = now.year
        self.year_long = '{}-{}'.format(self.year, self.year + 1)
        self.unicode = unicode
        self.Types = types
        self.Faculties = faculties
        self.config = config_raw
        # internal mapping of course code to orisis code
        self._course_mapping = {}
        self._retrieve_internal_mapping()

    ### Helper functions

    def _get_requests_session(self):
        session = requests.session()
        session.headers = self.request_headers
        return session

    # def _get_faculty_long_name(self,i faculty):
    #     return [f[1] for f in self.Faculties if f[0] == faculty][0]

    def _get_type_long_name(self, type):
        return [t[1] for t in self.Types if t[0] == type][0]

    def _retrieve_internal_mapping(self, year=None):
        if year is None:
            year = self.year
            year_long= self.year_long
        else:
            year=int(year)
            year_long = f'{year}-{year+1}'

        search_payload = {'from': 0,
                          'size': 5000,  # in practise infinite
                          'sort': [#{'cursus_korte_naam.raw': {'order': 'asc'}},
                                   {'cursus': {'order': 'asc'}},
                                   {'collegejaar': {'order': 'desc'}}],
                          'post_filter': {'bool': {'must': [{'terms': {'collegejaar': [year_long]}}]}},
                          }
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
        try:
            docent = docent[0]['velden'][0]['docent']
        except (KeyError, IndexError):
            docent = 'Unknown'

        course = {
            'code': velden['cursus'],
            'name': velden['cursus_lange_naam'],
            'responsiblestaff': {
                'name': docent
            },
            'ECTS': velden['Studiepunten (ECTS)'].split(' ')[0],
            'language': velden['Voertaal'],
            #'detaillink': '#',
            'preknowledge': velden.get('Veronderstelde voorkennis'),
            'type': velden['Cursustype'],
            'owner': {
                'faculty': velden['Faculteit'],
                'group': velden['Coördinerend onderdeel']
            },
            'level': velden.get('Categorie', '-')
        }
        if 'deeplink' in self.config:
            course['detaillink'] = self.config['deeplink'].format(code=course['code'], year=self.year)

        timeslots = []
        if 'Inschrijfperiodes' in velden:
            for x in velden['Inschrijfperiodes']:
                if 'velden' in x:
                   timeslots.append({
                       'quartile': x['omschrijving'],
                       'timeslot': [y['waarde'] for y in x['velden'] if y['titel'] == 'Timeslot(s)'][0]
                   })
                # elif 'blokken' in x:
                #     timeslots.append({
                #         'quartile': x['omschrijving'],
                #         'timeslot': '-'
                #     })
        course['timeslot'] = sorted(timeslots,
                                    key=lambda x: (x['quartile'], x['timeslot']))
        course['quartile'] = sorted(list(set([x['quartile'] for x in timeslots])))

        return course

    def _get_internal_code(self, code, year):
        if not validate_course_code(code):
            return None
        if year not in self._course_mapping:
            assert self._retrieve_internal_mapping(year)
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
        # filter out invalid codes
        # codes = [code.upper() for code in codes if self._get_internal_code(code.upper(), year) is not None]
        if len(codes) == 0:
            return []
        urls = []
        for (course_code, internal_code) in codes:
            urls.append(f'{self.course_url}{internal_code}')
        results = async_fetcher(urls, self.request_headers)

        results_dicts = []
        for result in results:
            # try:
            results_dicts.append(self._build_course_header(result))
            # except:
            # continue
        # return sorted(results_dicts, key=lambda x: x['code'])  # removed sorting
        return results_dicts

    def getCourses(self, faculty_long="Electrical Engineering", stage="GS", study=None, year=None):
        # study argument is not used, silently drop it

        if year is None:
            year = self.year_long
        else:
            year=int(year)
            year = f'{year}-{year+1}'

        session = self._get_requests_session()
        search_payload = {'from': 0,
                          'size': 2500,  # in practise infinite
                          'sort': [#{'cursus_korte_naam.raw': {'order': 'asc'}},
                                   {'cursus': {'order': 'asc'}},
                                   {'collegejaar': {'order': 'desc'}}],
                          'post_filter': {'bool': {'must': [{'terms': {'collegejaar': [year]}},
                                                            {'terms': {'faculteit_naam': [
                                                                faculty_long]}},
                                                            ]}},
                          }
        r = session.post(self.search_url, json=search_payload)
        if r.status_code != 200:
            return None
        data = r.json()
        # extract coursecode plus internal osiris code for all in result set
        type_long = self._get_type_long_name(stage)
        all_courses = [(x['_source']['cursus'], x['_source']['id_cursus']) for x in data['hits']['hits']
                       if x['_source']['cursustype_omschrijving'] == type_long]
        # only return the coursecodes
        # return sorted([x[0] for x in all_courses])

        # all_courses = [x['_source']['cursus'] for x in data['hits']['hits'] if x['_source']['cursustype_omschrijving'] == type_long]
        return all_courses
