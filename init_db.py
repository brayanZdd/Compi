"""
Script para inicializar la base de datos con datos de ejemplo
Ejecutar con: python manage.py shell < init_db.py
"""
import os
import django

# Configurar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rover.settings')
django.setup()

from roverapp.models import Rol, Usuario
from django.contrib.auth.hashers import make_password

def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    print("Inicializando base de datos...")
    
    # Crear roles si no existen
    admin_rol, created_admin = Rol.objects.get_or_create(
        nombre='Administrador',
        defaults={'id_rol': 1}
    )
    
    if created_admin:
        print("Rol de Administrador creado")
    else:
        print("Rol de Administrador ya existe")
    
    aspirante_rol, created_aspirante = Rol.objects.get_or_create(
        nombre='Aspirante',
        defaults={'id_rol': 2}
    )
    
    if created_aspirante:
        print("Rol de Aspirante creado")
    else:
        print("Rol de Aspirante ya existe")
    
    # Crear usuario administrador si no existe
    admin_user, created_admin_user = Usuario.objects.get_or_create(
        nickname='admin',
        defaults={
            'nombre': 'Administrador del Sistema',
            'correo': 'admin@umg.edu.gt',
            'telefono': '12345678',
            'id_rol': admin_rol,
            'password': make_password('admin123'),
            'avatar': '',  # Base64 vacío
            'username': 'admin',
            'email': 'admin@umg.edu.gt',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created_admin_user:
        print("Usuario administrador creado")
    else:
        print("Usuario administrador ya existe")
    
    # Crear usuarios de ejemplo (aspirantes)
    aspirante1, created_aspirante1 = Usuario.objects.get_or_create(
        nickname='aspirante1',
        defaults={
            'nombre': 'Aspirante Uno',
            'correo': 'aspirante1@umg.edu.gt',
            'telefono': '87654321',
            'id_rol': aspirante_rol,
            'password': make_password('password123'),
            'avatar': '',  # Base64 vacío
            'username': 'aspirante1',
            'email': 'aspirante1@umg.edu.gt'
        }
    )
    
    if created_aspirante1:
        print("Usuario aspirante1 creado")
    else:
        print("Usuario aspirante1 ya existe")
    
    aspirante2, created_aspirante2 = Usuario.objects.get_or_create(
        nickname='aspirante2',
        defaults={
            'nombre': 'Aspirante Dos',
            'correo': 'aspirante2@umg.edu.gt',
            'telefono': '76543210',
            'id_rol': aspirante_rol,
            'password': make_password('password123'),
            'avatar': '',  # Base64 vacío
            'username': 'aspirante2',
            'email': 'aspirante2@umg.edu.gt'
        }
    )
    
    if created_aspirante2:
        print("Usuario aspirante2 creado")
    else:
        print("Usuario aspirante2 ya existe")
    
    print("Inicialización de la base de datos completada.")

# Ejecutar la función
if __name__ == "__main__":
    init_database()