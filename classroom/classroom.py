from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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

    def getCursosNombre(self):
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
        return listaCursos

    def buscarCurso(self,nombre):
        cursos=self.getCursosNombre()
        resultado=None
        nombre = normalize(nombre)
        for curso in cursos:
            if normalize(curso['nombre']).find(nombre) != -1:
                resultado=curso
                
        return resultado
    
    def anuncios(self,nombre,cantidad):
        curso=self.buscarCurso(nombre)
        res=None
        if curso:
            id_course=curso['id']
            anuncios = self.service.courses().announcements().list(courseId=id_course,pageSize=cantidad).execute() 
            res={'curso':curso['nombre'],'anuncios':-1}
            if anuncios:
                res['anuncios']=[]
                anuncios = anuncios['announcements'] 
                for a in anuncios:
                    res['anuncios'].append({'id':a['id'],'text':a['text'],'link':a['alternateLink']})
        else:
            res = -1 # No se encontro el curso
        return res

def main():
    ca=Classroom()
    res=ca.anuncios('vision',10)
    if res:
        for r in res:
            print(r['text'])
    else:
        print('no hay anuncios')

if __name__=='__main__':
    main()