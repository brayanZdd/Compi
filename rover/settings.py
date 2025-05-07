# Configuración de usuario personalizado
AUTH_USER_MODEL = 'roverapp.Usuario'

# URLs de login/logout
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/editor/'
LOGOUT_REDIRECT_URL = '/'

# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_correo@gmail.com'  # CAMBIAR ESTO
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_app'  # CAMBIAR ESTO