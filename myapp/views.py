from django.shortcuts import render
import sounddevice as sd
import speech_recognition as sr
import wavio
import re
from googlesearch import search
from nltk.corpus import stopwords
from nltk import sent_tokenize
from nltk import word_tokenize


# Create your views here.


def voice_recorder_HomePage(request):
    return render(request, 'voice.html')


def voice_recorder(request):
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = int(request.GET['Duration'])
    language = request.GET['language']
    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq),
                       samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    wavio.write("myrecording.wav", recording, freq, sampwidth=2)

    # speech_recognition
    spoken_text = speech_recognition(language)

    words_list = get_searched_words_and_sentence(spoken_text)
    # words_list = (re.sub("[^\w]", " ", spoken_text).split())
    # words_list=filter_clean_text(spoken_text)
    # print(words_list)

    # sent_list=sent_tokenize(spoken_text)

    links_list = []

    for i in words_list:
        links = list(search(i, tld="com", num=10, stop=10, pause=3))
        links_list += links
    print(words_list)
    return render(request, 'test.html', {'spoken_text': spoken_text, 'links': links_list})


def speech_recognition(language):
    r = sr.Recognizer()
    myaudio = sr.AudioFile('myrecording.wav')
    with myaudio as source:
        audio = r.record(source)
    mytext = ''
    try:
        if (language == 'Deutsch'):
            mytext = r.recognize_google(audio, language='de-DE')
        elif ((language == 'English')):
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


# here to filter the text from stoped word that is not important like ..to..on ..for.. from ...... .
# function will return a list
def clean_stopwords(spoken_text):
    unwanted_words = set(stopwords.words("english") or stopwords.words("german"))
    wanted_words = []
    #     = [x for x in word_tokenize(spoken_text) if x not in unwanted_words]

    for word in word_tokenize(spoken_text):
        if word not in unwanted_words:
            wanted_words.append(word)

    return wanted_words


# will return List of the most commend words in the text and complete sentence from the text
def get_searched_words_and_sentence(spoken_text):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    most_commen_wordslist = []
    temp_test = clean_stopwords(spoken_text)

    for i in temp_test:
        temp = temp_test.count(i)
        if temp >= 2 and i not in punctuations:
            most_commen_wordslist.append(i)
    most_commen_wordslist = list(set(most_commen_wordslist))

    sentence_list = sent_tokenize(spoken_text)

    return most_commen_wordslist + sentence_list
