"""
Módulo de control para el UMG Basic Rover 2.0
Este módulo simula el control del rover físico para pruebas y depuración.
"""
import time
import math
import logging

# Configurar el registro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rover.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("rover_control")

class Rover:
    """Clase para controlar el UMG Basic Rover 2.0"""
    
    def __init__(self):
        """Inicializar el rover"""
        # Posición y orientación del rover
        self.position_x = 0.0
        self.position_y = 0.0
        self.orientation = 0.0  # En grados (0 = adelante, 90 = derecha, etc.)
        
        # Constantes para conversión
        self.wheel_circumference = 20.0  # cm
        self.rover_width = 15.0  # cm (distancia entre ruedas)
        
        # Estado de los motores
        self.left_motor_enabled = True
        self.right_motor_enabled = True
        
        logger.info("Rover instanciado")
    
    def initialize(self):
        """Inicializar el hardware del rover"""
        logger.info("Iniciando rover")
        
        # Aquí se inicializarían los pines GPIO, servos, etc.
        # En este caso, simplemente simularemos que todo funciona
        
        logger.info("Hardware del rover inicializado")
        return True
    
    def finalize(self):
        """Finalizar y liberar recursos"""
        logger.info("Finalizando rover")
        
        # Aquí se liberarían los recursos (pines GPIO, etc.)
        
        logger.info("Recursos liberados")
        return True
    
    def move_wheels(self, turns):
        """
        Mover las ruedas un número específico de vueltas
        
        Args:
            turns (int): Número de vueltas (positivo = adelante, negativo = atrás)
        """
        logger.info(f"Moviendo ruedas: {turns} vueltas")
        
        # Calcular la distancia en cm
        distance = turns * self.wheel_circumference
        
        # Mover el rover
        self._move_distance(distance)
        
        logger.info(f"Ruedas movidas {turns} vueltas")
    
    def move_cm(self, centimeters):
        """
        Mover el rover una distancia específica en centímetros
        
        Args:
            centimeters (int): Distancia en cm (positivo = adelante, negativo = atrás)
        """
        logger.info(f"Moviendo: {centimeters} cm")
        
        # Mover el rover
        self._move_distance(centimeters)
        
        logger.info(f"Movido {centimeters} cm")
    
    def move_meters(self, meters):
        """
        Mover el rover una distancia específica en metros
        
        Args:
            meters (int): Distancia en metros (positivo = adelante, negativo = atrás)
        """
        logger.info(f"Moviendo: {meters} metros")
        
        # Convertir a centímetros y mover
        centimeters = meters * 100
        self._move_distance(centimeters)
        
        logger.info(f"Movido {meters} metros")
    
    def turn_right(self):
        """Girar a la derecha (activando solo el motor izquierdo)"""
        logger.info("Girando a la derecha")
        
        # Desactivar motor derecho
        self.right_motor_enabled = False
        self.left_motor_enabled = True
        
        logger.info("Giro a la derecha completado")
    
    def turn_left(self):
        """Girar a la izquierda (activando solo el motor derecho)"""
        logger.info("Girando a la izquierda")
        
        # Desactivar motor izquierdo
        self.left_motor_enabled = False
        self.right_motor_enabled = True
        
        logger.info("Giro a la izquierda completado")
    
    def move_straight(self):
        """Avanzar en línea recta (activando ambos motores)"""
        logger.info("Configurando para avanzar en línea recta")
        
        # Activar ambos motores
        self.left_motor_enabled = True
        self.right_motor_enabled = True
        
        logger.info("Configuración para línea recta completada")
    
    def draw_circle(self, radius):
        """
        Dibujar un círculo con un radio específico
        
        Args:
            radius (int): Radio del círculo en centímetros
        """
        logger.info(f"Dibujando círculo de radio {radius} cm")
        
        # Calculamos la circunferencia
        circumference = 2 * math.pi * radius
        
        # Para dibujar un círculo, el rover debe girar mientras avanza
        # Simulamos esto cambiando la orientación gradualmente
        original_x = self.position_x
        original_y = self.position_y
        
        for angle in range(0, 360, 5):
            # Calcular nueva posición
            rad_angle = math.radians(angle)
            self.position_x = original_x + radius * math.cos(rad_angle)
            self.position_y
            self.position_y = original_y + radius * math.sin(rad_angle)
            self.orientation = angle + 90  # Tangente al círculo
            
            # Simular un pequeño retraso
            time.sleep(0.01)
        
        # Restaurar orientación original
        self.orientation = 0
        
        logger.info("Círculo completado")
    
    def draw_square(self, side):
        """
        Dibujar un cuadrado con un lado específico
        
        Args:
            side (int): Longitud del lado en centímetros
        """
        logger.info(f"Dibujando cuadrado de lado {side} cm")
        
        # Guardamos la posición original
        original_x = self.position_x
        original_y = self.position_y
        original_orientation = self.orientation
        
        # Dibujamos los 4 lados del cuadrado
        for i in range(4):
            # Avanzar side cm
            self._move_distance(side)
            
            # Girar 90 grados a la derecha
            self.orientation += 90
            if self.orientation >= 360:
                self.orientation -= 360
            
            # Simular un pequeño retraso
            time.sleep(0.5)
        
        # Restaurar orientación original
        self.orientation = original_orientation
        
        logger.info("Cuadrado completado")
    
    def rotate(self, turns):
        """
        Rotar el rover sobre su propio eje
        
        Args:
            turns (int): Número de vueltas (positivo = derecha, negativo = izquierda)
        """
        logger.info(f"Rotando {turns} vueltas")
        
        # Calcular el ángulo total
        angle = turns * 360
        
        # Actualizar la orientación
        self.orientation += angle
        
        # Normalizar a [0, 360)
        self.orientation %= 360
        
        logger.info(f"Rotación completada. Nueva orientación: {self.orientation} grados")
    
    def walk(self, steps):
        """
        Simular una caminata
        
        Args:
            steps (int): Número de pasos (positivo = adelante, negativo = atrás)
        """
        logger.info(f"Caminando {steps} pasos")
        
        direction = 1 if steps > 0 else -1
        abs_steps = abs(steps)
        
        for i in range(abs_steps):
            # Avanzar un poco
            self._move_distance(10 * direction)
            
            # Simular un "paso" moviendo ligeramente a los lados
            if i % 2 == 0:
                self.position_x += 5
            else:
                self.position_x -= 5
            
            # Simular un pequeño retraso
            time.sleep(0.2)
        
        logger.info("Caminata completada")
    
    def moonwalk(self, steps):
        """
        Simular el paso moonwalk de Michael Jackson
        
        Args:
            steps (int): Número de pasos (positivo = adelante, negativo = atrás)
        """
        logger.info(f"Ejecutando moonwalk de {steps} pasos")
        
        direction = 1 if steps > 0 else -1
        abs_steps = abs(steps)
        
        for i in range(abs_steps):
            # Moonwalk: parece que avanza hacia adelante pero en realidad retrocede
            self._move_distance(-10 * direction)
            
            # Simular el deslizamiento lateral del moonwalk
            if i % 2 == 0:
                self.position_x += 8
            else:
                self.position_x -= 8
            
            # Simular un pequeño retraso
            time.sleep(0.3)
        
        logger.info("Moonwalk completado")
    
    def _move_distance(self, distance):
        """
        Método interno para mover el rover una distancia específica
        
        Args:
            distance (float): Distancia en centímetros
        """
        # Calcular componentes x e y del movimiento según la orientación
        angle_rad = math.radians(self.orientation)
        delta_x = distance * math.cos(angle_rad)
        delta_y = distance * math.sin(angle_rad)
        
        # Actualizar posición teniendo en cuenta los motores activos
        if self.left_motor_enabled and self.right_motor_enabled:
            # Ambos motores: avance recto
            self.position_x += delta_x
            self.position_y += delta_y
        elif self.left_motor_enabled:
            # Solo motor izquierdo: giro a la derecha
            self.orientation += 10  # Girar gradualmente
            self.position_x += delta_x * 0.5
            self.position_y += delta_y * 0.5
        elif self.right_motor_enabled:
            # Solo motor derecho: giro a la izquierda
            self.orientation -= 10  # Girar gradualmente
            self.position_x += delta_x * 0.5
            self.position_y += delta_y * 0.5
        
        # Normalizar la orientación
        self.orientation %= 360
        
        # Simular el tiempo que tomaría el movimiento
        # (proporcional a la distancia)
        time.sleep(abs(distance) / 100)  # 1 segundo por cada 100 cm
        
        logger.debug(f"Nueva posición: ({self.position_x}, {self.position_y}), orientación: {self.orientation}°")