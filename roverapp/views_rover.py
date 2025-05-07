"""
Vistas para la comunicación con el UMG Basic Rover 2.0
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import requests
from datetime import datetime
import logging

# Configuración de logging
logger = logging.getLogger(__name__)

# URL del ESP8266 (puede ser configurada en la base de datos para cada usuario)
# Por defecto, usamos una dirección IP local que debe ser cambiada según el rover
ROVER_URL = "http://192.168.1.100"  # CAMBIAR POR LA IP REAL DEL ESP8266

@csrf_exempt
@login_required
def enviar_comando_rover(request):
    """
    Envía un comando al rover
    
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
    
    # Obtener el comando del cuerpo de la solicitud
    try:
        data = json.loads(request.body)
        comando = data.get('comando', '')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    
    if not comando:
        return JsonResponse({
            'success': False,
            'message': 'No se proporcionó un comando'
        }, status=400)
    
    # Intentar enviar el comando al rover
    try:
        # Registro del envío
        logger.info(f"Enviando comando al rover: {comando}")
        
        # Enviar petición HTTP al ESP8266
        response = requests.post(
            f"{ROVER_URL}/ejecutar",
            json={"comando": comando},
            timeout=5  # Timeout de 5 segundos
        )
        
        # Verificar respuesta
        if response.status_code == 200:
            response_data = response.json()
            return JsonResponse({
                'success': True,
                'message': f"Comando enviado exitosamente: {comando}",
                'rover_response': response_data
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f"Error en la respuesta del rover: {response.status_code}",
                'rover_response': response.text if response.text else "Sin respuesta"
            }, status=500)
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión al rover. URL: {ROVER_URL}")
        return JsonResponse({
            'success': False,
            'message': f"No se pudo conectar con el rover. Verifique que esté encendido y conectado a la red."
        }, status=503)
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con el rover. URL: {ROVER_URL}")
        return JsonResponse({
            'success': False,
            'message': f"Timeout al conectar con el rover. La conexión tardó demasiado tiempo."
        }, status=504)
    
    except Exception as e:
        logger.error(f"Error al enviar comando: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f"Error al enviar comando: {str(e)}"
        }, status=500)

@login_required
def detener_rover(request):
    """
    Detiene cualquier operación en curso en el rover
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        JsonResponse: Resultado de la operación
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Intentar enviar el comando de detención al rover
    try:
        # Registro de la detención
        logger.info("Deteniendo el rover")
        
        # Enviar petición HTTP al ESP8266
        response = requests.get(
            f"{ROVER_URL}/detener",
            timeout=5  # Timeout de 5 segundos
        )
        
        # Verificar respuesta
        if response.status_code == 200:
            response_data = response.json()
            return JsonResponse({
                'success': True,
                'message': "Rover detenido exitosamente",
                'rover_response': response_data
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f"Error en la respuesta del rover: {response.status_code}",
                'rover_response': response.text if response.text else "Sin respuesta"
            }, status=500)
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión al rover. URL: {ROVER_URL}")
        return JsonResponse({
            'success': False,
            'message': f"No se pudo conectar con el rover. Verifique que esté encendido y conectado a la red."
        }, status=503)
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con el rover. URL: {ROVER_URL}")
        return JsonResponse({
            'success': False,
            'message': f"Timeout al conectar con el rover. La conexión tardó demasiado tiempo."
        }, status=504)
    
    except Exception as e:
        logger.error(f"Error al detener rover: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f"Error al detener rover: {str(e)}"
        }, status=500)

@login_required
def estado_rover(request):
    """
    Consulta el estado actual del rover
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        JsonResponse: Estado del rover
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
    # Intentar consultar el estado del rover
    try:
        # Registro de la consulta
        logger.info("Consultando estado del rover")
        
        # Enviar petición HTTP al ESP8266
        response = requests.get(
            f"{ROVER_URL}/estado",
            timeout=5  # Timeout de 5 segundos
        )
        
        # Verificar respuesta
        if response.status_code == 200:
            response_data = response.json()
            return JsonResponse({
                'success': True,
                'message': "Estado consultado exitosamente",
                'rover_status': response_data
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f"Error en la respuesta del rover: {response.status_code}",
                'rover_response': response.text if response.text else "Sin respuesta"
            }, status=500)
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión al rover. URL: {ROVER_URL}")
        return JsonResponse({
            'success': False,
            'message': f"No se pudo conectar con el rover. Verifique que esté encendido y conectado a la red."
        }, status=503)
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con el rover. URL: {ROVER_URL}")
        return JsonResponse({
            'success': False,
            'message': f"Timeout al conectar con el rover. La conexión tardó demasiado tiempo."
        }, status=504)
    
    except Exception as e:
        logger.error(f"Error al consultar estado: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f"Error al consultar estado: {str(e)}"
        }, status=500)

