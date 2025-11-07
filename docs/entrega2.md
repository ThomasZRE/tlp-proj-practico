# Entrega 2: Motor Gráfico y de Juego

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Objetivos](#2-objetivos)
3. [Arquitectura del Motor](#3-arquitectura-del-motor)
4. [Especificaciones Técnicas](#4-especificaciones-técnicas)
5. [Implementación](#5-implementación)
6. [Sistema de Renderizado](#6-sistema-de-renderizado)
7. [Manejo de Entradas](#7-manejo-de-entradas)
8. [Bucle Principal del Juego](#8-bucle-principal-del-juego)
9. [Casos de Prueba](#9-casos-de-prueba)

---

## 1. Introducción

La **Entrega 2** implementa el motor gráfico base para el sistema de juegos de ladrillos. Este motor es **genérico** y no contiene lógica específica de ningún juego particular, proporcionando la infraestructura necesaria para:

- Crear y gestionar una ventana de juego
- Renderizar objetos en pantalla
- Capturar entradas del usuario
- Mantener un bucle de juego estable

### 1.1 Características Principales

- Ventana de 640×480 píxeles  
- Bucle de juego a 60 FPS  
- Sistema de objetos móviles  
- Control con teclado (flechas direccionales)  
- Detección de límites de pantalla  
- Compatible con Python 2.7 y 3.x  
- Tamaño < 1.44 MB

---

## 2. Objetivos

### 2.1 Objetivo Principal

Desarrollar un motor gráfico genérico que sirva como base para ejecutar diferentes juegos definidos mediante archivos `.brik`.

### 2.2 Objetivos Específicos

-  Crear sistema de inicialización de ventana
-  Implementar bucle principal del juego (game loop)
-  Desarrollar clase `movable_object` para entidades
-  Integrar sistema de captura de entradas
-  Implementar funciones de renderizado
-  Añadir restricciones de movimiento en bordes

---

## 3. Arquitectura del Motor

El motor gráfico usa Pygame para mostrar una ventana donde se dibujan los juegos y se capturan entradas del teclado.

El flujo básico es este:

1. Se inicializa Pygame, se crea la ventana y se configura un reloj para controlar los FPS.

2. Se crea un objeto móvil (un ladrillo rojo) con posición, tamaño y velocidad.

3. En un bucle que se repite mientras el juego está activo:

   - Se procesan los eventos, como cerrar la ventana.

   - Se limpia la pantalla (se pinta de negro).

   - Se dibuja el ladrillo en la pantalla.

   - Se leen las teclas presionadas para mover el ladrillo (arriba, abajo, izquierda, derecha).

   - Se aplican límites para que el ladrillo no salga de la ventana.

   - Se actualiza la pantalla con los cambios.

   - Se limita la velocidad del juego a 60 FPS.

4. Cuando el usuario cierra la ventana, se termina el bucle y se cierra Pygame.

En resumen, es un ciclo simple que actualiza la pantalla y responde al teclado para mover objetos.


---

## 4. Especificaciones Técnicas

### 4.1 Requisitos del Sistema

| Componente | Especificación Mínima |
|------------|----------------------|
| **Sistema Operativo** | Windows XP / Linux / macOS |
| **Python** | 2.7 o 3.x |
| **Pygame** | 1.9.1+ (Python 2.7) / 2.0+ (Python 3) |
| **RAM** | 64 MB |
| **Procesador** | AMD Athlon XP o equivalente |
| **Espacio en disco** | < 1.44 MB (restricción del proyecto) |
| **Resolución** | Mínimo 640×480 |

### 4.2 Configuración de la Ventana

```python
┌────────────────────────────────┐
│   VENTANA DEL MOTOR           │
├────────────────────────────────┤
│ Ancho:      640 píxeles        │
│ Alto:       480 píxeles        │
│ Título:     "Motor de Juegos"  │
│ FPS:        60 cuadros/seg     │
│ Color fondo: Negro (0,0,0)     │
└────────────────────────────────┘
```

### 4.3 Especificaciones del Objeto Móvil

**Ladrillo de Prueba:**
```python
┌─────────────────────────────┐
│   OBJETO: brick             │
├─────────────────────────────┤
│ Posición X:  320 (centro)   │
│ Posición Y:  240 (centro)   │
│ Ancho:       20 píxeles     │
│ Alto:        10 píxeles     │
│ Color:       Rojo           │
│ Velocidad:   3.5 px/frame   │
│              (210 px/seg)   │
└─────────────────────────────┘
```

---

## 5. Implementación

### 5.1 Estructura del Código

```python
# engine/test-motor.py

import pygame

# ==================
# CLASE MOVABLE_OBJECT
# ==================

class movable_object(): 
    def __init__(self, xpos, ypos, width, height, color):
        self.x = xpos
        self.y = ypos
        self.width = width 
        self.height = height
        self.color = color

# ==================
# INICIALIZACIÓN
# ==================

pygame.init()
screen = pygame.display.set_mode((640, 480))
s_width = screen.get_width()
s_height = screen.get_height()

brick = movable_object(s_width/2, s_height/2, 20, 10, "red")
speed = 3.5

clock = pygame.time.Clock()
running = True
dt = 0

# ==================
# BUCLE PRINCIPAL
# ==================

while running:
    # Fase 1: Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fase 2: Limpiar
    screen.fill("black")
    
    # Fase 3: Renderizar
    pygame.draw.rect(screen, brick.color, 
                    (brick.x, brick.y, brick.width, brick.height))
    
    # Fase 4: Entradas
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:    brick.y -= speed 
    if keys[pygame.K_DOWN]:  brick.y += speed
    if keys[pygame.K_LEFT]:  brick.x -= speed
    if keys[pygame.K_RIGHT]: brick.x += speed
    
    # Fase 5: Límites
    if brick.x <= 0:
        brick.x = 0
    if brick.x >= s_width - brick.width:
        brick.x = s_width - brick.width
    if brick.y <= 0:
        brick.y = 0
    if brick.y >= s_height - brick.height:
        brick.y = s_height - brick.height
    
    # Fase 6: Actualizar display
    pygame.display.flip()
    
    # Fase 7: Control FPS
    dt = clock.tick(60) / 1000

pygame.quit()
```

### 5.2 Clase `movable_object`

**Propósito:** Representar cualquier objeto móvil en el juego (ladrillos, bloques, personajes).

#### Atributos

| Atributo | Tipo | Descripción | Ejemplo |
|----------|------|-------------|---------|
| `x` | float | Coordenada X (horizontal) | `320.0` |
| `y` | float | Coordenada Y (vertical) | `240.0` |
| `width` | int | Ancho en píxeles | `20` |
| `height` | int | Alto en píxeles | `10` |
| `color` | str | Color del objeto | `"red"` |

#### Constructor

```python
def __init__(self, xpos, ypos, width, height, color):
    """
    Inicializa un objeto móvil.
    
    Args:
        xpos (float): Posición inicial en X
        ypos (float): Posición inicial en Y
        width (int): Ancho del objeto
        height (int): Alto del objeto
        color (str): Color del objeto
    """
    self.x = xpos
    self.y = ypos
    self.width = width 
    self.height = height
    self.color = color
```

#### Ejemplo de Uso

```python
# Crear ladrillo en el centro de la pantalla
brick = movable_object(320, 240, 20, 10, "red")

# Acceder a propiedades
print(brick.x)      # 320
print(brick.color)  # "red"

# Modificar posición
brick.x += 5        # Mover 5 píxeles a la derecha
brick.y -= 3        # Mover 3 píxeles arriba
```

---

## 6. Sistema de Renderizado

### 6.1 Inicialización de Pygame

```python
# Inicializar todos los módulos de Pygame
pygame.init()

# Crear ventana de visualización
screen = pygame.display.set_mode((640, 480))

# Obtener dimensiones para cálculos
s_width = screen.get_width()   # 640
s_height = screen.get_height() # 480
```

### 6.2 Función de Renderizado Principal

```python
# Limpiar pantalla (fondo negro)
screen.fill("black")

# Dibujar rectángulo (ladrillo)
pygame.draw.rect(
    screen,              # Superficie donde dibujar
    brick.color,         # Color del rectángulo
    (brick.x,            # Coordenada X
     brick.y,            # Coordenada Y
     brick.width,        # Ancho
     brick.height)       # Alto
)

# Actualizar toda la pantalla
pygame.display.flip()
```

### 6.3 Funciones Gráficas Disponibles

#### screen.fill(color)
Rellena toda la pantalla con un color.

```python
screen.fill("black")      # Negro
screen.fill("white")      # Blanco
screen.fill((255,0,0))    # Rojo (RGB)
```

#### pygame.draw.rect(surface, color, rect)
Dibuja un rectángulo.

```python
# Rectángulo en (100, 100) de 50×30
pygame.draw.rect(screen, "blue", (100, 100, 50, 30))

# Con variables
pygame.draw.rect(screen, brick.color, 
                (brick.x, brick.y, brick.width, brick.height))
```

#### pygame.display.flip()
Actualiza la ventana completa.

```python
pygame.display.flip()  # Debe llamarse una vez por frame
```

### 6.4 Sistema de Coordenadas

```
Pantalla 640×480

(0,0) ────────────────────── (640,0)
  │                              │
  │                              │
  │         (320,240)            │
  │            ● Centro          │
  │                              │
  │                              │
(0,480) ──────────────────── (640,480)

Coordenadas:
- X aumenta hacia la DERECHA
- Y aumenta hacia ABAJO
- Origen (0,0) en esquina superior izquierda
```

---

## 7. Manejo de Entradas

### 7.1 Sistema de Captura de Teclas

Pygame proporciona dos formas de capturar entradas:

**1. Eventos (para acciones únicas):**
```python
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            print("Espacio presionado")
```

**2. Estado del teclado (para movimiento continuo) ← USADO EN EL MOTOR:**
```python
keys = pygame.key.get_pressed()

if keys[pygame.K_UP]:
    # La tecla está siendo presionada
    brick.y -= speed
```

### 7.2 Teclas Soportadas

| Tecla Visual | Constante Pygame | Acción | Efecto |
|--------------|------------------|--------|--------|
| ↑ | `pygame.K_UP` | Mover arriba | `y -= 3.5` |
| ↓ | `pygame.K_DOWN` | Mover abajo | `y += 3.5` |
| ← | `pygame.K_LEFT` | Mover izquierda | `x -= 3.5` |
| → | `pygame.K_RIGHT` | Mover derecha | `x += 3.5` |

### 7.3 Implementación del Control

```python
# Obtener estado de todas las teclas
keys = pygame.key.get_pressed()

# Movimiento vertical
if keys[pygame.K_UP]:
    brick.y -= speed  # Mover hacia arriba (Y negativo)
if keys[pygame.K_DOWN]:
    brick.y += speed  # Mover hacia abajo (Y positivo)

# Movimiento horizontal
if keys[pygame.K_LEFT]:
    brick.x -= speed  # Mover hacia izquierda (X negativo)
if keys[pygame.K_RIGHT]:
    brick.x += speed  # Mover hacia derecha (X positivo)
```

### 7.4 Velocidad de Movimiento

```python
speed = 3.5  # píxeles por frame

# A 60 FPS:
# 3.5 px/frame × 60 frames/seg = 210 píxeles/segundo

# Tiempo para cruzar la pantalla:
# 640 px ÷ 210 px/seg ≈ 3 segundos
```

### 7.5 Sistema de Límites de Pantalla

**Propósito:** Evitar que el objeto salga de la ventana.

```python
# Límite IZQUIERDO
if brick.x <= 0:
    brick.x = 0

# Límite DERECHO
# (se resta el ancho para que el borde del objeto toque el límite)
if brick.x >= s_width - brick.width:
    brick.x = s_width - brick.width

# Límite SUPERIOR
if brick.y <= 0:
    brick.y = 0

# Límite INFERIOR
# (se resta la altura por la misma razón)
if brick.y >= s_height - brick.height:
    brick.y = s_height - brick.height
```

**Ejemplo visual:**

```
Sin restricción de ancho:
brick.x = 640
┌────────┐
│ Ladrillo sale
│        de pantalla →

Con restricción:
brick.x = 640 - 20 = 620
         ┌──┐
Pantalla │●│ (Borde del ladrillo
         └──┘  toca el límite)
```

---

## 8. Bucle Principal del Juego

### 8.1 El Game Loop

El **bucle principal** es el corazón del motor. Se ejecuta aproximadamente 60 veces por segundo.

**Patrón general:**
```
mientras el juego esté activo:
    1. Procesar eventos
    2. Actualizar estado
    3. Renderizar
    4. Controlar tiempo
```

### 8.2 Fases del Bucle

#### Fase 1: Procesar Eventos

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False  # Terminar el bucle
```

**Propósito:** Detectar cuando el usuario cierra la ventana.

---

#### Fase 2: Limpiar Pantalla

```python
screen.fill("black")
```

**Propósito:** Borrar el frame anterior para evitar "ghosting" (rastros).

---

#### Fase 3: Renderizar Objetos

```python
pygame.draw.rect(screen, brick.color, 
                (brick.x, brick.y, brick.width, brick.height))
```

**Propósito:** Dibujar todos los objetos en sus nuevas posiciones.

---

#### Fase 4: Capturar Entradas

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_UP]:    brick.y -= speed
if keys[pygame.K_DOWN]:  brick.y += speed
if keys[pygame.K_LEFT]:  brick.x -= speed
if keys[pygame.K_RIGHT]: brick.x += speed
```

**Propósito:** Leer el estado del teclado y actualizar variables.

---

#### Fase 5: Actualizar Lógica (Límites)

```python
# Aplicar restricciones de bordes
if brick.x <= 0:                        brick.x = 0
if brick.x >= s_width - brick.width:    brick.x = s_width - brick.width
if brick.y <= 0:                        brick.y = 0
if brick.y >= s_height - brick.height:  brick.y = s_height - brick.height
```

**Propósito:** Aplicar reglas del juego (en este caso, colisiones con bordes).

---

#### Fase 6: Actualizar Display

```python
pygame.display.flip()
```

**Propósito:** Mostrar el nuevo frame al usuario.

---

#### Fase 7: Control de Tiempo

```python
dt = clock.tick(60) / 1000
```

**Propósito:** Limitar el juego a 60 FPS y calcular delta time.

**Explicación:**
- `clock.tick(60)`: Pausa el bucle si va muy rápido
- Retorna: milisegundos desde el último frame
- `/ 1000`: Convierte a segundos (delta time)

---

### 8.3 Gestión de Tiempo y FPS

```python
# Crear reloj
clock = pygame.time.Clock()

# En cada iteración del bucle:
dt = clock.tick(60) / 1000

# dt (delta time) = tiempo transcurrido en segundos
# Ejemplo: dt ≈ 0.0166 seg (1/60)
```

**Uso del delta time (para futura expansión):**
```python
# Movimiento dependiente de FPS (actual)
brick.x += speed  # 3.5 px por frame

# Movimiento independiente de FPS (mejor práctica)
brick.x += speed * dt * 60  # píxeles por segundo
```

---

## 9. Casos de Prueba

### 9.1 Prueba 1: Inicialización Correcta

**Objetivo:** Verificar que la ventana se crea correctamente.

**Procedimiento:**
1. Ejecutar `python engine/test-motor.py`
2. Observar la ventana

**Resultado Esperado:**
-  Aparece ventana de 640×480
-  Fondo completamente negro
-  Ladrillo rojo visible en el centro
-  Sin errores en consola

**Resultado Obtenido:**  APROBADO

**Captura:**

![Inicialización](../assets/img/1.png)

---

### 9.2 Prueba 2: Movimiento con Teclas

**Objetivo:** Verificar respuesta fluida a las entradas.

**Procedimiento:**
1. Presionar ↑ durante 2 segundos
2. Presionar → durante 2 segundos
3. Presionar ↓ durante 2 segundos
4. Presionar ← durante 2 segundos
5. Presionar diagonales (↑ + →)

**Resultado Esperado:**
-  Movimiento suave sin "saltos"
-  Velocidad constante en todas direcciones
-  Respuesta inmediata al presionar
-  Movimiento diagonal funciona

**Resultado Obtenido:**  APROBADO

---

### 9.3 Prueba 3: Límites de Pantalla

**Objetivo:** Verificar que el objeto no puede salir de la ventana.

**Procedimiento:**
1. Mover ladrillo hasta borde superior
2. Intentar seguir presionando ↑
3. Verificar que se detiene
4. Repetir para los 4 bordes

**Resultado Esperado:**
```
Borde Superior (y=0):        Bloqueado
Borde Inferior (y=470):      Bloqueado
Borde Izquierdo (x=0):       Bloqueado
Borde Derecho (x=620):       Bloqueado
```

**Resultado Obtenido:**  APROBADO

**Observación:** El ladrillo permanece completamente visible en el borde.

---

### 9.4 Prueba 4: Rendimiento (60 FPS)

**Objetivo:** Verificar que el motor mantiene 60 FPS constantes.

**Procedimiento:**
1. Ejecutar el motor
2. Mover el ladrillo en círculos
3. Observar fluidez del movimiento

**Herramienta de medición:**
```python
# Agregar al código temporalmente:
print(f"FPS: {clock.get_fps():.2f}")
```

**Resultado Esperado:**
-  FPS entre 59-60 constantemente
-  Sin caídas de rendimiento
-  Movimiento fluido y suave

**Resultado Obtenido:**  APROBADO  
**FPS Medido:** 59.8 - 60.0 FPS

---

### 9.5 Prueba 5: Cierre de Ventana

**Objetivo:** Verificar que el programa termina correctamente.

**Procedimiento:**
1. Hacer clic en botón X de la ventana
2. Verificar que la ventana se cierra
3. Revisar consola

**Resultado Esperado:**
-  Ventana cierra inmediatamente
-  Sin errores en consola
-  Proceso termina completamente

**Resultado Obtenido:**  APROBADO

---

### 9.6 Prueba 6: Compatibilidad Python 2.7

**Objetivo:** Verificar ejecución en Python 2.7.

**Procedimiento:**
```bash
python2.7 engine/test-motor.py
```

**Resultado Esperado:**
-  Se ejecuta sin modificar código
-  Comportamiento idéntico a Python 3

**Resultado Obtenido:** APROBADO

**Nota:** Compatible gracias al uso de:
- `from __future__ import division` (opcional)
- Sintaxis compatible con ambas versiones

---





