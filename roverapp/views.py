from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import qrcode
from io import BytesIO
import base64
import os
import pdfkit
from .models import Usuario, Rol, Ingreso

def login_view(request):
    """Vista para el inicio de sesión"""
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        
        user = authenticate(request, username=nickname, password=password)
        
        if user is not None:
            login(request, user)
            
            # Registrar ingreso
            ingreso = Ingreso(id_usuario=user)
            ingreso.save()
            
            # Guardar el ID del ingreso en la sesión para registrar la salida después
            request.session['ingreso_id'] = ingreso.id_ingreso
            
            # Redirigir según el rol
            if user.id_rol.nombre == 'Administrador':
                return redirect('dashboard')
            else:
                return redirect('editor')
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})
    
    return render(request, 'login.html')

def registro_usuario(request):
    """Vista para el registro de usuarios"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        confirmar_password = request.POST.get('confirmar_password')
        nickname = request.POST.get('nickname')
        avatar = request.FILES.get('avatar')
        
        # Validaciones básicas
        if password != confirmar_password:
            return render(request, 'registro.html', {'error': 'Las contraseñas no coinciden'})
        
        if Usuario.objects.filter(correo=correo).exists():
            return render(request, 'registro.html', {'error': 'El correo ya está registrado'})
        
        if Usuario.objects.filter(nickname=nickname).exists():
            return render(request, 'registro.html', {'error': 'El nickname ya está en uso'})
        
        # Crear el usuario
        rol_aspirante = Rol.objects.get(nombre='Aspirante')
        
        # Procesar avatar
        avatar_data = None
        if avatar:
            avatar_data = base64.b64encode(avatar.read()).decode('utf-8')
        
        # Crear usuario
        user = Usuario(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            nickname=nickname,
            username=nickname,
            id_rol=rol_aspirante,
            avatar=avatar_data
        )
        user.set_password(password)
        user.save()
        
        # Generar credencial
        generar_credencial(user)
        
        return redirect('login')
    
    return render(request, 'registro.html')

@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    # Registrar salida
    if 'ingreso_id' in request.session:
        try:
            ingreso = Ingreso.objects.get(id_ingreso=request.session['ingreso_id'])
            ingreso.fecha_salida = timezone.now()
            ingreso.save()
        except Ingreso.DoesNotExist:
            pass
    
    logout(request)
    return redirect('login')

@login_required
def editor(request):
    """Vista para el editor de código"""
    return render(request, 'editor.html')

def generar_credencial(usuario):
    """Genera y envía la credencial del usuario por correo"""
    # Generar código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"ID:{usuario.id_usuario}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar QR en memoria
    buffer = BytesIO()
    img.save(buffer)
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Renderizar credencial HTML
    context = {
        'usuario': usuario,
        'qr_code': qr_image_base64
    }
    
    # Generar PDF
    html_string = render_to_string('credencial.html', context)
    pdf_filename = f"credencial_{usuario.id_usuario}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'credenciales', pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    # Generar PDF
    pdfkit.from_string(html_string, pdf_path)
    
    # Enviar por correo
    email = EmailMessage(
        'Tu credencial de acceso a UMG Basic Rover 2.0',
        'Adjunto encontrarás tu credencial de acceso.',
        settings.EMAIL_HOST_USER,
        [usuario.correo]
    )
    email.attach_file(pdf_path)
    email.send()