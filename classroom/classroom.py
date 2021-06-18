from __future__ import print_function
import pickle
import os.path
from google.auth.credentials import AnonymousCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime as dTime
import datetime

# If modifying these scopes, delete the file token.pickle.
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly','https://www.googleapis.com/auth/classroom.announcements',
'https://www.googleapis.com/auth/devstorage.read_only']


def normalize(s): #Quitar tildes y convertir a minusculas
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    s = s.lower()
    return s   

class Classroom:
    service = None
    cursos=[]
    def __init__(self):

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('classroom/credentials/token.pickle'):
            with open('classroom/credentials/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'classroom/credentials/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('classroom/credentials/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('classroom', 'v1', credentials=creds)

    def getCursos(self):
        coursesResponse = self.service.courses().list(pageSize=20).execute()
        courses = coursesResponse.get('courses', [])
        listaCursos=[]
        if not courses:
            listaCursos.append('No se encontraron cursos')
        else:
            for course in courses:
                #print(course['name']+' '+course['id'])        
                listaCursos.append({'nombre':course['name'],'link':course['alternateLink'],'id':course['id']})
                #print(course)
        self.cursos=listaCursos
        return listaCursos

    def buscarCurso(self,nombre=None,id=None):
        #Ver si ya se ha hecho esta consulta antes
        if not self.cursos:
            self.getCursos()

        resultado=None
        if nombre:
            nombre = normalize(nombre)
            for curso in self.cursos:
                if normalize(curso['nombre']).find(nombre) != -1:
                    resultado=curso
        elif id:
            for curso in self.cursos:
                if normalize(curso['id']) == id:
                    resultado=curso
                
        return resultado
    
    def anunciosCurso(self,cantidad,nombre=None,id_course=None):
        res=None
        curso=self.buscarCurso(nombre,id_course)
        if curso:
            id_course=curso['id']
        else:
            res = -1 # No se encontro el curso

        if id_course:
            anuncios = self.service.courses().announcements().list(courseId=id_course,pageSize=cantidad).execute() 
            res={'curso':curso['nombre'],'anuncios':-1}
            if anuncios:
                res['anuncios']=[]
                anuncios = anuncios['announcements'] 
                for a in anuncios:
                    fecha=dTime.strptime(a['updateTime'][2:10]+" "+ a['updateTime'][11:19],'%y-%m-%d %H:%M:%S')
                    fecha=fecha-datetime.timedelta(hours = 5)
                    res['anuncios'].append({'id':a['id'],'text':a['text'],'link':a['alternateLink'],"updateTime":fecha})
        return res

    def anunciosRecientes(self):
        #Ver si ya se ha hecho esta consulta antes
        if not self.cursos:
            self.getCursos()
        currentTime=datetime.datetime.now()
        resultado=[] #Anuncios con fechas de hace 3 dias
        for curso in self.cursos:
            anuncios = self.anunciosCurso(3,id_course=curso['id'])['anuncios']
            if anuncios!=-1:
                aRecientes=[]
                for anuncio in anuncios:
                    if anuncio['updateTime'] > (currentTime-datetime.timedelta(days=3)):
                        aRecientes.append(anuncio)
                if aRecientes:
                    resultado.append({'curso':curso['nombre'],'anuncios':aRecientes})

        return resultado


def main():
    ca=Classroom()
    an=ca.anunciosRecientes()
    for a in an:
        print(a['updateTime'])

if __name__=='__main__':
    main()