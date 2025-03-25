from django.urls import path
from .views import fetch_messages, save_message, load_more_messages, send_message

urlpatterns = [
    path('fetch_messages/', fetch_messages, name='fetch_messages'),
    path('save_message/', save_message, name='save_message'),
    path('load_more_messages/', load_more_messages, name='load_more_messages'),
    path("send_message/", send_message, name="send_message"),
]
