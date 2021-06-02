from django.urls import path
from . import views

app_name = 'speech_recognition'




urlpatterns = [
    path('HomePage', views.view_homePage, name='voice_recorder_HomePage'),
    path('voice_recorde_result', views.fetch_voice_recorde_result, name='voice_recorde_result'),
    path('addTopic', views.add_topic_and_fetch_topic_result, name='addTopic'),
    path('get_lead_user',views.get_lead_user,name='get_lead_user'),
    path('viewleaduser',views.view_leaduser,name='viewpager'),
    path('get_lead_user_HttpResponse', views.get_lead_user_HttpResponse, name='get_lead_user_HttpResponse'),

]
