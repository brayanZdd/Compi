"""
Transpilador de UMG++ a Python
Este módulo convierte código UMG++ a código Python que puede ser ejecutado
por el UMG Basic Rover 2.0.
"""
import re
import json

class UMGPPTranspiler:
    """Clase para transpilar código UMG++ a Python"""
    
    def __init__(self):
        """Inicializar el transpilador"""
        # Expresiones regulares para los tokens
        self.token_patterns = [
            ('KEYWORD', r'\b(PROGRAM|BEGIN|END)\b'),
            ('FUNCTION', r'\b(avanzar_vlts|avanzar_ctms|avanzar_mts|girar|circulo|cuadrado|rotar|caminar|moonwalk)\b'),
            ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('NUMBER', r'-?\d+'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('SEMICOLON', r';'),
            ('PLUS', r'\+'),
            ('DOT', r'\.'),
            ('WHITESPACE', r'\s+'),
        ]
    
    def tokenize(self, code):
        """
        Análisis léxico del código UMG++
        
        Args:
            code (str): Código fuente en UMG++
            
        Returns:
            list: Lista de tokens encontrados
            list: Lista de errores léxicos
        """
        tokens = []
        errors = []
        
        # Analizar el código línea por línea
        lines = code.split('\n')
        for line_number, line in enumerate(lines, 1):
            position = 0
            
            while position < len(line):
                match = None
                
                for token_type, pattern in self.token_patterns:
                    regex = re.compile(pattern)
                    result = regex.match(line[position:])
                    
                    if result:
                        value = result.group(0)
                        
                        if token_type != 'WHITESPACE':
                            tokens.append({
                                'type': token_type,
                                'value': value,
                                'line': line_number,
                                'column': position + 1
                            })
                        
                        position += len(value)
                        match = True
                        break
                
                if not match:
                    errors.append({
                        'message': f"Carácter no reconocido: '{line[position]}'",
                        'line': line_number,
                        'column': position + 1
                    })
                    position += 1
        
        return tokens, errors
    
    def parse(self, tokens):
        """
        Análisis sintáctico de los tokens UMG++
        
        Args:
            tokens (list): Lista de tokens
            
        Returns:
            dict: Árbol de sintaxis abstracta (AST)
            list: Lista de errores sintácticos
        """
        position = 0
        errors = []
        
        # Función para avanzar al siguiente token si coincide con el tipo esperado
        def match(expected_type):
            nonlocal position
            if position < len(tokens) and tokens[position]['type'] == expected_type:
                token = tokens[position]
                position += 1
                return token
            return None
        
        # Función para reportar errores sintácticos
        def syntax_error(expected):
            nonlocal position
            token = tokens[position] if position < len(tokens) else tokens[-1]
            errors.append({
                'message': f"Error de sintaxis: se esperaba {expected}, pero se encontró '{token['value']}'",
                'line': token['line'],
                'column': token['column']
            })
            position += 1
            return None
        
        # Analizar el programa completo
        def parse_program():
            if not match('KEYWORD') or tokens[position - 1]['value'] != 'PROGRAM':
                return syntax_error('PROGRAM')
            
            program_name = match('IDENTIFIER')
            if not program_name:
                return syntax_error('nombre de programa')
            
            if not match('KEYWORD') or tokens[position - 1]['value'] != 'BEGIN':
                return syntax_error('BEGIN')
            
            instructions = []
            while position < len(tokens) and not (tokens[position]['type'] == 'KEYWORD' and tokens[position]['value'] == 'END'):
                instruction = parse_instruction()
                if instruction:
                    instructions.append(instruction)
                else:
                    # Avanzar hasta el próximo punto y coma si hay un error
                    while position < len(tokens) and tokens[position]['type'] != 'SEMICOLON':
                        position += 1
                    if position < len(tokens):
                        position += 1
            
            if not match('KEYWORD') or tokens[position - 1]['value'] != 'END':
                return syntax_error('END')
            
            if not match('DOT'):
                return syntax_error('un punto (.) para finalizar el programa')
            
            return {
                'type': 'program',
                'name': program_name['value'],
                'instructions': instructions
            }
        
        # Analizar una instrucción
        def parse_instruction():
            if position < len(tokens) and tokens[position]['type'] == 'FUNCTION' and tokens[position]['value'] == 'girar':
                return parse_girar_combination()
            
            if position < len(tokens) and tokens[position]['type'] == 'FUNCTION':
                func = match('FUNCTION')
                
                if not match('LPAREN'):
                    return syntax_error('un paréntesis de apertura (')
                
                param_token = match('NUMBER')
                if not param_token:
                    return syntax_error('un número entero')
                
                if not match('RPAREN'):
                    return syntax_error('un paréntesis de cierre )')
                
                if not match('SEMICOLON'):
                    return syntax_error('un punto y coma (;) para finalizar la instrucción')
                
                return {
                    'type': 'instruction',
                    'function': func['value'],
                    'parameter': int(param_token['value'])
                }
            
            return syntax_error('una instrucción válida')
        
        # Analizar una combinación de girar + avanzar
        def parse_girar_combination():
            girar_instructions = []
            advance_instruction = None
            
            # Primer girar
            first_girar = match('FUNCTION')
            
            if not match('LPAREN'):
                return syntax_error('un paréntesis de apertura (')
            
            first_param = match('NUMBER')
            if not first_param:
                return syntax_error('un número entero')
            
            if not match('RPAREN'):
                return syntax_error('un paréntesis de cierre )')
            
            girar_instructions.append({
                'function': first_girar['value'],
                'parameter': int(first_param['value'])
            })
            
            # Buscar combinaciones de + girar o + avanzar_*
            while match('PLUS'):
                next_function = match('FUNCTION')
                if not next_function:
                    return syntax_error('una función válida después del signo +')
                
                if not match('LPAREN'):
                    return syntax_error('un paréntesis de apertura (')
                
                param = match('NUMBER')
                if not param:
                    return syntax_error('un número entero')
                
                if not match('RPAREN'):
                    return syntax_error('un paréntesis de cierre )')
                
                if next_function['value'] == 'girar':
                    girar_instructions.append({
                        'function': next_function['value'],
                        'parameter': int(param['value'])
                    })
                elif next_function['value'] in ['avanzar_vlts', 'avanzar_ctms', 'avanzar_mts']:
                    advance_instruction = {
                        'function': next_function['value'],
                        'parameter': int(param['value'])
                    }
                    break
                else:
                    return syntax_error('una función girar o avanzar_* después del signo +')
            
            if not match('SEMICOLON'):
                return syntax_error('un punto y coma (;) para finalizar la instrucción')
            
            return {
                'type': 'giro_combination',
                'giros': girar_instructions,
                'advance': advance_instruction
            }
        
        # Iniciar el análisis del programa
        program = parse_program()
        
        if position < len(tokens):
            errors.append({
                'message': 'Hay tokens adicionales después del final del programa',
                'line': tokens[position]['line'],
                'column': tokens[position]['column']
            })
        
        return program, errors
    
    def analyze_semantics(self, ast):
        """
        Análisis semántico del AST
        
        Args:
            ast (dict): Árbol de sintaxis abstracta
            
        Returns:
            list: Lista de errores semánticos
        """
        errors = []
        
        if not ast or 'instructions' not in ast:
            return errors
        
        for instruction in ast['instructions']:
            if instruction['type'] == 'instruction':
                # Validar parámetros según la función
                func = instruction['function']
                param = instruction['parameter']
                
                if func in ['avanzar_vlts', 'avanzar_ctms', 'avanzar_mts', 'rotar', 'caminar', 'moonwalk']:
                    if param == 0:
                        errors.append({
                            'message': f"Error semántico: El parámetro para {func} no puede ser 0",
                            'instruction': instruction
                        })
                elif func == 'girar':
                    if param not in [-1, 0, 1]:
                        errors.append({
                            'message': f"Error semántico: El parámetro para {func} debe ser -1, 0 o 1",
                            'instruction': instruction
                        })
                elif func in ['circulo', 'cuadrado']:
                    if param < 10 or param > 200:
                        errors.append({
                            'message': f"Error semántico: El parámetro para {func} debe estar entre 10 y 200 centímetros",
                            'instruction': instruction
                        })
            
            elif instruction['type'] == 'giro_combination':
                # Validar parámetros en combinaciones de giro
                for giro in instruction['giros']:
                    if giro['parameter'] not in [-1, 0, 1]:
                        errors.append({
                            'message': "Error semántico: El parámetro para girar debe ser -1, 0 o 1",
                            'instruction': instruction
                        })
                
                if instruction['advance']:
                    func = instruction['advance']['function']
                    param = instruction['advance']['parameter']
                    if param == 0:
                        errors.append({
                            'message': f"Error semántico: El parámetro para {func} no puede ser 0",
                            'instruction': instruction
                        })
        
        return errors
    
    def generate_python_code(self, ast):
        """
        Genera código Python a partir del AST
        
        Args:
            ast (dict): Árbol de sintaxis abstracta
            
        Returns:
            str: Código Python generado
        """
        if not ast:
            return ""
        
        python_code = [
            "# Código Python generado a partir de UMG++ para el UMG Basic Rover 2.0",
            "# Programa: " + ast['name'],
            "",
            "import time",
            "import math",
            "import rover_control",
            "",
            "def main():",
            "    print('Iniciando programa: " + ast['name'] + "')",
            "    rover = rover_control.Rover()",
            "    rover.initialize()",
            ""
        ]
        
        for instruction in ast['instructions']:
            if instruction['type'] == 'instruction':
                func = instruction['function']
                param = instruction['parameter']
                
                if func == 'avanzar_vlts':
                    python_code.append(f"    rover.move_wheels({param})  # Avanzar {param} vueltas")
                elif func == 'avanzar_ctms':
                    python_code.append(f"    rover.move_cm({param})  # Avanzar {param} centímetros")
                elif func == 'avanzar_mts':
                    python_code.append(f"    rover.move_meters({param})  # Avanzar {param} metros")
                elif func == 'girar':
                    if param == 1:
                        python_code.append("    rover.turn_right()  # Girar a la derecha")
                    elif param == -1:
                        python_code.append("    rover.turn_left()  # Girar a la izquierda")
                    else:  # param == 0
                        python_code.append("    rover.move_straight()  # Avanzar en línea recta")
                elif func == 'circulo':
                    python_code.append(f"    rover.draw_circle({param})  # Dibujar círculo de radio {param} cm")
                elif func == 'cuadrado':
                    python_code.append(f"    rover.draw_square({param})  # Dibujar cuadrado de lado {param} cm")
                elif func == 'rotar':
                    python_code.append(f"    rover.rotate({param})  # Rotar {param} vueltas")
                elif func == 'caminar':
                    python_code.append(f"    rover.walk({param})  # Caminar {param} pasos")
                elif func == 'moonwalk':
                    python_code.append(f"    rover.moonwalk({param})  # Moonwalk de {param} pasos")
            
            elif instruction['type'] == 'giro_combination':
                # Procesar combinaciones de giros
                giro_code = []
                for giro in instruction['giros']:
                    if giro['parameter'] == 1:
                        giro_code.append("rover.turn_right()")
                    elif giro['parameter'] == -1:
                        giro_code.append("rover.turn_left()")
                    else:  # param == 0
                        giro_code.append("rover.move_straight()")
                
                # Agregar el avance si existe
                if instruction['advance']:
                    func = instruction['advance']['function']
                    param = instruction['advance']['parameter']
                    
                    if func == 'avanzar_vlts':
                        giro_code.append(f"rover.move_wheels({param})")
                    elif func == 'avanzar_ctms':
                        giro_code.append(f"rover.move_cm({param})")
                    elif func == 'avanzar_mts':
                        giro_code.append(f"rover.move_meters({param})")
                
                # Agregar comentario descriptivo
                comment = " # " + " + ".join([f"girar({g['parameter']})" for g in instruction['giros']])
                if instruction['advance']:
                    comment += f" + {instruction['advance']['function']}({instruction['advance']['parameter']})"
                
                # Combinar el código con el comentario
                python_code.append(f"    {'; '.join(giro_code)}{comment}")
        
        # Finalizar el programa
        python_code.extend([
            "",
            "    rover.finalize()",
            "    print('Programa finalizado')",
            "",
            "if __name__ == '__main__':",
            "    main()"
        ])
        
        # También generar versión para ESP8266
        esp8266_code = self.generate_esp8266_code(ast)
        
        result = {
            'python_code': "\n".join(python_code),
            'esp8266_code': esp8266_code
        }
        
        return result
        
    def generate_esp8266_code(self, ast):
        """
        Genera código específico para el ESP8266
        
        Args:
            ast (dict): Árbol de sintaxis abstracta
            
        Returns:
            str: Lista de comandos para el ESP8266
        """
        if not ast:
            return []
        
        comandos = []
        
        for instruction in ast['instructions']:
            if instruction['type'] == 'instruction':
                func = instruction['function']
                param = instruction['parameter']
                
                if func == 'avanzar_vlts':
                    comandos.append(f"avanzar_vlts:{param}")
                elif func == 'avanzar_ctms':
                    comandos.append(f"avanzar_ctms:{param}")
                elif func == 'avanzar_mts':
                    comandos.append(f"avanzar_mts:{param}")
                elif func == 'girar':
                    comandos.append(f"girar:{param}")
                elif func == 'circulo':
                    comandos.append(f"circulo:{param}")
                elif func == 'cuadrado':
                    comandos.append(f"cuadrado:{param}")
                elif func == 'rotar':
                    comandos.append(f"rotar:{param}")
                elif func == 'caminar':
                    comandos.append(f"caminar:{param}")
                elif func == 'moonwalk':
                    comandos.append(f"moonwalk:{param}")
            
            elif instruction['type'] == 'giro_combination':
                # Procesar combinaciones de giros
                for giro in instruction['giros']:
                    comandos.append(f"girar:{giro['parameter']}")
                
                # Agregar el avance si existe
                if instruction['advance']:
                    func = instruction['advance']['function']
                    param = instruction['advance']['parameter']
                    
                    if func == 'avanzar_vlts':
                        comandos.append(f"avanzar_vlts:{param}")
                    elif func == 'avanzar_ctms':
                        comandos.append(f"avanzar_ctms:{param}")
                    elif func == 'avanzar_mts':
                        comandos.append(f"avanzar_mts:{param}")
        
        return comandos
    
    def compile(self, code):
        """
        Compila código UMG++ a Python
        
        Args:
            code (str): Código fuente en UMG++
            
        Returns:
            dict: Resultado de la compilación con el código Python generado o errores
        """
        # Análisis léxico
        tokens, lex_errors = self.tokenize(code)
        
        if lex_errors:
            return {
                'success': False,
                'stage': 'lexical',
                'errors': lex_errors
            }
        
        # Análisis sintáctico
        ast, parse_errors = self.parse(tokens)
        
        if parse_errors:
            return {
                'success': False,
                'stage': 'syntax',
                'errors': parse_errors
            }
        
        # Análisis semántico
        semantic_errors = self.analyze_semantics(ast)
        
        if semantic_errors:
            return {
                'success': False,
                'stage': 'semantic',
                'errors': semantic_errors
            }
        
        # Generación de código Python
        result = self.generate_python_code(ast)
        
        return {
            'success': True,
            'ast': ast,
            'python_code': result['python_code'],
            'esp8266_code': result['esp8266_code']
        }


def transpile_to_python(umgpp_code):
    """
    Función auxiliar para transpilar código UMG++ a Python
    
    Args:
        umgpp_code (str): Código fuente en UMG++
        
    Returns:
        dict: Resultado de la transpilación
    """
    transpiler = UMGPPTranspiler()
    return transpiler.compile(umgpp_code)