@csrf_exempt
@login_required
def ejecutar_programa_rover(request):
    """
    Ejecuta un programa completo en el rover
    
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
    
    # Obtener el programa del cuerpo de la solicitud
    try:
        data = json.loads(request.body)
        python_code = data.get('python_code', '')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    
    if not python_code:
        return JsonResponse({
            'success': False,
            'message': 'No se proporcionó código Python para ejecutar'
        }, status=400)
    
    # Procesar el código Python para extraer comandos para el rover
    comandos = procesar_codigo_python(python_code)
    
    if not comandos:
        return JsonResponse({
            'success': False,
            'message': 'No se pudieron extraer comandos válidos del código'
        }, status=400)
    
    # Ejecutar el programa en el rover
    resultado = ejecutar_programa_rover_interno(comandos)
    
    if not resultado['success']:
        return JsonResponse(resultado, status=503)
    
    return JsonResponse({
        'success': True,
        'message': f"Programa iniciado. Ejecutando {len(comandos)} comandos.",
        'comandos': comandos
    })

def ejecutar_programa_rover_interno(comandos):
    """
    Función interna para ejecutar un programa completo en el rover
    
    Args:
        comandos (list): Lista de comandos a ejecutar
    
    Returns:
        dict: Resultado de la operación
    """
    if not comandos or not isinstance(comandos, list):
        return {
            'success': False,
            'message': 'No se proporcionaron comandos válidos'
        }
    
    # Registrar el inicio del programa
    logger.info(f"Iniciando programa con {len(comandos)} comandos")
    
    try:
        # Crear un comando especial que incluye toda la secuencia
        comando_programa = "programa:" + ",".join(comandos)
        
        # Enviar petición HTTP al ESP8266
        response = requests.post(
            f"{ROVER_URL}/ejecutar",
            json={"comando": comando_programa},
            timeout=5  # Timeout de 5 segundos
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': f"Programa enviado exitosamente ({len(comandos)} comandos)",
                'rover_response': response.json() if response.text else {}
            }
        else:
            return {
                'success': False,
                'message': f"Error en la respuesta del rover: {response.status_code}",
                'rover_response': response.text if response.text else "Sin respuesta"
            }
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión al rover. URL: {ROVER_URL}")
        return {
            'success': False,
            'message': f"No se pudo conectar con el rover. Verifique que esté encendido y conectado a la red."
        }
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con el rover. URL: {ROVER_URL}")
        return {
            'success': False,
            'message': f"Timeout al conectar con el rover. La conexión tardó demasiado tiempo."
        }
    
    except Exception as e:
        logger.error(f"Error al enviar programa: {str(e)}")
        return {
            'success': False,
            'message': f"Error al enviar programa: {str(e)}"
        }

def procesar_codigo_python(codigo):
    """
    Procesa el código Python para extraer comandos para el rover
    
    Args:
        codigo (str): Código Python generado por el transpilador
    
    Returns:
        list: Lista de comandos a ejecutar por el rover
    """
    comandos = []
    
    # Dividir el código en líneas
    lineas = codigo.strip().split('\n')
    
    # Buscar líneas que contengan comandos para el rover
    for linea in lineas:
        if 'rover.move_wheels' in linea:
            # Extraer el parámetro
            param = extraer_parametro(linea)
            comandos.append(f"avanzar_vlts:{param}")
        
        elif 'rover.move_cm' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"avanzar_ctms:{param}")
        
        elif 'rover.move_meters' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"avanzar_mts:{param}")
        
        elif 'rover.turn_right' in linea:
            comandos.append("girar:1")
        
        elif 'rover.turn_left' in linea:
            comandos.append("girar:-1")
        
        elif 'rover.move_straight' in linea:
            comandos.append("girar:0")
        
        elif 'rover.draw_circle' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"circulo:{param}")
        
        elif 'rover.draw_square' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"cuadrado:{param}")
        
        elif 'rover.rotate' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"rotar:{param}")
        
        elif 'rover.walk' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"caminar:{param}")
        
        elif 'rover.moonwalk' in linea:
            param = extraer_parametro(linea)
            comandos.append(f"moonwalk:{param}")
    
    return comandos

def extraer_parametro(linea):
    """
    Extrae el parámetro de una línea de código
    
    Args:
        linea (str): Línea de código Python
    
    Returns:
        str: Parámetro extraído
    """
    inicio = linea.find('(') + 1
    fin = linea.find(')')
    
    if inicio > 0 and fin > inicio:
        return linea[inicio:fin].strip()
    
    return "0"