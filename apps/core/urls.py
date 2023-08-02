from django.urls import path
from apps.core.views import home, ferramenta_youtube, ferramenta_qrcode, ferramenta_recibos, ferramenta_senha, ferramenta_numeros

urlpatterns = [
    path('', home, name='home'),
    path('youtube', ferramenta_youtube, name='ferramenta_youtube'),
    path('qrcode', ferramenta_qrcode, name='ferramenta_qrcode'),
    path('recibos', ferramenta_recibos, name='ferramenta_recibos'),
    path('senha', ferramenta_senha, name='ferramenta_senha'),
    path('numeros', ferramenta_numeros, name='ferramenta_numeros'),

]






