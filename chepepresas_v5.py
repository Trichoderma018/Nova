"""
╔══════════════════════════════════════════════════════╗
║           CHEPEPRESAS 🚗💨                       ║
║   Scroll con ImagenBase1.png + ImagenBase2.png       ║
║   Carros bajando suavemente por los carriles         ║
╚══════════════════════════════════════════════════════╝

Controles:
  ← → ↑ ↓  : Mover el carro (también WASD)
  ESPACIO   : Saltar
  Z         : Encender radio
  X         : Cambiar emisora
  C         : Apagar radio
  R         : Reiniciar después de Game Over
  ESC       : Salir

Requisitos:
  pip install pygame

Estructura de archivos:
  chepepresas_v5_final.py   este archivo
  ImagenBase1.png           misma carpeta
  ImagenBase2.png           misma carpeta
  icono_ebrio.png           misma carpeta
  ImagenesBase3Noche.png         misma carpera
  ImagenesBase4Noche.png         misma carpera
  ImagenesBase5Tarde.png         misma carpera
  ImagenesBase6Tarde.png         misma carpera
  Radios/                   carpeta con subcarpetas de estaciones (mp3)
"""

#region Importacion de librerias
import pygame       # Motor grafico y de audio para el juego
import random       # Generacion de numeros aleatorios (spawn, colores, zigzag)
import sys          # Para cerrar el proceso del juego limpiamente
import os           # Manejo de rutas de archivos e imagenes
import math         # Funciones matematicas (seno para el zigzag)
#endregion

#region Constantes de pantalla y juego
ANCHO  = 480        # Ancho de la ventana del juego en pixeles
ALTO   = 750        # Alto de la ventana del juego en pixeles
FPS    = 60         # Cuadros por segundo del bucle principal
TITULO = "CHEPEPRESAS v5"  # Titulo de la ventana
#endregion

#region Paleta de colores (tuplas RGB)
NEGRO    = (  0,   0,   0)
BLANCO   = (255, 255, 255)
ROJO     = (220,  50,  50)
AMARILLO = (255, 220,   0)
VERDE_CR = ( 14, 130,  60)   # Verde inspirado en la bandera de Costa Rica
NARANJA  = (255, 140,   0)
CELESTE  = (150, 210, 255)
#endregion

#region Constantes de carriles y limites de la carretera
CARRILES_X = [155, 223, 314]  # Posiciones X centrales de los 3 carriles
LIMITE_IZQ = 120              # Borde izquierdo de la carretera
LIMITE_DER = 360              # Borde derecho de la carretera
#endregion

#region Posiciones verticales clave
Y_APARICION = -80    # Posicion Y donde aparecen los enemigos (fuera de pantalla arriba)
Y_JUGADOR   = 610    # Posicion Y inicial del jugador
Y_FUERA     = 700    # Posicion Y donde un enemigo se considera fuera de pantalla
#endregion

#region Limites verticales de movimiento del jugador
LIMITE_SUP = 80      # Limite superior de movimiento del jugador
LIMITE_INF = 690     # Limite inferior de movimiento del jugador
#endregion

#region Dimensiones y escala del carro
ESCALA_FIJA = 1.0    # Escala fija (sin perspectiva dinamica)
CARRO_ANCHO = 46     # Ancho base del carro en pixeles
CARRO_ALTO  = 76     # Alto base del carro en pixeles
#endregion

#region Constantes de velocidad y aparicion de enemigos
VEL_BASE  = 2.0      # Velocidad base del juego al inicio
VEL_MAX   = 9.0      # Velocidad maxima que puede alcanzar el juego
INTV_BASE = 105      # Intervalo base entre apariciones de enemigos (en frames)
#endregion

#region Factores de velocidad
FONDO_FACTOR = 0.45  # Factor de velocidad del scroll del fondo respecto al juego

ENEMIGO_FACTOR_MIN = 1.6  # Multiplicador minimo de velocidad del enemigo
ENEMIGO_FACTOR_MAX = 2.4  # Multiplicador maximo de velocidad del enemigo
#endregion

#region Colores disponibles para los carros enemigos
COLORES_ENEMIGO = [
    (  0, 100, 200), (160, 160,   0), ( 40, 160,  70),
    (160,  50, 160), (220, 110,   0), ( 60, 170, 170),
    (150,  40,  40), ( 60,  60, 160), (200,  90,  50),
]
#endregion


#region Funcion de escala
def obtener_escala(y):
    """Retorna la escala visual segun la posicion Y (fija en esta version)"""
    return ESCALA_FIJA
#endregion


#region Carga de imagenes desde disco
def cargar_imagen(nombre):
    """Carga una imagen desde la carpeta del script y la escala al tamaño de la ventana"""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre)
    if os.path.exists(ruta):
        img = pygame.image.load(ruta).convert()
        img = pygame.transform.scale(img, (ANCHO, ALTO))
        print(f"OK {nombre}")
        return img
    print(f"No encontrada: {nombre}")
    return None
