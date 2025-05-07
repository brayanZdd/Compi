"""
Vistas de API para el compilador UMG++
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import os
from datetime import datetime

from .models import Usuario, Ingreso
from .transpiler import transpile_to_python

@csrf_exempt
@login_required
def compile_code(request):
    """
    API para compilar código UMG++ a Python
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        JsonResponse: Resultado de la compilación
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Obtener el código UMG++ del cuerpo de la solicitud
    try:
        data = json.loads(request.body)
        umgpp_code = data.get('code', '')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    
    if not umgpp_code:
        return JsonResponse({
            'success': False,
            'message': 'No se proporcionó código para compilar'
        }, status=400)
    
    # Compilar el código
    result = transpile_to_python(umgpp_code)
    
    # Registrar la compilación en estadísticas
    if result['success']:
        # Aquí se podría registrar la compilación en una tabla de estadísticas
        pass
    
    return JsonResponse(result)

@csrf_exempt
@login_required
def save_code(request):
    """
    API para guardar el código UMG++ en el servidor
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        JsonResponse: Resultado de la operación
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Obtener el código y nombre de archivo
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        filename = data.get('filename', '')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    
    if not code or not filename:
        return JsonResponse({
            'success': False,
            'message': 'Se requiere código y nombre de archivo'
        }, status=400)
    
    # Asegurarse de que el archivo tenga extensión .umgpp
    if not filename.endswith('.umgpp'):
        filename += '.umgpp'
    
    # Crear directorio para programas del usuario si no existe
    user_directory = os.path.join('media', 'programas', str(request.user.id_usuario))
    os.makedirs(user_directory, exist_ok=True)
    
    # Ruta completa del archivo
    file_path = os.path.join(user_directory, filename)
    
    # Guardar el archivo
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al guardar el archivo: {str(e)}'
        }, status=500)
    
    return JsonResponse({
        'success': True,
        'message': 'Archivo guardado correctamente',
        'path': file_path
    })

@login_required
def get_user_programs(request):
    """
    API para obtener los programas guardados por el usuario
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        JsonResponse: Lista de programas del usuario
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Directorio de programas del usuario
    user_directory = os.path.join('media', 'programas', str(request.user.id_usuario))
    
    # Verificar si el directorio existe
    if not os.path.exists(user_directory):
        return JsonResponse({
            'success': True,
            'programs': []
        })
    
    # Obtener lista de archivos .umgpp
    programs = []
    for file in os.listdir(user_directory):
        if file.endswith('.umgpp'):
            file_path = os.path.join(user_directory, file)
            stats = os.stat(file_path)
            
            programs.append({
                'name': file,
                'path': file_path,
                'size': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return JsonResponse({
        'success': True,
        'programs': programs
    })

@login_required
def get_program_content(request, program_id):
    """
    API para obtener el contenido de un programa específico
    
    Args:
        request: Objeto de solicitud HTTP
        program_id: ID del programa (nombre del archivo)
    
    Returns:
        JsonResponse: Contenido del programa
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Directorio de programas del usuario
    user_directory = os.path.join('media', 'programas', str(request.user.id_usuario))
    file_path = os.path.join(user_directory, program_id)
    
    # Verificar si el archivo existe
    if not os.path.exists(file_path) or not file_path.endswith('.umgpp'):
        return JsonResponse({
            'success': False,
            'message': 'Programa no encontrado'
        }, status=404)
    
    # Leer el contenido del archivo
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al leer el archivo: {str(e)}'
        }, status=500)
    
    return JsonResponse({
        'success': True,
        'content': content,
        'name': os.path.basename(file_path)
    })

@csrf_exempt
@login_required
def execute_code(request):
    """
    API para ejecutar el código UMG++ en el Rover
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        JsonResponse: Resultado de la ejecución
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Obtener el código UMG++ del cuerpo de la solicitud
    try:
        data = json.loads(request.body)
        umgpp_code = data.get('code', '')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    
    if not umgpp_code:
        return JsonResponse({
            'success': False,
            'message': 'No se proporcionó código para ejecutar'
        }, status=400)
    
    # Compilar el código
    result = transpile_to_python(umgpp_code)
    
    if not result['success']:
        return JsonResponse(result)
    
    # Si la compilación es exitosa, tenemos el código Python y los comandos para ESP8266
    python_code = result['python_code']
    esp8266_comandos = result['esp8266_code']
    
    # Intentar enviar los comandos al rover
    from .views_rover import ejecutar_programa_rover_interno
    ejecucion_result = ejecutar_programa_rover_interno(esp8266_comandos)
    
    if not ejecucion_result['success']:
        return JsonResponse({
            'success': False,
            'message': 'Error al ejecutar en el rover: ' + ejecucion_result['message'],
            'python_code': python_code,
            'esp8266_comandos': esp8266_comandos
        })
    
    return JsonResponse({
        'success': True,
        'message': 'Código enviado al Rover con éxito',
        'python_code': python_code,
        'esp8266_comandos': esp8266_comandos,
        'execution_id': datetime.now().strftime('%Y%m%d%H%M%S')
    })