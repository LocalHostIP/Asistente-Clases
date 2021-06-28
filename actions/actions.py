# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from os import link
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from classroom import classroom

ca=classroom.Classroom()

class Revisar(Action):
	global ca
	def name(self) -> Text:
		return "action_revisar"

	def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
	domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		tipo = tracker.get_slot('tipo_revisar')
		
		#Si se encontro una entidad 
		if tipo!=None:
			#Si se estan buscando los cursos
			#---------------Cursos------------------------
			if tipo=='cursos':
				#Obtener nombre de los cursos
				cursos=ca.getCursos()
				dispatcher.utter_message(text="Tus cursos son:")
				for curso in cursos:
					dispatcher.utter_message(json_message={"link":curso['link'],"text":curso['nombre']})
			#---------------Anuncios----------------------
			elif tipo=='anuncios':
				resultado=ca.anunciosRecientes()
				if resultado:
					dispatcher.utter_message(text="Anuncios recientes:")
					for c in resultado:
						dispatcher.utter_message(text='Anuncios de '+c['curso']+":")
						for a in c['anuncios']:
							dispatcher.utter_message(json_message={"link":a['link'],"text":'('+str(a['updateTime'])[2:16]+')\n\n'+a['text']})

				else:
					dispatcher.utter_message(text="No tienes nuevos anuncios")
			# ---------------Tareas------------------------
			elif tipo == 'tareas':
				dispatcher.utter_message(text='Tus tareas son:\n')
				resultado = ca.tareasPendientes()
				hayTareas=False
				for r in resultado:
					tareas=r['tareas']
					if tareas and tareas!=-1: #Si no es una lista vacia o vale -1
						dispatcher.utter_message(text="Curso: "+r['curso'])
						for t in tareas:
							dispatcher.utter_message(json_message={"link":t['link'],"text":'('+str(t['updateTime'])[2:16]+')\n\n'+t['titulo']+"\n\n"+t['description']})
			else:
				#No se reconoce lo que se quiere revisar
				dispatcher.utter_message(text="No entendí que revisar")	
		else:
			#No se especifico que revisar
			dispatcher.utter_message(text="No indicaste que revisar")

		return []

class RevisarUnCurso(Action):
	global ca
	def name(self) -> Text:
		return "action_revisarUnCurso"

	def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
	domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		tipo = tracker.get_slot('tipo_revisarUno')
			
		#Si se encontro una entidad 
		if tipo!=None:
			#---------------Anuncios----------------------
			if tipo=='anuncios':
				curso = tracker.get_slot('curso')
				cantidad = tracker.get_slot('cantidad_revisar')
				if not curso: 
					#Preguntar si no se sabe el curso
					dispatcher.utter_message(text="¿Para cual curso?")
				else:
					c=3
					if cantidad:
						try:
							c = int(cantidad)
						except:
							pass
							
					resultado=ca.anunciosCurso(c,nombre=curso)

					if resultado==-1:
						dispatcher.utter_message(text='No se encontró el curso '+curso)				
					else:
						if resultado['anuncios']==-1:
							dispatcher.utter_message(text=resultado['curso']+' no tiene anuncios')
						else:
							dispatcher.utter_message(text='Anuncios de '+resultado['curso']+':')				
							for r in resultado['anuncios']:
								dispatcher.utter_message(json_message={"link":r['link'],"text":'('+str(r['updateTime'])[2:16]+')\n\n'+r['text']})
			#---------------Alumnos----------------------
			elif tipo == 'alumnos':
				curso = tracker.get_slot('curso')
				if not curso: 
					#Preguntar si no se sabe el curso
					dispatcher.utter_message(text="¿Para cual curso?")
				else:
					resultado=ca.alumnosCurso(nombre=curso)

					if resultado==-1:
						dispatcher.utter_message(text='No se encontró el curso '+curso)				
					else:
						if resultado['alumnos']==-1:
							dispatcher.utter_message(text=resultado['curso']+' no tiene alumnos inscritos')
						else:
							dispatcher.utter_message(text='Alumnos de '+resultado['curso']+':')				
							for r in resultado['alumnos']:
								dispatcher.utter_message(text=r['name']+'\n'+r['email'])

			else:
				#No se reconoce lo que se quiere revisar
				print(tipo)
				dispatcher.utter_message(text="No entendí que revisar")	
		
		else:
			#No se especifico que revisar
			dispatcher.utter_message(text="No indicaste que revisar")
		
		return [SlotSet('curso',None)]

class guardar_curso(Action):
	#Guardar el slot curso
	global ca
	def name(self) -> Text:
		return "action_guardar_curso"

	def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
	domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		text = tracker.latest_message['text']

		return [SlotSet('curso',text)]

class buscar_abrir(Action):
	global ca
	def name(self) -> Text:
		return "action_buscar_abrir"

	def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
	domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		curso = tracker.get_slot('curso')
		if not curso:
			dispatcher.utter_message(text="¿Para qué curso?")
		else:
			dispatcher.utter_message(text='Buscando '+curso+'...')
			resultado=ca.buscarCurso(curso)
			if resultado:
				dispatcher.utter_message(json_message={"link":resultado['link'],"text":resultado['nombre']})
			else:
				dispatcher.utter_message(text='No se encontró el curso '+curso)

		return [SlotSet('curso',None)]