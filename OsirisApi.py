import json
import requests

class OsirisApi:
    BASEURL = "https://master.ele.tue.nl/osiris/api/"

    def __init__(self):
        self.session = requests.session()
        try:
            with open('osiris/proxies.json', 'r') as stream:
                self.proxies = json.loads(stream.readlines()[0].strip('\n'))
        except:
            self.proxies = {}
        self.session.headers['User-Agent'] = 'Osiris TUe Unofficial Interface'
        self.session.headers['From'] = 'mastermarketplace@tue.nl'


    def types(self):
        r = self.session.get(self.BASEURL + 'types/')
        if r.status_code != 200:
            return
        return json.loads(r.text)

    def faculties(self):
        r = self.session.get(self.BASEURL + 'faculties/')
        if r.status_code != 200:
            return
        return json.loads(r.text)

    def course(self, coursecode):
        r = self.session.get(self.BASEURL + 'course/' + coursecode + '/')
        if r.status_code != 200:
            return
        return json.loads(r.text)

    def facultyCoursesType(self, faculty, type):
        r = self.session.get(self.BASEURL + 'faculty/courses/{}/{}/'.format(faculty, type))
        if r.status_code != 200:
            return
        return json.loads(r.text)

    def facultyCoursesLevel(self, faculty, level):
        r = self.session.get(self.BASEURL + 'faculty/courses/{}/level/{}/'.format(faculty, level))
        if r.status_code != 200:
            return
        return json.loads(r.text)