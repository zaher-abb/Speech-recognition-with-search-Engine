from django.shortcuts import render
import sounddevice as sd
import speech_recognition as sr
import wavio
import re
from googlesearch import search


# Create your views here.


def voice_recorder_HomePage(request):
    return render(request, 'voice.html')


def voice_recorder(request):
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = int(request.GET['Duration'])

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq),
                       samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    wavio.write("myrecording.wav", recording, freq, sampwidth=2)

    spoken_text = speech_recognition()

    words_list = re.sub("[^\w]", " ", spoken_text).split()
    links_list = []
    for i in words_list:
        # temp_string += " " + "\n  " + i + " "
        links = list(search(i, tld="com", num=10, stop=10, pause=3))
        links_list += links

    return render(request, 'test.html', {'spoken_text': spoken_text, 'links': links_list})


def speech_recognition():
    r = sr.Recognizer()
    myaudio = sr.AudioFile('myrecording.wav')
    with myaudio as source:
        audio = r.record(source)
    mytext = ''
    try:
        mytext = r.recognize_google(audio)
    except Exception as exp:
        print(exp)

    return mytext

    # from googlesearch import search
    # query : anfrage String
    # tld :  Domain Suchen
    # num : anzahl von links
    # stop : anzahl wo programm aufhoert
    # pause : warten
def get_links_from_google(query):
    return search(query, tld="com", num=10, stop=10, pause=3)
