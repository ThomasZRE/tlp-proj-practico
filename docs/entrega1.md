# Entrega 1: Analizador Léxico y Sintáctico
---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Objetivos](#2-objetivos)
3. [El Lenguaje .brik](#3-el-lenguaje-brik)
4. [Arquitectura del Analizador](#4-arquitectura-del-analizador)
5. [Análisis Léxico (Tokenizer)](#5-análisis-léxico-tokenizer)
6. [Análisis Sintáctico (Parser)](#6-análisis-sintáctico-parser)
7. [Tabla de Símbolos](#7-tabla-de-símbolos)
8. [Árbol de Sintaxis Abstracta (AST)](#8-árbol-de-sintaxis-abstracta-ast)
9. [Casos de Prueba](#9-casos-de-prueba)

---

## 1. Introducción

En esta Entrega se implementa un analizador léxico y sintáctico completo para el lenguaje `.brik`, diseñado específicamente para definir configuraciones de juegos de ladrillos (Tetris, Snake, etc.).

### 1.1 ¿Qué hace el analizador?

El analizador toma un archivo `.brik` (texto plano) y lo convierte en un **Árbol de Sintaxis Abstracta (AST)** en formato JSON, que posteriormente será utilizado por el motor de juegos para ejecutar las reglas definidas.

**Flujo general:**
```
archivo.brik → [Lexer] → Tokens → [Parser]  → archivo.ast
```

---

## 2. Objetivos

- Construir un sistema de análisis que valide y procese archivos .brik
-  Implementar un tokenizador (lexer) que reconozca los elementos del lenguaje
-  Construir un parser recursivo descendente que valide la sintaxis
-  Generar una tabla de símbolos con las variables definidas
-  Producir un AST en formato JSON
-  Manejar comentarios y espacios en blanco
-  Reportar errores léxicos y sintácticos de forma clara

---

## 3. El Lenguaje .brik

### 3.1 Características del Lenguaje

El lenguaje .brik es un lenguaje declarativo diseñado para especificar configuraciones de juegos.

**Características principales:**
- **Declarativo:** Describe QUÉ es el juego, no CÓMO funciona
- **Tipado dinámico:** Soporta números, strings, objetos y arrays
- **Sintaxis simple:** Inspirada en JSON pero más flexible
- **Comentarios:** Líneas que comienzan con `#`
- **Variables mutables:** Usando la palabra clave `let`

### 3.2 Gramática del Lenguaje

```ebnf
programa      ::= declaracion*

declaracion   ::= ['let'] IDENTIFIER '=' valor
                | ['let'] IDENTIFIER '{' contenido '}'

valor         ::= STRING
                | NUMBER
                | objeto
                | array
                | IDENTIFIER

objeto        ::= '{' pares '}'
                | '{' valor '}'

pares         ::= par (',' par)*
par           ::= IDENTIFIER ':' valor

array         ::= '[' elementos ']'
elementos     ::= valor (',' valor)*

comentario    ::= '#' [^\n]* '\n'
```

### 3.3 Elementos del Lenguaje

#### Literales
```brik
# Strings (entre comillas dobles)
"Snake the game"
"LEFT_ARROW"

# Números (enteros o decimales)
100
0.5
3.14

# Booleanos (como strings)
"yes"
"no"
```

#### Estructuras de Datos

**Objetos:**
```brik
# Objeto con pares clave:valor
scoring {
    single_line: 100,
    double_line: 300
}

# Objeto con valor directo
name { "Tetris" }
```

**Arrays:**
```brik
# Array de números
board_size { [20, 10] }

# Array de strings
types { ["O", "I", "S", "Z", "L", "J", "T"] }

# Array de acciones
action [ "lock_piece", "check_lines", "spawn_piece" ]
```

#### Variables Mutables

```brik
# Variable mutable con let
let controls {
    mov_l: LEFT_ARROW,
    mov_r: RIGHT_ARROW
}

# Variable inmutable (sin let)
version { 0.1 }
```

#### Comentarios

```brik
# Esto es un comentario de una línea
# Los comentarios se ignoran completamente

name { "Tetris" }  # Comentario al final de línea
```

### 3.4 Ejemplo Completo: tetris.brik

```brik
#===============================
# Game generals
#===============================

name { "Tetris" }
version { 0.1 }
board_size { [20, 10] }
max_speed { 10 }

#===============================
# Game rules
#===============================

put_piece {
    event { "piece_landed" },
    action [
        "lock_piece",
        "check_lines",
        "spawn_piece"
    ]
}

let scoring {
    single_line { 100 },
    double_line { 300 },
    tetris { 800 }
}

#===============================
# Game Controls
#===============================

let controls {
    mov_l { "LEFT_ARROW" },
    mov_r { "RIGHT_ARROW" },
    rotate { "UP_ARROW" },
    drop { "DOWN_ARROW" }
}

#===============================
# Object definitions
#===============================

let pieces { 
    types { ["O", "I", "S", "Z", "L", "J", "T"] },
    speed { 1 },
    spawn_position { [0, 5] },
    rotation_enabled { "yes" }  
}
```

---

## 4. Arquitectura del Analizador

El analizador tiene tres partes básicas:

1. **Lexer (Tokenizador):** lee el archivo `.brik` y lo divide en piezas pequeñas llamadas tokens (como palabras).

2. **Parser (Analizador Sintáctico):** revisa que esos tokens tengan sentido según las reglas del lenguaje y arma un árbol de datos (AST).

3. **Generador:** toma ese árbol y lo guarda en un archivo `.ast` en formato JSON para que el motor de juegos lo use.

Resumiendo, el flujo es:
archivo.brik → Lexer → Tokens → Parser → AST → archivo.ast

---

## 5. Análisis Léxico (Tokenizer)

### 5.1 ¿Qué es el Tokenizer?

El **tokenizer** (o lexer) es la primera fase del análisis. Su función es:
1. Leer el archivo carácter por carácter
2. Agrupar caracteres en **tokens** (unidades con significado)
3. Clasificar cada token según su tipo

### 5.2 Tipos de Tokens

| Token | Patrón (Regex) | Ejemplo | Descripción |
|-------|----------------|---------|-------------|
| `STRING` | `\"([^\"]*)\"` | `"Tetris"` | Cadena de texto |
| `KEYWORD` | `\blet\b` | `let` | Palabra clave |
| `IDENTIFIER` | `\b(?!\d)\w+\b` | `controls` | Nombre de variable |
| `NUMBER` | `(\d+\.?\d*)` | `100`, `0.5` | Número entero o decimal |
| `SYMBOL` | `({}\[\]=,:)` | `{`, `[`, `:` | Símbolos especiales |
| `SKIP` | `\s+` | ` `, `\n`, `\t` | Espacios en blanco |
| `COMMENT` | `#` | `# comentario` | Comentario |

### 5.3 Especificación de Tokens

```python
token_specs = [ 
    ('STRING', r'\"([^\"]*)\"'),
    ('KEYWORD', r'\blet\b'),
    ('IDENTIFIER', r'\b(?!\d)\w+\b'),
    ('NUMBER', r'(\d+\.?\d*)'),
    ('SYMBOL', r'({|}|\[|\]|=|,|:)'),
    ('SKIP', r'\s+'),
    ('COMMENT', r'#')
]
```

### 5.4 Algoritmo del Tokenizer

```python
def tokenizer(source_code):
    tokens = []
    pos = 0
    
    while pos < len(source_code):
        found = None
        
        # Intenta cada patrón en orden
        for token_type, pattern in token_specs:
            rex = re.compile(pattern)
            m = rex.match(source_code, pos)
            
            if m:
                # CASO ESPECIAL: Comentarios
                if token_type == 'COMMENT':
                    # Ignora hasta fin de línea
                    rex1 = re.compile(r'.+(\n)*')
                    nlmatch = rex1.match(source_code, pos)
                    if nlmatch:
                        pos = nlmatch.end(0)
                    break
                
                # Obtener texto del token
                text = m.group(0)
                
                # Agregar token (excepto espacios)
                if token_type != 'SKIP':
                    tokens.append((token_type, text))
                
                pos = m.end(0)
                found = True
                break
        
        # Error léxico
        if not found:
            print("Error léxico: carácter no reconocido")
            break
    
    return tokens
```

### 5.5 Ejemplo de Tokenización

**Entrada:**
```brik
name { "Tetris" }
version { 0.1 }
```

**Salida (tokens):**
```python
[
    ('IDENTIFIER', 'name'),
    ('SYMBOL', '{'),
    ('STRING', '"Tetris"'),
    ('SYMBOL', '}'),
    ('IDENTIFIER', 'version'),
    ('SYMBOL', '{'),
    ('NUMBER', '0.1'),
    ('SYMBOL', '}')
]
```

---

## 6. Análisis Sintáctico (Parser)

### 6.1 ¿Qué es el Parser?

El parser (analizador sintáctico) toma la lista de tokens y:
1. Verifica que siguen la gramática del lenguaje
2. Construye un Árbol de Sintaxis Abstracta (AST)
3. Detecta errores de sintaxis

### 6.2 Tipo de Parser

El parser implementado es un Parser tiene las siguientes características:
- Lee tokens de izquierda a derecha
- Usa funciones recursivas para cada regla gramatical
- Mantiene un puntero (`pos`) al token actual

### 6.3 Clase Parser

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = {}  # Tabla de símbolos
    
    def peek(self):
        """Mira el token actual sin avanzar"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return (None, None)
    
    def consume(self):
        """Devuelve el token actual y avanza"""
        tok = self.peek()
        self.pos += 1
        return tok
```

### 6.4 Métodos del Parser

#### parse()
Método principal que procesa todas las declaraciones:

```python
def parse(self):
    ast = {}
    
    while self.pos < len(self.tokens):
        ttype, tval = self.peek()
        if ttype is None:
            break
        
        # Detectar 'let' (variable mutable)
        is_mutable = False
        if ttype == 'KEYWORD' and tval == 'let':
            is_mutable = True
            self.consume()
            ttype, tval = self.peek()
        
        # Debe venir un identificador
        if ttype == 'IDENTIFIER':
            key = tval
            self.consume()
            
            # Puede venir '=' o directamente el valor
            ttype, tval = self.peek()
            if tval == '=':
                self.consume()
            
            # Parsear el valor
            value = self.parse_value()
            
            # Guardar en AST y tabla de símbolos
            ast[key] = value
            self.symbol_table[key] = value
        else:
            self.consume()
    
    return ast
```

#### parse_value()
Interpreta diferentes tipos de valores:

```python
def parse_value(self):
    ttype, tval = self.peek()
    
    if ttype == 'STRING':
        self.consume()
        return tval.strip('"')
    
    elif ttype == 'NUMBER':
        self.consume()
        return float(tval) if '.' in tval else int(tval)
    
    elif tval == '{':
        return self.parse_object()
    
    elif tval == '[':
        return self.parse_array()
    
    elif ttype == 'IDENTIFIER':
        # Referencia a variable existente
        self.consume()
        return self.symbol_table.get(tval, tval)
    
    else:
        raise SyntaxError("valor inesperado")
```

#### parse_object()
Maneja objetos entre llaves `{ }`:

```python
def parse_object(self):
    self.consume()  # Consumir '{'
    
    ttype, tval = self.peek()
    
    # Caso: { valor_directo }
    if ttype in ['STRING', 'NUMBER'] or tval == '[':
        value = None
        if ttype == 'STRING':
            value = tval.strip('"')
            self.consume()
        elif ttype == 'NUMBER':
            value = float(tval) if '.' in tval else int(tval)
            self.consume()
        elif tval == '[':
            value = self.parse_array()
        
        # Cerrar '}'
        ttype, tval = self.peek()
        if tval == '}':
            self.consume()
        
        return value
    
    # Caso: { clave: valor, ... }
    obj = {}
    while True:
        ttype, tval = self.peek()
        if tval == '}':
            self.consume()
            break
        
        if ttype == 'IDENTIFIER':
            key = tval
            self.consume()
            
            # Puede venir ':' o un bloque
            ttype, tval = self.peek()
            if tval == ':':
                self.consume()
                obj[key] = self.parse_value()
            else:
                obj[key] = self.parse_value()
            
            # Coma opcional
            ttype, tval = self.peek()
            if tval == ',':
                self.consume()
        else:
            self.consume()
    
    return obj
```

#### parse_array()
Maneja arrays entre corchetes `[ ]`:

```python
def parse_array(self):
    arr = []
    self.consume()  # Consumir '['
    
    while True:
        ttype, tval = self.peek()
        if tval == ']':
            self.consume()
            break
        
        # Elemento del array
        if ttype == 'IDENTIFIER':
            self.consume()
            arr.append(self.symbol_table.get(tval, tval))
        else:
            arr.append(self.parse_value())
        
        # Coma opcional
        ttype, tval = self.peek()
        if tval == ',':
            self.consume()
    
    return arr
```

---

## 7. Tabla de Símbolos

### 7.1 ¿Qué es la Tabla de Símbolos?

La **tabla de símbolos** es un diccionario que almacena las variables definidas durante el parsing.


### 7.2 Ejemplo de Uso

**Código .brik:**
```brik
max_speed { 10 }

let pieces {
    speed: max_speed
}
```

**Tabla de símbolos durante el parsing:**
```python
{
    'max_speed': 10
}
```

Cuando el parser encuentra `speed: max_speed`, consulta la tabla y resuelve `max_speed` a `10`.

**AST resultante:**
```json
{
    "max_speed": 10,
    "pieces": {
        "speed": 10
    }
}
```

---

## 8. Árbol de Sintaxis Abstracta (AST)

### 8.1 ¿Qué es el AST?

El **AST** (Abstract Syntax Tree) es una representación estructurada del código fuente que:
- Elimina detalles sintácticos innecesarios (espacios, comentarios)
- Organiza el código en una jerarquía lógica
- Facilita su posterior procesamiento


### 8.3 Ejemplo Completo

**Entrada (tetris.brik):**
```brik
name { "Tetris" }
version { 0.1 }
board_size { [20, 10] }

let controls {
    mov_l { "LEFT_ARROW" },
    mov_r { "RIGHT_ARROW" }
}

let scoring {
    single_line { 100 },
    tetris { 800 }
}
```

**Salida (tetrisarbol.ast):**
```json
{
    "name": "Tetris",
    "version": 0.1,
    "board_size": [20, 10],
    "controls": {
        "mov_l": "LEFT_ARROW",
        "mov_r": "RIGHT_ARROW"
    },
    "scoring": {
        "single_line": 100,
        "tetris": 800
    }
}
```

---

## 9. Casos de Prueba

### 9.1 Prueba 1: Tetris Completo

**Archivo:** `tetris.brik`

**Comando:**
```bash
python analizer.py
# Input: tetris
```

**Resultado Esperado:**
-  No hay errores léxicos
-  No hay errores sintácticos
-  Se genera `tetrisarbol.ast`
- El AST contiene todas las configuraciones

**Estado:**  APROBADO

---

### 9.2 Prueba 2: Snake Completo

**Archivo:** `snake.brik`

**Comando:**
```bash
python analizer.py
# Input: snake
```

**Resultado Esperado:**
-  Procesa correctamente arrays y objetos anidados
-  Maneja comentarios extensos
- Genera `snakearbol.ast`

**Estado:**  APROBADO

---

### 9.3 Prueba 3: Sintaxis con Errores

**Entrada (error.brik):**
```brik
name { "Test"
version { 0.1 }
```
*(Falta cerrar llave)*

**Resultado Esperado:**
```
ERROR DE SINTAXIS: faltó '}' al final
```

**Estado:**  APROBADO (detecta error)

---

### 9.4 Prueba 4: Comentarios

**Entrada:**
```brik
# Esto es un comentario
name { "Test" }  # Comentario inline

# Otro comentario
version { 1.0 }
```

**Resultado Esperado:**
-  se ignoralos comentarios
-  Procesa solo las declaraciones

**Estado:**  APROBADO

---

### 9.5 Prueba 5: Referencias entre Variables

**Entrada:**
```brik
base_speed { 5 }

let player {
    speed: base_speed
}
```

**AST Esperado:**
```json
{
    "base_speed": 5,
    "player": {
        "speed": 5
    }
}
```

**Estado:**  APROBADO


---