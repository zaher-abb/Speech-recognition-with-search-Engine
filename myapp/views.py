from urllib import request
from urllib.request import urlopen

from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render
import sounddevice as sd
import speech_recognition as sr
import wavio
from googlesearch import search
from nltk.corpus import stopwords
from google_trans_new import google_translator

import gzip
import json
import pandas as df
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

    audio = sr.AudioFile('recording.wav')
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



def get_links_from_google(searched_text, request):

    searched_word = searched_text[-1]
    if topic_list.count(searched_word) == 1 :

        links = search(searched_word, tld="com", num=10, stop=10, pause=4)
        for i in links :
           static_links_list.append(i)
        return static_links_list
    else:
        return static_links_list




# TODO: text muss noch ausgewertet mit haufigkeit
def fetch_voice_recorde_result(request):
    links_list=[]
    language = request.GET['language']
    start_recording(request)
    print(speech_recognition(language))

    spoken_text = clean_stopwords(speech_recognition(language))
    print(spoken_text)
    for word in get_searched_words_and_sentence(speech_recognition(language)):
       links_list += search(word, tld="com", num=10, stop=5, pause=3)


    return render(request, 'test2.html', {'spoken_text': spoken_text, 'links': links_list})


# here to filter the text from stopped word that is not important like ..to..on ..for.. from ...... .
# function will return a list
def clean_stopwords(spoken_text):
    unwanted_words = set(stopwords.words("english") and stopwords.words("german"))

    wanted_words = []
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


# add topic to the Static list  " topic_list " and fetch result by rendering the page
def add_topic_and_fetch_topic_result(request):

    searched_word=request.GET['topic']
    topic_list.append(searched_word)
    spoken_text = list(set(topic_list))
    links_list = get_links_from_google(topic_list, request)
    links_list=list(links_list)
    lead_user_Daten=get_lead_user(request)

    name_list=lead_user_Daten['name']

    user_Score_list=lead_user_Daten['userScore']
    zibList=zip(links_list,name_list,user_Score_list)

    return render(request, 'voice.html', {'spoken_text': spoken_text,'zibList':zibList })


# Implement a for loop and pass a list containing the string tags script and style into the Beautiful Soup object as the sequence. with  bs4.BeautifulSoup.decompose().
# Pass the bs4.BeautifulSoup.stripped_strings generator into list(generator) to return a list of the remaining string text in the html object.

def read_text_of_website(url):
    soup = BeautifulSoup(urlopen(url).read())
    for script in soup(["script", "style"]):
        script.decompose()

    return ' '.join(list(soup.stripped_strings))


def get_lead_user(request):
    searched_topic=request.GET['topic']


    with gzip.open('couchdb_a_src_twitter_2021_04_08.json.gz', 'r') as zipfile:
        twitter_data = json.loads(zipfile.read().decode('ascii'))
    lead_users = []

    for i in twitter_data:
        try:
            hashtags = []
            for hashtag in i['entities']['hashtags']:
                hashtags.append(hashtag['text'])
            if searched_topic in i['text'] or searched_topic in hashtags:
                lead_users.append(
                    [i['user']['name'], i['user']['followers_count'], i['text'], i['user']['url'], i['retweet_count']])

        except Exception as e:
            print(e)
            pass

    tweet_text = df.DataFrame(data=lead_users,
                              columns=['user', "followers_total", 'text', 'url', 'retweet_count'])

    # Sum_Retweets
    tweet_text['sum_retweet'] = tweet_text.groupby(['user'])['retweet_count'].transform('sum')

    # number_of_tweets
    tweet_text['number_of_tweets'] = tweet_text.groupby(['user'])['user'].transform('count')

    # Drop the duplicates
    tweet_text = tweet_text.drop_duplicates(subset=['user'])

     # find a user_Score from formula
    tweet_text['User_Score'] = 100000 * tweet_text['number_of_tweets'] \
                               + 100000 * tweet_text['sum_retweet'] + 1 * tweet_text['followers_total']

    # sorted list first into User_Score and then to followers number
    sorted_list_for_leadUser = tweet_text.sort_values(by=['User_Score', 'followers_total'], ascending=False)

    name=sorted_list_for_leadUser['user'].tolist()
    userScore=sorted_list_for_leadUser['User_Score'].tolist()
    followers_total=sorted_list_for_leadUser['followers_total'].tolist()
    retweet_count=sorted_list_for_leadUser['retweet_count'].tolist()
    text=sorted_list_for_leadUser['text'].tolist()
    url=sorted_list_for_leadUser['url'].tolist()
    pydict={'name':name,'userScore':userScore , 'followers_total' : followers_total , 'url' :url , 'retweet_count':retweet_count,'text':text}


    return pydict
#
#
def get_lead_user_HttpResponse(request):
    lead_users_list_HttpResponse=get_lead_user(request)
    frame= df.DataFrame(lead_users_list_HttpResponse)
    geeks_object = frame.to_html()

    return HttpResponse(geeks_object)

def view_leaduser(request):
    return render(request, 'twitter_lead_user.html')