from urllib import request
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

topic_list = []
static_links_list = []


def view_homePage(request):
    return render(request, 'voice.html')


# TODO : vesuchen die Aufnehmen zum teilen 10 min
def start_recording(request):
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = int(request.GET['Duration'])

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    wavio.write("myrecording.wav", recording, freq, sampwidth=2)

    # speech_recognition

    # return get_links_from_google(spoken_text, request)


def speech_recognition(language):
    r = sr.Recognizer()
    audio = sr.AudioFile('myrecording.wav')
    with audio as source:
        audio = r.record(source)
    text = ''
    try:
        if language == 'Deutsch':
            text = r.recognize_google(audio, language='de-DE')
        elif language == 'English':
            text = r.recognize_google(audio)
    except Exception as exp:
        print(exp)

    return text


# TODO : create static search links for rendering performance
def get_links_from_google(searched_text, request):
    # to  avoid a duplicated result from search
    # # words_list = list(set(searched_text))
    # print(words_list)
    searched_word = searched_text[-1]

    if topic_list.count(searched_word) == 1 :
        print(topic_list.count(searched_word))
        links = search(searched_word, tld="com", num=10, stop=5, pause=3)
        for i in links :
           static_links_list.append(i)
        return static_links_list
    else:
        return static_links_list


def fetch_topic_result(request):
    spoken_text = list(set(topic_list))
    links_list = get_links_from_google(spoken_text, request)
    list(links_list)
    return render(request, 'test.html', {'spoken_text': spoken_text, 'links': links_list})


# TODO: text muss noch ausgewertet mit haufigkeit
def fetch_voice_recorde_result(request):
    language = request.GET['language']
    start_recording(request)
    spoken_text = clean_stopwords(speech_recognition(language))

    links_list = get_links_from_google(spoken_text, request)
    return render(request, 'test2.html', {'spoken_text': spoken_text, 'links': links_list})


# here to filter the text from stopped word that is not important like ..to..on ..for.. from ...... .
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

# TODO: check if this methode still needed
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


# add topic to the Static list  " topic_list " and fetch result by rendering the page
def add_topic_and_fetch_topic_result(request):
    topic_list.append(request.GET['topic'])
    spoken_text = list(set(topic_list))
    links_list = get_links_from_google(topic_list, request)
  
    list(links_list)

    return render(request, 'voice.html', {'spoken_text': spoken_text, 'links': links_list})


# Implement a for loop and pass a list containing the string tags script and style into the Beautiful Soup object as the sequence. with  bs4.BeautifulSoup.decompose().
# Pass the bs4.BeautifulSoup.stripped_strings generator into list(generator) to return a list of the remaining string text in the html object.

def read_text_of_website(url):
    soup = BeautifulSoup(urlopen(url).read())
    for script in soup(["script", "style"]):
        script.decompose()

    return ' '.join(list(soup.stripped_strings))
