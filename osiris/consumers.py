from channels.generic.websocket import AsyncWebsocketConsumer
from . import views
from .util import getConfig, getAPi
from django.http import Http404
import json

class ApiRespondCourse(AsyncWebsocketConsumer):
    async def connect(self):
        config = getConfig()
        self.unicode = self.scope['url_route']['kwargs']['unicode']
        if self.unicode in config:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        try:
            header = views.getCourseHeader(None, text_data, uni=self.unicode, http=False)
            info = views.getCourseInfo(None, text_data, uni=self.unicode, http=False)
        except Http404:
            await self.send(text_data='Invalid course code')
            return
        await self.send(text_data=json.dumps({
            'header' : header,
            'info' : info,
        }))

class ApiRespondFaculty(AsyncWebsocketConsumer):
    async def connect(self):
        config = getConfig()
        self.unicode = self.scope['url_route']['kwargs']['unicode']
        if self.unicode in config:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        try:
            faculty = text_data.split(':')[0]
            type = text_data.split(':')[1]
        except:
            await self.send(text_data='Invalid format, must be: "<faculty>:<type>')
            return

        api = getAPi(self.unicode)

        if faculty not in [f[0] for f in api.Faculties]:
            await self.send(text_data='invalid faculty, opitons are: ' + json.dumps([f[0] for f in api.Faculties]))
            return
        if type not in [f[0] for f in api.Types]:
            await self.send(text_data='invalid type, opitons are: ' + json.dumps([f[0] for f in api.Types]))
            return

        courses = views.getCoursesFromFaculty(None, faculty, type, uni=self.unicode, http=False)

        await self.send(text_data=json.dumps(courses))