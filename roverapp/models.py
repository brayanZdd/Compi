from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'tb_roles'

class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    avatar = models.TextField()
    nickname = models.CharField(max_length=45)
    
    # Campos requeridos por AbstractUser pero que no usaremos
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    
    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['username', 'email']
    
    def __str__(self):
        return self.nickname
    
    class Meta:
        db_table = 'tb_usuarios'

class Ingreso(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tb_ingresos'