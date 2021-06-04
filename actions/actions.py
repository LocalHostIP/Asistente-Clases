# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from classroom import classroom

ca=classroom.Classroom()

class Revisar(Action):
	global ca
	def name(self) -> Text:
		return "action_revisar"

	def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
	domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		tipo=None
		#Obtener la ultima entidad
		if(len(tracker.latest_message['entities'])>0): 
			tipo=tracker.latest_message['entities'][0]['value']

		#Si se encontro una entidad 
		if tipo!=None:
			#Si se estan buscando los cursos
			if tipo=='cursos':
				#Obtener nombre de los cursos
				cursos=ca.getCursosNombre()
				dispatcher.utter_message(text="Tus cursos son:")
				for curso in cursos:
					dispatcher.utter_message(text=curso['nombre']+'\n['+curso['link']+']')
			else:
				#No se encontro entidad
				dispatcher.utter_message(text="Ka?")	
		else:
			#No se encontro una entidad
			dispatcher.utter_message(text="Ka?")

		return []
