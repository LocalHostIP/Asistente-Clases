#from codecs import encode
import os
import io
from google.cloud import speech_v1 as speech
import pyaudio
import scipy.io.wavfile as wav
import wave

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'demoServiceAccount.json'

WAVE_OUTPUT_FILENAME = "out.wav"

client = speech.SpeechClient()

#WAVE_OUTPUT_FILENAME = "pruebaLuis.wav"

def record_audio():
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	RECORD_SECONDS = 3

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

	print("* recording")

	frames = [stream.read(CHUNK) for i in range(0, int(RATE / CHUNK * RECORD_SECONDS))]

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

def predictAudio():
	with io.open(WAVE_OUTPUT_FILENAME,'rb') as audio_file:
		content = audio_file.read()
		audio=speech.types.RecognitionAudio(content=content)


	config = speech.RecognitionConfig(
		encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
		sample_rate_hertz=16000,
		language_code = 'es-MX',
		enable_word_time_offsets=True)

	response=client.recognize(config=config,audio=audio)

	return response

def grabar():
	record_audio()
	print('prediciendo')
	return predictAudio()