from django.urls import path, include
from . import views
from . import views_dashboard
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_usuario, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('editor/', views.editor, name='editor'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    path('api/', include('roverapp.urls_api')),
    path('api/rover/', include('roverapp.urls_rover')),
]

# Para servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)