from django.urls import path
from . import views

app_name = 'speech_recognition'




urlpatterns = [
    path('HomePage', views.view_homePage, name='voice_recorder_HomePage'),
    # TODO Delete
    # path('voice_topic_result', views.fetch_topic_result, name='voice_topic_result'),
    path('voice_recorde_result', views.fetch_voice_recorde_result, name='voice_recorde_result'),
    path('addTopic', views.add_topic_and_fetch_topic_result, name='addTopic'),
]
