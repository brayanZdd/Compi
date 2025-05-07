from django.urls import path
from . import views_api

urlpatterns = [
    path('compile/', views_api.compile_code, name='api_compile'),
    path('save/', views_api.save_code, name='api_save'),
    path('execute/', views_api.execute_code, name='api_execute'),
    path('programs/', views_api.get_user_programs, name='api_programs'),
    path('programs/<str:program_id>/', views_api.get_program_content, name='api_program_content'),
]