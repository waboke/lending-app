from django.urls import re_path
from .consumers import LoanUpdateConsumer

websocket_urlpatterns = [
    re_path(r'ws/loans/$', LoanUpdateConsumer.as_asgi()),
]
