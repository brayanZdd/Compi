from django.urls import path
from . import views_rover

urlpatterns = [
    path('enviar-comando/', views_rover.enviar_comando_rover, name='api_rover_comando'),
    path('detener/', views_rover.detener_rover, name='api_rover_detener'),
    path('estado/', views_rover.estado_rover, name='api_rover_estado'),
    path('ejecutar-programa/', views_rover.ejecutar_programa_rover, name='api_rover_ejecutar_programa'),
]