#endregion


#region Fondo de respaldo generado por codigo
def fondo_procedural():
    """Genera un fondo de carretera basico si no se encuentran las imagenes"""
    superficie = pygame.Surface((ANCHO, ALTO))
    superficie.fill((80, 160, 60))  # Pasto verde de fondo
    # Rectangulo gris que representa la carretera
    pygame.draw.rect(superficie, (65, 65, 70),
                     (LIMITE_IZQ - 10, 0, LIMITE_DER - LIMITE_IZQ + 20, ALTO))
    # Lineas divisorias blancas entre carriles
    for y in range(0, ALTO, 50):
        medio_x1 = (CARRILES_X[0] + CARRILES_X[1]) // 2
        medio_x2 = (CARRILES_X[1] + CARRILES_X[2]) // 2
        pygame.draw.rect(superficie, BLANCO, (medio_x1 - 2, y, 4, 28))
        pygame.draw.rect(superficie, BLANCO, (medio_x2 - 2, y, 4, 28))
    return superficie
#endregion


#region Clase para el scroll infinito del fondo
class DesplazamientoFondo:
    """Maneja el desplazamiento vertical infinito del fondo y el cambio de escenario segun puntaje"""
    def __init__(self, fondos):
        self.fondos = fondos                          # Diccionario {puntaje_minimo: imagen}
        self.actual = fondos[min(fondos.keys())]      # Fondo activo al inicio
        self.desplazamiento = 0.0                     # Offset vertical del scroll

    def actualizar(self, vel, puntaje):
        """Avanza el scroll y selecciona el fondo correspondiente al puntaje"""
        self.desplazamiento += vel
        if self.desplazamiento >= ALTO:
            self.desplazamiento -= ALTO
        # elegir fondo según puntaje
        for limite in sorted(self.fondos.keys()):
            if puntaje >= limite:
                self.actual = self.fondos[limite]

    def dibujar(self, superficie):
        """Dibuja dos copias del fondo para lograr el efecto de scroll infinito"""
        despl = int(self.desplazamiento)
        superficie.blit(self.actual, (0, despl))
        superficie.blit(self.actual, (0, despl - ALTO))
#endregion


