"""
Vistas para el dashboard administrativo
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Q
from django.db.models.functions import TruncDate
import json
from datetime import timedelta, datetime

from .models import Usuario, Ingreso, Rol

@login_required
def dashboard(request):
    """
    Vista del dashboard administrativo
    
    Args:
        request: Objeto de solicitud HTTP
    
    Returns:
        HttpResponse: Respuesta renderizada
    """
    # Verificar si el usuario es administrador
    if request.user.id_rol.nombre != 'Administrador':
        return redirect('editor')
    
    # Estadísticas generales
    total_usuarios = Usuario.objects.filter(id_rol__nombre='Aspirante').count()
    
    # Ingresos del día de hoy
    today = timezone.now().date()
    total_ingresos_hoy = Ingreso.objects.filter(fecha_ingreso__date=today).count()
    
    # Total de compilaciones (esto podría venir de una tabla de estadísticas)
    total_compilaciones = 0  # Placeholder, implementar según tu modelo de datos
    
    # Tiempo promedio de sesión
    # Calcular la duración de las sesiones completadas (con fecha_salida)
    duracion_expr = ExpressionWrapper(
        F('fecha_salida') - F('fecha_ingreso'),
        output_field=fields.DurationField()
    )
    
    ingresos_completos = Ingreso.objects.exclude(fecha_salida=None).annotate(duracion=duracion_expr)
    tiempo_promedio = ingresos_completos.aggregate(promedio=Avg('duracion'))['promedio']
    
    if tiempo_promedio:
        # Convertir a formato más legible (HH:MM:SS)
        total_seconds = tiempo_promedio.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        tiempo_promedio_session = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        tiempo_promedio_session = "00:00:00"
    
    # Obtener datos para el gráfico de ingresos por día
    # Últimos 7 días
    last_week = today - timedelta(days=6)
    ingresos_por_dia = Ingreso.objects.filter(
        fecha_ingreso__date__gte=last_week
    ).annotate(
        dia=TruncDate('fecha_ingreso')
    ).values('dia').annotate(
        count=Count('id_ingreso')
    ).order_by('dia')
    
    # Formatear datos para los gráficos
    fechas_ingresos = []
    conteo_ingresos = []
    
    for item in ingresos_por_dia:
        fechas_ingresos.append(item['dia'].strftime('%d-%m-%Y'))
        conteo_ingresos.append(item['count'])
    
    # Tiempo promedio por día
    tiempo_por_dia = ingresos_completos.filter(
        fecha_ingreso__date__gte=last_week
    ).annotate(
        dia=TruncDate('fecha_ingreso')
    ).values('dia').annotate(
        promedio=Avg('duracion')
    ).order_by('dia')
    
    fechas_tiempo = []
    promedio_tiempo = []
    
    for item in tiempo_por_dia:
        fechas_tiempo.append(item['dia'].strftime('%d-%m-%Y'))
        promedio_tiempo.append(item['promedio'].total_seconds() / 60)  # Convertir a minutos
    
    # Obtener listado de ingresos ordenados por fecha descendente
    ingresos = Ingreso.objects.select_related('id_usuario').all().order_by('-fecha_ingreso')
    
    # Calcular duración para cada ingreso
    for ingreso in ingresos:
        if ingreso.fecha_salida:
            duracion = ingreso.fecha_salida - ingreso.fecha_ingreso
            horas = duracion.seconds // 3600
            minutos = (duracion.seconds % 3600) // 60
            segundos = duracion.seconds % 60
            ingreso.duracion = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        else:
            ingreso.duracion = "En progreso"
    
    # Contexto para la plantilla
    context = {
        'total_usuarios': total_usuarios,
        'total_ingresos_hoy': total_ingresos_hoy,
        'total_compilaciones': total_compilaciones,
        'tiempo_promedio_session': tiempo_promedio_session,
        'ingresos': ingresos,
        'fechas_ingresos': json.dumps(fechas_ingresos),
        'conteo_ingresos': json.dumps(conteo_ingresos),
        'fechas_tiempo': json.dumps(fechas_tiempo),
        'promedio_tiempo': json.dumps(promedio_tiempo)
    }
    
    return render(request, 'dashboard.html', context)