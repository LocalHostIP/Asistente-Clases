# Asistente-Clases
Asistente de clases con RASA y Google Classroom API

Interfaz gráifica mediante TkInter

Actuales capacidades del bot:
  - Revisar en que cursos está
  - Buscar curso
  - Speech to text de google cloud
  - Abrir links desde interfaz
  - Contar chistes
  - Mostrar anuncios recientes (3 dias)
  - Mostrar anuncios de una materia
  - Mostrar una cantidad deseada de anuncnios de una materia
  - Mostrar tareas sin hacer de todas las materias
  - Buscar un curso en especifico
  - Contar chistes
  - Mensaje de bienvenida 
  - Qué puedes hacer?
  - Revisar alumnos de un curso

Dependencias:
  - rasa
  - tkinter
  - pip install --upgrade google-cloud-speech
  - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
  - pip install rasa[spacy]
  - python -m spacy download es_core_news_md
  - pyaudio

## Colaboradores
- Miguel Angel Guerrero Padilla
- Lazaro Fabricio Torres Orozco
- Luis Humberto Márquez Álvarez

## Credenciales google cloud
Colocar el archivo de credenciales (credentials.json) de la API de Google Classroom en la carpeta credentials de la carpeta classroom

Colocar el archivo de credenciales de la API de Speech to Text de Google (demoServiceAccount.json) en la carpeta UI

