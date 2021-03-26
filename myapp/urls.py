from django.urls import path
from . import views



app_name = 'speech_recognition'


urlpatterns = [
    path('Home', views.voice_recorder_HomePage, name='voice_recorder_HomePage'),
    path('voice_recorder',views.voice_recorder,name='voice_recorder'),
    ]