#region Funcion para dibujar un carro (jugador o enemigo)
def dibujar_carro(superficie, cx, cy, esc, color, es_jugador=False):
    """Dibuja un carro rectangullar con detalles: ventanas, llantas, luces"""
    ancho = max(6,  int(CARRO_ANCHO * esc))
    alto  = max(10, int(CARRO_ALTO * esc))
    cx, cy = int(cx), int(cy)
    color_oscuro = tuple(max(c - 55, 0) for c in color)  # Version oscura del color para el cuerpo
    radio_borde  = max(2, int(7 * esc))

    # Cuerpo principal del carro
    pygame.draw.rect(superficie, color, (cx-ancho//2, cy-alto//2, ancho, alto), border_radius=radio_borde)
    # Parte interna mas oscura (techo/capota)
    pygame.draw.rect(superficie, color_oscuro,
                     (cx-ancho//2+max(1,int(4*esc)), cy-alto//2+max(1,int(9*esc)),
                      ancho-max(2,int(8*esc)), alto-max(4,int(22*esc))),
                     border_radius=max(1, int(5*esc)))
    # Ventana delantera (parabrisas)
    pygame.draw.rect(superficie, CELESTE,
                     (cx-ancho//2+max(1,int(5*esc)), cy-alto//2+max(1,int(5*esc)),
                      ancho-max(2,int(10*esc)), max(3, int(14*esc))),
                     border_radius=max(1, int(3*esc)))
    # Ventana trasera
    pygame.draw.rect(superficie, CELESTE,
                     (cx-ancho//2+max(1,int(5*esc)), cy+alto//2-max(3,int(20*esc)),
                      ancho-max(2,int(10*esc)), max(2, int(12*esc))),
                     border_radius=max(1, int(3*esc)))

    # Llantas (4 esquinas del carro)
    ancho_llanta = max(2, int(8*esc))
    alto_llanta  = max(3, int(15*esc))
    for rx, ry in [
        (-ancho//2-max(1,int(4*esc)), -alto//2+max(1,int(5*esc))),   # Delantera izquierda
        ( ancho//2-max(1,int(4*esc)), -alto//2+max(1,int(5*esc))),   # Delantera derecha
        (-ancho//2-max(1,int(4*esc)),  alto//2-max(3,int(20*esc))),  # Trasera izquierda
        ( ancho//2-max(1,int(4*esc)),  alto//2-max(3,int(20*esc))),  # Trasera derecha
    ]:
        pygame.draw.rect(superficie, NEGRO, (cx+rx, cy+ry, ancho_llanta, alto_llanta),
                         border_radius=max(1, int(3*esc)))

    # Faros delanteros (circulitos amarillos)
    radio_faro = max(1, int(4*esc))
    pygame.draw.circle(superficie, AMARILLO,
                       (cx-ancho//2+max(1,int(7*esc)), cy-alto//2+max(1,int(4*esc))), radio_faro)
    pygame.draw.circle(superficie, AMARILLO,
                       (cx+ancho//2-max(1,int(7*esc)), cy-alto//2+max(1,int(4*esc))), radio_faro)

    if es_jugador:
        # Placa trasera del jugador (rectangulo amarillo)
        ancho_placa = max(4, int(20*esc))
        alto_placa  = max(2, int(6*esc))
        pygame.draw.rect(superficie, AMARILLO,
                         (cx-ancho_placa//2, cy+alto//2-max(2,int(11*esc)), ancho_placa, alto_placa),
                         border_radius=1)
    else:
        # Luces traseras del enemigo (circulitos rojos)
        radio_luz = max(1, int(4*esc))
        pygame.draw.circle(superficie, ROJO,
                           (cx-ancho//2+max(1,int(6*esc)), cy+alto//2-max(1,int(5*esc))), radio_luz)
        pygame.draw.circle(superficie, ROJO,
                           (cx+ancho//2-max(1,int(6*esc)), cy+alto//2-max(1,int(5*esc))), radio_luz)
#endregion


# ─────────────────────────────────────────────
#  SISTEMA DE RADIO
# ─────────────────────────────────────────────
#region Clase del sistema de radio del juego
class SistemaRadio:
    """Maneja la reproduccion de musica en el juego, con multiples estaciones"""
    def __init__(self):
        self.encendida = False                # Estado de la radio (encendida/apagada)
        self.indice_estacion_actual = 0       # Indice de la estacion seleccionada
        self.nombre_estaciones = []           # Lista con los nombres de las estaciones
        self.mp3_por_estacion = []            # Lista de listas con rutas de mp3 por estacion
        self.indice_mp3_actual = 0            # Indice de la cancion actual dentro de la estacion
        self._cargar_estaciones()

    def _cargar_estaciones(self):
        """Busca carpetas de estaciones dentro de la carpeta Radios/ y carga las canciones"""
        carpeta_mp3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Radios")
        if not os.path.isdir(carpeta_mp3):
            self.nombre_estaciones = []
            self.mp3_por_estacion = []
            return

        # Buscar subcarpetas (cada una es una estacion)
        carpeta_estaciones = sorted(
            [d for d in os.listdir(carpeta_mp3) if os.path.isdir(os.path.join(carpeta_mp3, d))]
        )

        if carpeta_estaciones:
            self.nombre_estaciones = carpeta_estaciones
            audios_mp3 = []
            for carpeta in carpeta_estaciones:
                ruta_carpeta = os.path.join(carpeta_mp3, carpeta)
                archivos_mp3 = sorted(
                    [os.path.join(ruta_carpeta, f) for f in os.listdir(ruta_carpeta)
                     if f.lower().endswith(".mp3")]
                )
                audios_mp3.append(archivos_mp3)
            self.mp3_por_estacion = audios_mp3
        else:
            # Si no hay subcarpetas, agrupar todos los mp3 sueltos en una sola estacion
            archivos_mp3 = sorted(
                [os.path.join(carpeta_mp3, f) for f in os.listdir(carpeta_mp3)
                 if f.lower().endswith(".mp3")]
            )
            if archivos_mp3:
                self.nombre_estaciones = ["Todas"]
                self.mp3_por_estacion = [archivos_mp3]
            else:
                self.nombre_estaciones = []
                self.mp3_por_estacion = []

    def tiene_contenido(self):
        """Verifica si hay al menos una estacion con canciones disponibles"""
        return bool(self.nombre_estaciones) and any(self.mp3_por_estacion)

    def _escoger_mp3(self):
        """Selecciona la ruta del mp3 actual segun estacion e indice"""
        if self.indice_estacion_actual >= len(self.mp3_por_estacion):
            return None
        canciones_estacion = self.mp3_por_estacion[self.indice_estacion_actual]
        if not canciones_estacion:
            return None
        self.indice_mp3_actual = self.indice_mp3_actual % len(canciones_estacion)
        return canciones_estacion[self.indice_mp3_actual]

    def encender(self):
        """Enciende la radio y comienza a reproducir la estacion actual"""
        if not self.tiene_contenido() or self.encendida:
            return
        self.encendida = True
        self._reproducir_actual()

    def apagar(self):
        """Apaga la radio y detiene la musica"""
        self.encendida = False
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def siguiente_estacion(self):
        """Cambia a la siguiente estacion de radio"""
        if not self.tiene_contenido():
            return
        self.indice_estacion_actual = (self.indice_estacion_actual + 1) % len(self.nombre_estaciones)
        self.indice_mp3_actual = 0
        if self.encendida:
            self._reproducir_actual()

    def _reproducir_actual(self):
        """Carga y reproduce la cancion actual en loop infinito"""
        pista = self._escoger_mp3()
        if not pista:
            return
        try:
            pygame.mixer.music.load(pista)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def actualizar(self):
        """Revisa si la musica sigue sonando, si no la reinicia"""
        if not self.encendida:
            return
        try:
            if not pygame.mixer.music.get_busy():
                self._reproducir_actual()
        except Exception:
            pass
#endregion


# ─────────────────────────────────────────────
#  JUGADOR (con controles invertidos)
# ─────────────────────────────────────────────
#region Clase del jugador
class Jugador:
    """Clase del carro del jugador con movimiento, salto y sistema de confusion de controles"""
    VEL_MAX_MOV = 5.0    # Velocidad maxima de movimiento en cualquier eje
    ACELERACION = 0.4    # Aceleracion al presionar una tecla de direccion
    FRICCION    = 0.3    # Desaceleracion gradual cuando no se presiona ninguna tecla

    def __init__(self):
        self.x   = float(CARRILES_X[1])    # Posicion X inicial (carril del centro)
        self.y   = float(Y_JUGADOR)        # Posicion Y inicial
        self.esc = obtener_escala(self.y)   # Escala visual del carro
        self.vel_x     = 0.0               # Velocidad horizontal actual
        self.vel_y_mov = 0.0               # Velocidad vertical actual

        # Variables del sistema de salto
        self.saltando      = False         # Indica si esta en el aire
        self.salto_offset  = 0.0           # Desplazamiento visual del salto
        self.vel_salto     = 0.0           # Velocidad vertical del salto
        self.gravedad      = 0.6           # Fuerza de gravedad que lo jala hacia abajo
        self.fuerza_salto  = -12           # Impulso inicial del salto (negativo = hacia arriba)

        # Controles invertidos (tu aporte)
        self.controles_invertidos = False   # Si es True los controles WASD estan al reves
        self.tiempo_confusion     = 0      # Timestamp de cuando se activo la confusion

    def activar_confusion(self):
        """Activa la inversion de controles WASD por 5 segundos al chocar con un ebrio"""
        self.controles_invertidos = True
        self.tiempo_confusion = pygame.time.get_ticks()

    def actualizar_estado(self):
        """Revisa si ya pasaron los 5 segundos de confusion para desactivarla"""
        if self.controles_invertidos:
            if pygame.time.get_ticks() - self.tiempo_confusion > 5000:
                self.controles_invertidos = False

    def _rectangulo(self):
        """Retorna el rectangulo de colision del jugador"""
        ancho = int(CARRO_ANCHO * self.esc * 1.3)
        alto  = int(CARRO_ALTO * self.esc * 1.1)
        return pygame.Rect(int(self.x) - ancho // 2, int(self.y) - alto // 2, ancho, alto)

    def _aplicar_friccion(self, vel):
        """Aplica desaceleracion gradual a una velocidad dada"""
        if abs(vel) < self.FRICCION:
            return 0.0
        return vel - self.FRICCION if vel > 0 else vel + self.FRICCION

    def mover(self, teclas):
        """Procesa las teclas presionadas y mueve al jugador respetando los limites"""
        self.actualizar_estado()

        mitad_ancho = int(CARRO_ANCHO * self.esc) // 2
        mitad_alto  = int(CARRO_ALTO * self.esc) // 2

        # Controles normales o invertidos
        if self.controles_invertidos:
            # WASD invertidos, flechas normales
            izq    = teclas[pygame.K_LEFT] or teclas[pygame.K_d]
            der    = teclas[pygame.K_RIGHT] or teclas[pygame.K_a]
            arriba = teclas[pygame.K_UP] or teclas[pygame.K_s]
            abajo  = teclas[pygame.K_DOWN] or teclas[pygame.K_w]
        else:
            # WASD normales + flechas normales
            izq    = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
            der    = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]
            arriba = teclas[pygame.K_UP] or teclas[pygame.K_w]
            abajo  = teclas[pygame.K_DOWN] or teclas[pygame.K_s]

        # Eje X (movimiento horizontal)
        if izq and not der:
            self.vel_x = max(-self.VEL_MAX_MOV, self.vel_x - self.ACELERACION)
        elif der and not izq:
            self.vel_x = min( self.VEL_MAX_MOV, self.vel_x + self.ACELERACION)
        else:
            self.vel_x = self._aplicar_friccion(self.vel_x)

        self.x += self.vel_x
        # Restringir al jugador dentro de los limites de la carretera
        if self.x - mitad_ancho < LIMITE_IZQ:
            self.x = LIMITE_IZQ + mitad_ancho; self.vel_x = 0
        if self.x + mitad_ancho > LIMITE_DER:
            self.x = LIMITE_DER - mitad_ancho; self.vel_x = 0

        # Eje Y (movimiento vertical)
        if arriba and not abajo:
            self.vel_y_mov = max(-self.VEL_MAX_MOV, self.vel_y_mov - self.ACELERACION)
        elif abajo and not arriba:
            self.vel_y_mov = min( self.VEL_MAX_MOV, self.vel_y_mov + self.ACELERACION)
        else:
            self.vel_y_mov = self._aplicar_friccion(self.vel_y_mov)

        nueva_y = self.y + self.vel_y_mov
        # Restringir al jugador dentro de los limites verticales
        if nueva_y - mitad_alto < LIMITE_SUP:
            nueva_y = LIMITE_SUP + mitad_alto; self.vel_y_mov = 0.0
        elif nueva_y + mitad_alto > LIMITE_INF:
            nueva_y = LIMITE_INF - mitad_alto; self.vel_y_mov = 0.0
        self.y = nueva_y

    def saltar(self):
        """Inicia un salto si el jugador no esta en el aire ni confundido"""
        if self.controles_invertidos:
            return
        if not self.saltando:
            self.saltando     = True
            self.salto_offset = 0.0
            self.vel_salto    = self.fuerza_salto

    def actualizar(self):
        """Actualiza la fisica del salto (gravedad y aterrizaje)"""
        if self.saltando:
            self.salto_offset += self.vel_salto
            self.vel_salto    += self.gravedad
            if self.salto_offset >= 0.0:
                self.salto_offset = 0.0
                self.saltando     = False
                self.vel_salto    = 0.0

    def dibujar(self, superficie):
        """Dibuja el carro del jugador en pantalla con efecto de salto"""
        visual_y = self.y + self.salto_offset
        esc = self.esc * 1.15 if self.saltando else self.esc
        dibujar_carro(superficie, self.x, visual_y, esc, ROJO, es_jugador=True)

    def colisiona_con(self, enemigo):
        """Verifica si el rectangulo del jugador se superpone con el del enemigo"""
        return self._rectangulo().colliderect(enemigo.rectangulo())
#endregion


# ─────────────────────────────────────────────
#  ENEMIGO (con zigzag)
# ─────────────────────────────────────────────
#region Clase del carro enemigo
class Enemigo:
    """Carro enemigo que baja por la carretera, puede hacer zigzag si es ebrio"""
    def __init__(self, vel_juego, icono):
        self.icono   = icono                                     # Icono del ebrio para enemigos zigzag
        self.carril  = random.randint(0, 2)                      # Carril aleatorio (0, 1 o 2)
        self.x       = float(CARRILES_X[self.carril])            # Posicion X segun el carril
        self.y       = float(Y_APARICION)                        # Posicion Y inicial (fuera de pantalla)
        self.color   = random.choice(COLORES_ENEMIGO)            # Color aleatorio del carro
        self._factor = random.uniform(ENEMIGO_FACTOR_MIN, ENEMIGO_FACTOR_MAX)  # Multiplicador de velocidad
        self.vel     = vel_juego * self._factor                  # Velocidad resultante

        # Parametros del movimiento zigzag (solo el 30% de enemigos lo tienen)
        self.zigzag          = random.random() < 0.3             # Si es True, se mueve en zigzag
        self.zigzag_amplitud = random.uniform(30, 70)            # Amplitud del zigzag en pixeles
        self.zigzag_frec     = random.uniform(0.10, 0.10)        # Frecuencia del zigzag
        self.t               = 0                                 # Contador de frames para el seno
        self.base_x          = self.x                            # Posicion X base para el zigzag

    def actualizar(self, vel_juego):
        """Mueve al enemigo hacia abajo y aplica zigzag si corresponde"""
        self.vel  = vel_juego * self._factor
        self.y   += self.vel
        self.t   += 1

        if self.zigzag:
            # Calcula desplazamiento lateral con funcion seno
            desplazamiento = self.zigzag_amplitud * math.sin(self.t * self.zigzag_frec)
            self.x = self.base_x + desplazamiento
            # Mantener dentro de los limites de la carretera
            if self.x < LIMITE_IZQ:
                self.x = LIMITE_IZQ
            elif self.x > LIMITE_DER:
                self.x = LIMITE_DER

    def escala(self):
        """Retorna la escala visual del enemigo"""
        return obtener_escala(self.y)

    def rectangulo(self):
        """Retorna el rectangulo de colision del enemigo"""
        e = self.escala()
        ancho = int(CARRO_ANCHO * e * 1.3)
        alto  = int(CARRO_ALTO * e * 1.3)
        return pygame.Rect(int(self.x)-ancho//2, int(self.y)-alto//2, ancho, alto)

    def fuera(self):
        """Verifica si el enemigo ya salio por debajo de la pantalla"""
        return self.y > Y_FUERA

    def dibujar(self, superficie):
        """Dibuja el carro enemigo y el icono de ebrio si hace zigzag"""
        if self.y >= -CARRO_ALTO:
            dibujar_carro(superficie, self.x, self.y, self.escala(), self.color)

            # Si es ebrio, dibujar el icono flotando al lado del carro
            if self.zigzag:
                despl_y = math.sin(self.t * 0.1) * 6
                lado    = math.sin(self.t * 0.05)
                x_icono = self.x + 1 if lado > 0 else self.x - 1 - self.icono.get_width()
                superficie.blit(
                    self.icono,
                    (int(x_icono), int(self.y - self.icono.get_height() // 2 + despl_y))
                )
#endregion


#region Clase de particulas de explosion
class Particula:
    """Particula individual del efecto de explosion al chocar"""
    def __init__(self, x, y):
        self.x     = x + random.uniform(-25, 25)    # Posicion X con dispersion aleatoria
        self.y     = y + random.uniform(-25, 25)    # Posicion Y con dispersion aleatoria
        self.vx    = random.uniform(-5, 5)           # Velocidad horizontal aleatoria
        self.vy    = random.uniform(-8, 2)           # Velocidad vertical aleatoria
        self.vida  = random.randint(25, 55)          # Frames de vida restantes
        self.radio = random.randint(3, 10)           # Tamaño del circulo
        self.color = random.choice([ROJO, AMARILLO, NARANJA, BLANCO])  # Color aleatorio

    def actualizar(self):
        """Mueve la particula y aplica gravedad"""
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.3      # Gravedad que jala la particula hacia abajo
        self.vida -= 1

    def dibujar(self, superficie):
        """Dibuja la particula como un circulo en pantalla"""
        pygame.draw.circle(superficie, self.color,
                           (int(self.x), int(self.y)), max(1, self.radio))

    def muerta(self):
        """Retorna True si la particula ya no tiene vida"""
        return self.vida <= 0
#endregion


#region Funcion para dibujar el HUD (interfaz de usuario en pantalla)
def dibujar_hud(superficie, fuente, puntaje, velocidad, vidas, radio):
    """Dibuja la barra superior con puntaje, velocidad, vidas y el indicador de radio"""
    # Barra semi-transparente en la parte superior
    barra_hud = pygame.Surface((ANCHO, 50), pygame.SRCALPHA)
    barra_hud.fill((0, 0, 0, 160))
    superficie.blit(barra_hud, (0, 0))

    # Puntaje a la izquierda
    superficie.blit(fuente.render(f"PUNTAJE: {puntaje:05d}", True, AMARILLO), (10, 13))

    # Velocimetro a la derecha (conversion ficticia a km/h)
    km  = int(80 + velocidad * 12)
    texto_vel = fuente.render(f"{km} km/h", True, BLANCO)
    superficie.blit(texto_vel, (ANCHO - texto_vel.get_width() - 10, 13))

    # Vidas al centro
    texto_vidas = fuente.render(f"VIDAS: {vidas}", True, ROJO)
    superficie.blit(texto_vidas, (ANCHO//2 - texto_vidas.get_width()//2, 13))

    # Indicador de radio encendida
    if radio.encendida and radio.nombre_estaciones:
        nombre = radio.nombre_estaciones[radio.indice_estacion_actual]
        texto_radio = fuente.render(f"📻 {nombre}", True, CELESTE)
        superficie.blit(texto_radio, (10, ALTO - 30))
#endregion


#region Pantalla de Game Over
def dibujar_game_over(superficie, fuente_grande, fuente, puntaje):
    """Dibuja la pantalla de fin de juego con puntaje y opciones"""
    # Overlay oscuro semi-transparente
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    superficie.blit(overlay, (0, 0))
    cx = ANCHO // 2
    # Textos centrados
    for tipo_fuente, texto, color, y in [
        (fuente_grande, "PRESA!",                    ROJO,          ALTO//2 - 90),
        (fuente,        "Chocaste en el Coyol",      BLANCO,        ALTO//2 - 20),
        (fuente,        f"Puntaje: {puntaje:05d}",   AMARILLO,      ALTO//2 + 25),
        (fuente,        "[ R ] Reiniciar",           VERDE_CR,      ALTO//2 + 70),
        (fuente,        "[ ESC ] Salir",             (160,160,160), ALTO//2 +105),
    ]:
        superficie_texto = tipo_fuente.render(texto, True, color)
        superficie.blit(superficie_texto, superficie_texto.get_rect(center=(cx, y)))
#endregion


#region Pantalla de inicio
def dibujar_inicio(superficie, fuente_grande, fuente, fuente_chica):
    """Dibuja la pantalla de bienvenida con instrucciones de juego"""
    # Overlay oscuro semi-transparente
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    superficie.blit(overlay, (0, 0))
    cx = ANCHO // 2
    # Textos centrados con instrucciones
    for tipo_fuente, texto, color, y in [
        (fuente_grande, "CHEPEPRESAS",                 VERDE_CR,      ALTO//2 - 160),
        (fuente,        "Sobrevivi el trafico",         AMARILLO,      ALTO//2 -  90),
        (fuente,        "josefino...",                  AMARILLO,      ALTO//2 -  58),
        (fuente_chica,  "WASD / Flechas para moverse",  BLANCO,        ALTO//2 +   5),
        (fuente_chica,  "ESPACIO para saltar",          BLANCO,        ALTO//2 +  35),
        (fuente_chica,  "Z encender radio | X cambiar | C apagar", (200,200,200), ALTO//2 +  63),
        (fuente_chica,  "Evita los carros y no te quedes en presa", (200,200,200), ALTO//2 +  91),
        (fuente,        "[ ESPACIO ] para iniciar",     AMARILLO,      ALTO//2 + 135),
    ]:
        superficie_texto = tipo_fuente.render(texto, True, color)
        superficie.blit(superficie_texto, superficie_texto.get_rect(center=(cx, y)))
#endregion


#region Carga de fondos segun puntaje
def cargar_fondos():
    """Carga las imagenes de fondo asociadas a rangos de puntaje"""
    archivos_imagenes = {
        0:    "ImagenBase1.png",          # Fondo dia (puntaje 0+)
        500:  "ImagenesBase5Tarde.png",   # Fondo tarde (puntaje 500+)
        1000: "ImagenesBase3Noche.png",   # Fondo noche (puntaje 1000+)
        1500: "ImagenesBase4Noche.png",   # Fondo noche 2 (puntaje 1500+)
        2000: "ImagenesBase6Tarde.png"    # Fondo tarde 2 (puntaje 2000+)
    }
    fondos = {}
    for puntaje, nombre_archivo in archivos_imagenes.items():
        img = cargar_imagen(nombre_archivo)
        if img is not None:
            fondos[puntaje] = img
    # Si no se cargo ningun fondo, usar el procedural como respaldo
    if not fondos:
        fondos[0] = fondo_procedural()
    return fondos
#endregion


#region Funcion principal del juego
def principal():
    """Bucle principal del juego: inicializa pygame, maneja eventos, actualiza logica y dibuja"""
    pygame.init()
    pygame.display.set_caption(TITULO)
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj    = pygame.time.Clock()

    # Inicializar el mixer de audio (puede fallar si no hay dispositivo)
    try:
        pygame.mixer.init()
    except Exception:
        pass

    radio = SistemaRadio()

    # Fuentes de texto para el HUD y pantallas
    fuente_grande = pygame.font.SysFont("Arial", 54, bold=True)  # Titulos grandes
    fuente        = pygame.font.SysFont("Arial", 22, bold=True)  # Texto normal
    fuente_chica  = pygame.font.SysFont("Arial", 18)             # Texto pequeño

    # Icono para enemigos zigzag
    icono_ebrio = None
    ruta_icono = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icono_ebrio.png")
    if os.path.exists(ruta_icono):
        icono_ebrio = pygame.image.load(ruta_icono).convert_alpha()
        icono_ebrio = pygame.transform.scale(icono_ebrio, (80, 80))
    else:
        # Icono de respaldo si no existe el archivo
        icono_ebrio = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(icono_ebrio, AMARILLO, (20, 20), 18)
        fuente_tmp = pygame.font.SysFont("Arial", 22, bold=True)
        texto_tmp = fuente_tmp.render("?", True, NEGRO)
        icono_ebrio.blit(texto_tmp, (12, 8))

    # Cargar fondos y crear el objeto de scroll
    fondos = cargar_fondos()
    desplazamiento = DesplazamientoFondo(fondos)

    def reiniciar():
        """Retorna un diccionario con el estado inicial del juego"""
        return dict(
            jugador          = Jugador(),
            enemigos         = [],
            particulas       = [],
            puntaje          = 0,
            velocidad        = float(VEL_BASE),
            temporizador_aparicion = 0,
            fin_del_juego    = False,
            inicio           = True,
            enemigos_creados = 0,
            vidas            = 5,
        )

    estado = reiniciar()

    # ── BUCLE PRINCIPAL DEL JUEGO ──
    while True:
        reloj.tick(FPS)

        # ── MANEJO DE EVENTOS ──
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                # Iniciar el juego desde la pantalla de inicio
                if estado["inicio"] and evento.key == pygame.K_SPACE:
                    estado["inicio"] = False
                # Reiniciar despues de game over
                if estado["fin_del_juego"] and evento.key == pygame.K_r:
                    estado = reiniciar()
                    estado["inicio"] = False
                    radio.apagar()
                # Salto durante el juego
                if not estado["inicio"] and not estado["fin_del_juego"]:
                    if evento.key == pygame.K_SPACE:
                        estado["jugador"].saltar()
                # Controles de radio
                if evento.key == pygame.K_z:
                    radio.encender()
                elif evento.key == pygame.K_x:
                    radio.siguiente_estacion()
                elif evento.key == pygame.K_c:
                    radio.apagar()

        # ── LOGICA DEL JUEGO (solo si no esta en inicio ni game over) ──
        if not estado["inicio"] and not estado["fin_del_juego"]:
            estado["jugador"].mover(pygame.key.get_pressed())
            estado["jugador"].actualizar()
            # La velocidad aumenta gradualmente con el puntaje
            estado["velocidad"] = min(VEL_BASE + estado["puntaje"] / 600, VEL_MAX)
            vel = estado["velocidad"]

            desplazamiento.actualizar(vel * FONDO_FACTOR, estado["puntaje"])

            # Aparicion de enemigos
            estado["temporizador_aparicion"] += 1
            intervalo = max(28, int(INTV_BASE - estado["puntaje"] / 100))
            if estado["temporizador_aparicion"] >= intervalo and estado["enemigos_creados"] < 80:
                estado["temporizador_aparicion"] = 0
                # Verificar que carriles estan ocupados cerca del spawn
                ocupados = {e.carril for e in estado["enemigos"] if e.y < CARRO_ALTO * 2}
                libres   = [c for c in range(3) if c not in ocupados]
                if libres:
                    carril = random.choice(libres)
                    nuevo  = Enemigo(vel, icono_ebrio)
                    nuevo.carril = carril
                    nuevo.x      = float(CARRILES_X[carril])
                    estado["enemigos"].append(nuevo)

            # Actualizar posicion de cada enemigo
            for e in estado["enemigos"]:
                e.actualizar(vel)

            # Puntaje por enemigos esquivados (los que salen por abajo)
            vivos = []
            for e in estado["enemigos"]:
                if e.fuera():
                    estado["puntaje"] += 10
                else:
                    vivos.append(e)
            estado["enemigos"] = vivos

            # Deteccion de colisiones
            nuevos_enemigos = []
            for e in estado["enemigos"]:
                if not estado["jugador"].saltando and estado["jugador"].colisiona_con(e):
                    # Sí es zigzag → activar confusión de controles
                    if e.zigzag:
                        estado["jugador"].activar_confusion()

                    estado["vidas"] -= 1

                    # Generar particulas de explosion
                    for _ in range(80):
                        estado["particulas"].append(
                            Particula(estado["jugador"].x, estado["jugador"].y)
                        )

                    if estado["vidas"] <= 0:
                        estado["fin_del_juego"] = True
                        radio.apagar()
                    else:
                        # Reposicionar al jugador en el centro
                        estado["jugador"].x       = float(CARRILES_X[1])
                        estado["jugador"].y       = float(Y_JUGADOR)
                        estado["jugador"].vel_x   = 0
                        estado["jugador"].vel_y_mov = 0
                else:
                    nuevos_enemigos.append(e)

            estado["enemigos"] = nuevos_enemigos

            # Actualizar y limpiar particulas muertas
            estado["particulas"] = [p for p in estado["particulas"] if not p.muerta()]
            for p in estado["particulas"]:
                p.actualizar()

            # Incrementar puntaje por cada frame sobrevivido
            estado["puntaje"] += 1

        elif estado["inicio"]:
            # En la pantalla de inicio el fondo se mueve lentamente
            desplazamiento.actualizar(2.0, estado["puntaje"])

        # Actualizar el estado de la radio
        radio.actualizar()

        # ── DIBUJO ──
        desplazamiento.dibujar(pantalla)

        if estado["inicio"]:
            dibujar_inicio(pantalla, fuente_grande, fuente, fuente_chica)
        else:
            # Dibujar enemigos ordenados por Y (los de atras primero)
            for e in sorted(estado["enemigos"], key=lambda e: e.y):
                e.dibujar(pantalla)

            # Dibujar al jugador (solo si no es game over)
            if not estado["fin_del_juego"]:
                estado["jugador"].dibujar(pantalla)

            # Dibujar particulas de explosion
            for p in estado["particulas"]:
                p.dibujar(pantalla)

            # Dibujar el HUD
            dibujar_hud(pantalla, fuente, estado["puntaje"], estado["velocidad"],
                        estado["vidas"], radio)

            # Si es game over, dibujar la pantalla de fin
            if estado["fin_del_juego"]:
                dibujar_game_over(pantalla, fuente_grande, fuente, estado["puntaje"])

        pygame.display.flip()
#endregion


#region Punto de entrada del programa
if __name__ == "__main__":
    principal()
#endregion