from urllib.request import urlopen

from bs4 import BeautifulSoup
from django.shortcuts import render
import sounddevice as sd
import speech_recognition as sr
import wavio
from googlesearch import search
from nltk.corpus import stopwords
from nltk import sent_tokenize
from nltk import word_tokenize
import threading

topic_list = []


def voice_recorder_HomePage(request):
    return render(request, 'voice.html')


def start_recording(request):
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = int(request.GET['Duration'])
    language = request.GET['language']
    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    wavio.write("myrecording.wav", recording, freq, sampwidth=2)

    # speech_recognition
    spoken_text = speech_recognition(language)

    # words_list = get_searched_words_and_sentence(spoken_text)
    #
    # links_list = []
    #
    # for i in words_list:
    #     links = list(search(i, tld="com", num=10, stop=10, pause=3))
    #     links_list += links
    # print(words_list)
    # return render(request, 'test.html', {'spoken_text': spoken_text, 'links': links_list})
    return get_links_from_google(spoken_text, request)


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


def get_links_from_google(spoken_text, request):
    words_list = get_searched_words_and_sentence(spoken_text)
    words_list += topic_list
    links_list = []

    for i in words_list:
        links = list(search(i, tld="com", num=10, stop=5, pause=3))
        links_list += links
    print(words_list)
    print(read_text_of_website(links_list))
    return render(request, 'test.html', {'spoken_text': spoken_text, 'links': links_list})


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
    most_common_wordlist = []
    temp_test = clean_stopwords(spoken_text)

    for i in temp_test:
        temp = temp_test.count(i)
        if temp >= 2 and i not in punctuations:
            most_common_wordlist.append(i)
    most_common_wordlist = list(set(most_common_wordlist))

    sentence_list = sent_tokenize(spoken_text)

    return most_common_wordlist + sentence_list


def addTopic(request):
    topic_list.append(request.GET['topic'])

    return render(request, 'voice.html')

# Implement a for loop and pass a list containing the
# string tags script and style into the Beautiful Soup object as the sequence.
# with  bs4.BeautifulSoup.decompose().
# Pass the bs4.BeautifulSoup.stripped_strings
# generator into list(generator) to return a list of the remaining
# string text in the html object.


def read_text_of_website(url_list):

    url='https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/testing.html'

    soup = BeautifulSoup(urlopen(url).read())

    for script in soup(["script", "style"]):

        script.decompose()

    return ' '.join(list(soup.stripped_strings))
