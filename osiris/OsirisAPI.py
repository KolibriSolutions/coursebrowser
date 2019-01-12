from bs4 import BeautifulSoup
import requests
import urllib.parse
import json
import re
from datetime import datetime
from osiris.tasks import task_scrape_codes_per_study
from celery import group
import itertools

class OsirisAPI:
    # OsirisBaseLink = "https://osiris.tue.nl/osiris_student_tueprd/"

    # Types = (
    #     ('BC', "Bachelor College"),
    #     ('GS', "Graduate School")
    # )
    #
    # Types_dict = {
    #     'Graduate School' : 'GS',
    #     'Bachelor College' : 'BC',
    # }

    Languages_dict = {
        'Engels' : 'EN',
        'Nederlands' : 'NL',
    }

    # Faculties = (
    #     ("BMT", "Biomedical Engineering"),
    #     ("B", "the Built Environment"),
    #     ("EE", "Electrical Engineering"),
    #     ("ID", "Industrial Design"),
    #     ("IE&IS", "Industrial Engineering & Innovation Sciences"),
    #     ("ST", "Chemical Engineering and Chemistry"),
    #     ("TN", "Applied Physics"),
    #     ("W", "Mechanical Engineering"),
    #     ("W&I", "Mathematics and Computer Science")
    # )

    def __init__(self, OsirisBaseLink, unicode, faculties=None, types=None):
        now = datetime.now()
        if now.month <= 6:
            self.year = now.year - 1
        else:
            self.year = now.year
        self.unicode = unicode
        self.CatalogusLinkBase = OsirisBaseLink + "OnderwijsCatalogusSelect.do?selectie=cursus&collegejaar={year}"
        self.CatalogusCourse = self.CatalogusLinkBase + "&cursus={code}"
        self.CatalogusListCourses = self.CatalogusLinkBase + "&faculteit={faculty}&cursustype={stage}"
        self.CatalogusListCoursesStudy = self.CatalogusListCourses + "&organisatieonderdeel={study}"
        self.CatalogusListCoursesLevel = self.CatalogusListCourses + "&categorie={level}"
        self.CatalogusNextLink = OsirisBaseLink + "OnderwijsCatalogusKiesCursus.do?event=goto&source=OnderwijsZoekCursus&value={index}&partialTargets=OnderwijsZoekCursus"
        self.SearchLink = OsirisBaseLink + "/OnderwijsCatalogusZoekCursus.do"

        try:
            with open('osiris/proxies.json', 'r') as stream:
                self.proxies = json.loads(stream.readlines()[0].strip('\n'))
        except:
            self.proxies = {}
        self.initSession()
        self.coursereg = re.compile(r'\b[0-9]\w{3}[0-9]\b')
        self.dictreg = re.compile(r'({[^{}]+})')

        if faculties is None:
            self.Faculties = self._extractFaculties()
        else:
            self.Faculties = faculties

        self.Studies = self._extractStudies()

        if types is None:
            self.Types = self._extractTypes()
        else:
            self.Types = types
        self.Types_dict = {}
        for t in self.Types:
            self.Types_dict[t[1]] = t[0]

    def initSession(self):
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Course Browser coursebrowser.nl by KolibriSolutions'
        self.session.headers['From'] = 'info@kolibrisolutions.nl'


    def _scraperesultpages(self, soupinitial):
        codes = set()
        for page in soupinitial.find_all('option'):
            r = self.session.get(self.CatalogusNextLink.format(index=page['value']),
                                 proxies=self.proxies, timeout=5)
            if r.status_code != 200:
                return None
            souppage = BeautifulSoup(r.text, 'lxml')
            cells = souppage.find_all('a', class_='psbLink')
            for cell in cells:
                codes.add(cell.text)
        return codes


    def _extractTypes(self):
        r = self.session.get(self.SearchLink, proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        options = []
        for optionsoup in soup.find('select', {'name': 'cursustype'}).find_all('option'):
            options.append((optionsoup['value'], optionsoup.text))

        return options

    def _extractFaculties(self):
        r = self.session.get(self.SearchLink, proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        options = []
        for optionsoup in soup.find('select', {'name': 'faculteit'}).find_all('option'):
            if 'geen voorkeur' in optionsoup.text.lower():
                continue
            options.append((optionsoup['value'], optionsoup.text))

        return options

    def _extractStudies(self):
        r = self.session.get(self.SearchLink, proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        options = []
        for optionsoup in soup.find('select', {'name': 'organisatieonderdeel'}).find_all('option'):
            if 'geen voorkeur' in optionsoup.text.lower():
                continue
            options.append((optionsoup['value'], optionsoup.text))

        return options

    def getTypesStats(self):
        options = self._extractTypes()
        link = self.CatalogusLinkBase + "&cursustype={}"
        types = {}
        # if len(soupinitial.find_all('option')) > 0:
        #     codes = self._scraperesultpages(soupinitial)
        for type in options:
            r = self.session.get(link.format(type[0]))
            if r.status_code != 200:
                return
            intialsoup = BeautifulSoup(r.text, 'lxml')
            courses = self._scraperesultpages(intialsoup)
            types[str(type)] = len(courses)
        return types


    def _extractCourseCodesFromResponse(self, html, code):
        lr = []
        #extract all words that are in the right format, remove duplicates
        l = list(set(self.coursereg.findall(html)))
        try:
            l.remove(code)
        except:
            pass
        #drop all codes that are only numbers
        for code in l:
            try:
                int(code)
                continue
            except:
                lr.append(code)
        return lr

    def _extractCourseInfoFromSoup(self, soup):
        #TODO: this doesnt work anymore due to changes in osiris, endpoint is temporarly disabled for now
        goalbase = soup.find('span', id='cursDoel').find('td', class_='psbTekst')
        for elem in goalbase.findAll(['script', 'style']):
            elem.extract()
        try:
            goals = goalbase.find('div').text
        except:
            goals = goalbase.text
        contentbase = soup.find('span', id='cursInhoud').find('td', class_='psbTekst')
        for elem in contentbase.findAll(['script', 'style']):
            elem.extract()
        try:
            content = contentbase.find('div').text
        except:
            content = contentbase.text

        try:
            preknowledge = soup.find('span', id='cursVoorkennis').find('td', class_='psbTekst').text
        except:
            preknowledge = '-'
        # try:
        # entrylinks = soup.find('span', id='OnderwijsCursusIngangseisen').find_all('a')
        # codetext = list(set(self.dictreg.findall(entrytable.text)))
        # entrydemands = [json.loads(t)['cursuscode'] for t in codetext]
        try:
            entrydemands = [t.text for t in soup.find('span', id='OnderwijsCursusIngangseisen').find_all('a')]
        except:
            entrydemands = []
        # except:
        #     entrydemands = []

        return {
            'goals' : goals.replace('\n', ''),
            'content' : content.replace('\n', ''),
            'prekownloedge' : preknowledge.replace('\n', ''),
            'entrydemands' : entrydemands
        }

    def _extractCourseHeaderFromSoup(self, soup, code, year):
        #some elements are not onliners so are prepared here, onlines are put directly in the dictionary
        #same goes for elements that are prone to faillure due to the universities not being consistent with data
        try:
            responsiblestaffname = soup.find('tr', id='cursContactpersoon').find('a').text
        except:
            try:
                responsiblestaffname = soup.find('tr', id='cursContactpersoon').find(class_='psbTekst').text
            except:
                try:
                    responsiblestaffname = soup.find('tr', id='cursContactpersoon').text
                except:
                    responsiblestaffname = "multiple"

        try:
            quartiles = []
            quartiles_raw = [soup.find('tr', id='cursAanvangsblok').find('span', class_='psbTekst').text]
            if soup.find('tr', id='cursAanvangsblok').find('a'):
                quartiles_raw.append(soup.find('tr', id='cursAanvangsblok').find('a').text)
            for q in quartiles_raw:
                try:
                    q = int(q)
                except ValueError:
                    try:
                        q = int(q[-1])
                    except:
                        pass
                quartiles.append(q)

        except:
            quartiles = ['X']

        try:
            timeslots = list(soup.find('tr', id='cursTimeslot').find('td', class_='psbTekst').text.split(':')[0])
        except:
            timeslots = ['X']

        for t in timeslots:
            try:
                int(t)
            except ValueError:
                continue
            timeslots.remove(t)

        course = {
            'code' : code,
            'name' : soup.find('span', class_='psbGroteTekst').text,

            'responsiblestaff' : {
                'name' : responsiblestaffname,
            },
            'ECTS' : soup.find('tr', id='cursStudiepunten').find('span', class_='psbTekst').text.replace(',', '.'),
            'language' : soup.find('tr', id='cursVoertaal').find('span', class_='psbTekst').text,
            'detaillink' : self.CatalogusCourse.format(code=code, year=year),
            'preknowledge' : self._extractCourseCodesFromResponse(str(soup), code)
        }


        try:
            course['type'] = self.Types_dict.get(soup.find('tr', id='cursCursustype').find('span', class_='psbTekst').text, '-')
        except:
            course['type'] = '-'

        try:
            course['ECTS'] = float(course['ECTS'])
        except:
            pass

        try:
            course['owner'] = {
                'faculty' : soup.find('span', id='cursFaculteit').text.strip().strip(';'),
                'group' : soup.find('span', id='cursCoordinerendOnderdeel').text.replace(';', '').replace('Group', '').strip()
            }
        except:
            pass
        try:
            course['responsiblestaff']['email'] = soup.find('tr', id='medeEMailAdres').find('a').text
        except:
            pass
        # if course['type'] == 'BC':
        #     try:
        try:
            course['level'] = soup.find('tr', id='cursCategorie').find('span', class_='psbTekst').text[0]
        except:
            course['level'] = '-'
        try:
            course['level'] = int(course['level'])
        except:
            pass
        courses = []
        for timeslot in timeslots:
            for quartile in quartiles:
                c = course.copy()
                c['timeslot'] = timeslot
                c['quartile'] = quartile
                courses.append(c)

        return courses

    def getCourseInfo(self, code, year=None):
        if year is None:
            year = self.year
        code = urllib.parse.quote_plus(code)
        r = self.session.get(self.CatalogusCourse.format(code=code, year=year), proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soup.title).lower():
            return None

        return self._extractCourseInfoFromSoup(soup)

    def getCourseHeader(self, code, year=None):
        if year is None:
            year = self.year
        code = urllib.parse.quote_plus(code)
        r = self.session.get(self.CatalogusCourse.format(code=code, year=year), proxies=self.proxies, timeout=20) #increased timeout because it is called in heavy paralel fashion which may block the request longer
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soup.title).lower():
            return None

        if len(soup.find_all('table', class_='OraTableContent')) == 1:
            results = []
            for tr in soup.find('table', class_='OraTableContent').find_all('tr'):
                try:
                    block = tr.find_all('td')[7]
                    slot = tr.find_all('td')[8]
                    r2 = self.session.get(self.CatalogusCourse.format(code=code) +
                                          '&timeslot=' + slot.find('span').text.split(',')[0] +
                                          '&aanvangsblok=' + block.find('span').text,
                                          proxies=self.proxies, timeout=5)
                except:
                    continue
                if r2.status_code != 200:
                    return None
                soup2 = BeautifulSoup(r2.text, 'lxml')
                if 'fout' in str(soup2.title).lower():
                    return None
                results += self._extractCourseHeaderFromSoup(soup2, code, year)
            return results
        else:

            return self._extractCourseHeaderFromSoup(soup, code, year)

    def getCouseRequirements(self, code, year=None):
        if year is None:
            year = self.year
        code = urllib.parse.quote_plus(code)
        r = self.session.get(self.CatalogusCourse.format(code=code, year=year), proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        return self._extractCourseCodesFromResponse(r.text, code)

    def getCourses(self, faculty="EE", stage="GS", study=None, year=None):
        if year is None:
            year = self.year
        faculty = urllib.parse.quote_plus(faculty)
        stage = urllib.parse.quote_plus(stage)
        if study is None:
            r = self.session.get(self.CatalogusListCourses.format(faculty=faculty, stage=stage, year=year),
                                proxies=self.proxies, timeout=5)
        else:
            r = self.session.get(self.CatalogusListCoursesStudy.format(faculty=faculty, stage=stage, study=study, year=year),
                                 proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        soupinitial = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soupinitial.title).lower():
            return None
        codes = set()
        if len(soupinitial.find_all('span', class_='psbToonTekstRood')) == 1: #query has too much results
            job = group([task_scrape_codes_per_study.s(self, faculty, stage, x[0]) for x in self.Studies])
            result = job.apply_async()
            result.join()
            data = [x for x in result.get() if x is not None]
            codes = list(itertools.chain.from_iterable(data))
        else:
            if len(soupinitial.find_all('option')) > 0:
                codes = self._scraperesultpages(soupinitial)
            else:
                cells = soupinitial.find_all('a', class_='psbLink')
                for cell in cells:
                    codes.add(cell.text)

        return list(codes)

    def getCoursesLevel(self, faculty="EE", level=3, year=None):
        if year is None:
            year = self.year
        codes = set()
        faculty = urllib.parse.quote_plus(faculty)
        stage = "BC"
        r = self.session.get(self.CatalogusListCoursesLevel.format(faculty=faculty, stage=stage, level=level, year=year),
                             proxies=self.proxies, timeout=5)
        if r.status_code != 200:
            return None
        soupinitial = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soupinitial.title).lower():
            return None

        if len(soupinitial.find_all('option')) > 0:
            for page in soupinitial.find_all('option'):
                r = self.session.get(self.CatalogusNextLink.format(index=page['value']),
                                     proxies=self.proxies, timeout=5)
                if r.status_code != 200:
                    return None
                souppage = BeautifulSoup(r.text, 'lxml')
                cells = souppage.find_all('a', class_='psbLink')
                for cell in cells:
                    codes.add(cell.text)
        else:
            cells = soupinitial.find_all('a', class_='psbLink')
            for cell in cells:
                codes.add(cell.text)

        return list(codes)