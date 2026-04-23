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

import pygame
import random
import sys
import os
import math


ANCHO  = 480
ALTO   = 750
FPS    = 60
TITULO = "CHEPEPRESAS v5"

NEGRO    = (  0,   0,   0)
BLANCO   = (255, 255, 255)
ROJO     = (220,  50,  50)
AMARILLO = (255, 220,   0)
VERDE_CR = ( 14, 130,  60)
NARANJA  = (255, 140,   0)
CELESTE  = (150, 210, 255)

CARRILES_X = [155, 223, 314]
LIMITE_IZQ = 120
LIMITE_DER = 360

Y_SPAWN   = -80
Y_JUGADOR = 610
Y_FUERA   = 700

LIMITE_SUP = 80
LIMITE_INF = 690

ESCALA_FIJA = 1.0

CARRO_W = 46
CARRO_H = 76

VEL_BASE  = 2.0
VEL_MAX   = 9.0
INTV_BASE = 105

FONDO_FACTOR = 0.45

ENEMIGO_FACTOR_MIN = 1.6
ENEMIGO_FACTOR_MAX = 2.4

COLORES_ENEMIGO = [
    (  0, 100, 200), (160, 160,   0), ( 40, 160,  70),
    (160,  50, 160), (220, 110,   0), ( 60, 170, 170),
    (150,  40,  40), ( 60,  60, 160), (200,  90,  50),
]


def get_escala(y):
    return ESCALA_FIJA


def cargar_imagen(nombre):
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre)
    if os.path.exists(ruta):
        img = pygame.image.load(ruta).convert()
        img = pygame.transform.scale(img, (ANCHO, ALTO))
        print(f"OK {nombre}")
        return img
    print(f"No encontrada: {nombre}")
    return None


def fondo_procedural():
    surf = pygame.Surface((ANCHO, ALTO))
    surf.fill((80, 160, 60))
    pygame.draw.rect(surf, (65, 65, 70),
                     (LIMITE_IZQ - 10, 0, LIMITE_DER - LIMITE_IZQ + 20, ALTO))
    for y in range(0, ALTO, 50):
        mx1 = (CARRILES_X[0] + CARRILES_X[1]) // 2
        mx2 = (CARRILES_X[1] + CARRILES_X[2]) // 2
        pygame.draw.rect(surf, BLANCO, (mx1 - 2, y, 4, 28))
        pygame.draw.rect(surf, BLANCO, (mx2 - 2, y, 4, 28))
    return surf


class ScrollFondo:
    def __init__(self, fondos):
        self.fondos = fondos
        self.actual = fondos[min(fondos.keys())]
        self.offset = 0.0

    def actualizar(self, vel, puntaje):
        self.offset += vel
        if self.offset >= ALTO:
            self.offset -= ALTO
        # elegir fondo según puntaje
        for limite in sorted(self.fondos.keys()):
            if puntaje >= limite:
                self.actual = self.fondos[limite]

    def dibujar(self, surface):
        off = int(self.offset)
        surface.blit(self.actual, (0, off))
        surface.blit(self.actual, (0, off - ALTO))


def dibujar_carro(surface, cx, cy, esc, color, es_jugador=False):
    w  = max(6,  int(CARRO_W * esc))
    h  = max(10, int(CARRO_H * esc))
    cx, cy = int(cx), int(cy)
    osc = tuple(max(c - 55, 0) for c in color)
    r   = max(2, int(7 * esc))

    pygame.draw.rect(surface, color, (cx-w//2, cy-h//2, w, h), border_radius=r)
    pygame.draw.rect(surface, osc,
                     (cx-w//2+max(1,int(4*esc)), cy-h//2+max(1,int(9*esc)),
                      w-max(2,int(8*esc)), h-max(4,int(22*esc))),
                     border_radius=max(1, int(5*esc)))
    pygame.draw.rect(surface, CELESTE,
                     (cx-w//2+max(1,int(5*esc)), cy-h//2+max(1,int(5*esc)),
                      w-max(2,int(10*esc)), max(3, int(14*esc))),
                     border_radius=max(1, int(3*esc)))
    pygame.draw.rect(surface, CELESTE,
                     (cx-w//2+max(1,int(5*esc)), cy+h//2-max(3,int(20*esc)),
                      w-max(2,int(10*esc)), max(2, int(12*esc))),
                     border_radius=max(1, int(3*esc)))

    rw = max(2, int(8*esc))
    rh = max(3, int(15*esc))
    for rx, ry in [
        (-w//2-max(1,int(4*esc)), -h//2+max(1,int(5*esc))),
        ( w//2-max(1,int(4*esc)), -h//2+max(1,int(5*esc))),
        (-w//2-max(1,int(4*esc)),  h//2-max(3,int(20*esc))),
        ( w//2-max(1,int(4*esc)),  h//2-max(3,int(20*esc))),
    ]:
        pygame.draw.rect(surface, NEGRO, (cx+rx, cy+ry, rw, rh),
                         border_radius=max(1, int(3*esc)))

    fr = max(1, int(4*esc))
    pygame.draw.circle(surface, AMARILLO,
                       (cx-w//2+max(1,int(7*esc)), cy-h//2+max(1,int(4*esc))), fr)
    pygame.draw.circle(surface, AMARILLO,
                       (cx+w//2-max(1,int(7*esc)), cy-h//2+max(1,int(4*esc))), fr)

    if es_jugador:
        pw = max(4, int(20*esc))
        ph = max(2, int(6*esc))
        pygame.draw.rect(surface, AMARILLO,
                         (cx-pw//2, cy+h//2-max(2,int(11*esc)), pw, ph),
                         border_radius=1)
    else:
        lr = max(1, int(4*esc))
        pygame.draw.circle(surface, ROJO,
                           (cx-w//2+max(1,int(6*esc)), cy+h//2-max(1,int(5*esc))), lr)
        pygame.draw.circle(surface, ROJO,
                           (cx+w//2-max(1,int(6*esc)), cy+h//2-max(1,int(5*esc))), lr)


# ─────────────────────────────────────────────
#  SISTEMA DE RADIO
# ─────────────────────────────────────────────
class SistemaRadio:
    def __init__(self):
        self.enabled = False
        self.estacion_actual_idx = 0
        self.nombre_estaciones = []
        self.mp3_por_estacion = []
        self.mp3_actual_idx = 0
        self._cargar_estaciones()

    def _cargar_estaciones(self):
        carpeta_mp3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Radios")
        if not os.path.isdir(carpeta_mp3):
            self.nombre_estaciones = []
            self.mp3_por_estacion = []
            return

        carpeta_estaciones = sorted(
            [d for d in os.listdir(carpeta_mp3) if os.path.isdir(os.path.join(carpeta_mp3, d))]
        )

        if carpeta_estaciones:
            self.nombre_estaciones = carpeta_estaciones
            audios_mp3 = []
            for folder in carpeta_estaciones:
                folder_path = os.path.join(carpeta_mp3, folder)
                mp3s = sorted(
                    [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                     if f.lower().endswith(".mp3")]
                )
                audios_mp3.append(mp3s)
            self.mp3_por_estacion = audios_mp3
        else:
            mp3s = sorted(
                [os.path.join(carpeta_mp3, f) for f in os.listdir(carpeta_mp3)
                 if f.lower().endswith(".mp3")]
            )
            if mp3s:
                self.nombre_estaciones = ["Todas"]
                self.mp3_por_estacion = [mp3s]
            else:
                self.nombre_estaciones = []
                self.mp3_por_estacion = []

    def tiene_contenido(self):
        return bool(self.nombre_estaciones) and any(self.mp3_por_estacion)

    def _escoger_mp3(self):
        if self.estacion_actual_idx >= len(self.mp3_por_estacion):
            return None
        station_tracks = self.mp3_por_estacion[self.estacion_actual_idx]
        if not station_tracks:
            return None
        self.mp3_actual_idx = self.mp3_actual_idx % len(station_tracks)
        return station_tracks[self.mp3_actual_idx]

    def encender(self):
        if not self.tiene_contenido() or self.enabled:
            return
        self.enabled = True
        self._reproducir_actual()

    def apagar(self):
        self.enabled = False
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def siguiente_estacion(self):
        if not self.tiene_contenido():
            return
        self.estacion_actual_idx = (self.estacion_actual_idx + 1) % len(self.nombre_estaciones)
        self.mp3_actual_idx = 0
        if self.enabled:
            self._reproducir_actual()

    def _reproducir_actual(self):
        track = self._escoger_mp3()
        if not track:
            return
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def update(self):
        if not self.enabled:
            return
        try:
            if not pygame.mixer.music.get_busy():
                self._reproducir_actual()
        except Exception:
            pass


# ─────────────────────────────────────────────
#  PLAYER (con controles invertidos)
# ─────────────────────────────────────────────
class Player:
    VEL_MAX_MOV = 5.0
    ACELERACION = 0.4
    FRICCION    = 0.3

    def __init__(self):
        self.x   = float(CARRILES_X[1])
        self.y   = float(Y_JUGADOR)
        self.esc = get_escala(self.y)
        self.vel_x     = 0.0
        self.vel_y_mov = 0.0

        self.saltando      = False
        self.salto_offset  = 0.0
        self.vel_salto     = 0.0
        self.gravedad      = 0.6
        self.fuerza_salto  = -12

        # Controles invertidos (tu aporte)
        self.controles_invertidos = False
        self.tiempo_confusion     = 0

    def activar_confusion(self):
        self.controles_invertidos = True
        self.tiempo_confusion = pygame.time.get_ticks()

    def actualizar_estado(self):
        if self.controles_invertidos:
            if pygame.time.get_ticks() - self.tiempo_confusion > 5000:
                self.controles_invertidos = False

    def _rect(self):
        w = int(CARRO_W * self.esc * 1.3)
        h = int(CARRO_H * self.esc * 1.1)
        return pygame.Rect(int(self.x) - w // 2, int(self.y) - h // 2, w, h)

    def _aplicar_friccion(self, vel):
        if abs(vel) < self.FRICCION:
            return 0.0
        return vel - self.FRICCION if vel > 0 else vel + self.FRICCION

    def mover(self, teclas):
        self.actualizar_estado()

        hw = int(CARRO_W * self.esc) // 2
        hh = int(CARRO_H * self.esc) // 2

        # Controles normales o invertidos
        if self.controles_invertidos:
            # WASD invertidos, flechas normales
            izq = teclas[pygame.K_LEFT] or teclas[pygame.K_d]
            der = teclas[pygame.K_RIGHT] or teclas[pygame.K_a]
            arriba = teclas[pygame.K_UP] or teclas[pygame.K_s]
            abajo = teclas[pygame.K_DOWN] or teclas[pygame.K_w]
        else:
            # WASD normales + flechas normales
            izq = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
            der = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]
            arriba = teclas[pygame.K_UP] or teclas[pygame.K_w]
            abajo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]

        # Eje X
        if izq and not der:
            self.vel_x = max(-self.VEL_MAX_MOV, self.vel_x - self.ACELERACION)
        elif der and not izq:
            self.vel_x = min( self.VEL_MAX_MOV, self.vel_x + self.ACELERACION)
        else:
            self.vel_x = self._aplicar_friccion(self.vel_x)

        self.x += self.vel_x
        if self.x - hw < LIMITE_IZQ:
            self.x = LIMITE_IZQ + hw; self.vel_x = 0
        if self.x + hw > LIMITE_DER:
            self.x = LIMITE_DER - hw; self.vel_x = 0

        # Eje Y
        if arriba and not abajo:
            self.vel_y_mov = max(-self.VEL_MAX_MOV, self.vel_y_mov - self.ACELERACION)
        elif abajo and not arriba:
            self.vel_y_mov = min( self.VEL_MAX_MOV, self.vel_y_mov + self.ACELERACION)
        else:
            self.vel_y_mov = self._aplicar_friccion(self.vel_y_mov)

        nueva_y = self.y + self.vel_y_mov
        if nueva_y - hh < LIMITE_SUP:
            nueva_y = LIMITE_SUP + hh; self.vel_y_mov = 0.0
        elif nueva_y + hh > LIMITE_INF:
            nueva_y = LIMITE_INF - hh; self.vel_y_mov = 0.0
        self.y = nueva_y

    def saltar(self):
        if self.controles_invertidos:
            return
        if not self.saltando:
            self.saltando     = True
            self.salto_offset = 0.0
            self.vel_salto    = self.fuerza_salto

    def actualizar(self):
        if self.saltando:
            self.salto_offset += self.vel_salto
            self.vel_salto    += self.gravedad
            if self.salto_offset >= 0.0:
                self.salto_offset = 0.0
                self.saltando     = False
                self.vel_salto    = 0.0

    def dibujar(self, surface):
        visual_y = self.y + self.salto_offset
        esc = self.esc * 1.15 if self.saltando else self.esc
        dibujar_carro(surface, self.x, visual_y, esc, ROJO, es_jugador=True)

    def colisiona_con(self, enemy):
        return self._rect().colliderect(enemy.rect())


# ─────────────────────────────────────────────
#  ENEMY (con zigzag)
# ─────────────────────────────────────────────
class Enemy:
    def __init__(self, vel_juego, icono):
        self.icono   = icono
        self.carril  = random.randint(0, 2)
        self.x       = float(CARRILES_X[self.carril])
        self.y       = float(Y_SPAWN)
        self.color   = random.choice(COLORES_ENEMIGO)
        self._factor = random.uniform(ENEMIGO_FACTOR_MIN, ENEMIGO_FACTOR_MAX)
        self.vel     = vel_juego * self._factor

        self.zigzag      = random.random() < 0.3
        self.zigzag_amp  = random.uniform(30, 70)
        self.zigzag_freq = random.uniform(0.10, 0.10)
        self.t           = 0
        self.base_x      = self.x

    def actualizar(self, vel_juego):
        self.vel  = vel_juego * self._factor
        self.y   += self.vel
        self.t   += 1

        if self.zigzag:
            offset  = self.zigzag_amp * math.sin(self.t * self.zigzag_freq)
            self.x  = self.base_x + offset
            if self.x < LIMITE_IZQ:
                self.x = LIMITE_IZQ
            elif self.x > LIMITE_DER:
                self.x = LIMITE_DER

    def esc(self):
        return get_escala(self.y)

    def rect(self):
        e = self.esc()
        w = int(CARRO_W * e * 1.3)
        h = int(CARRO_H * e * 1.3)
        return pygame.Rect(int(self.x)-w//2, int(self.y)-h//2, w, h)

    def fuera(self):
        return self.y > Y_FUERA

    def dibujar(self, surface):
        if self.y >= -CARRO_H:
            dibujar_carro(surface, self.x, self.y, self.esc(), self.color)

            if self.zigzag:
                offset_y = math.sin(self.t * 0.1) * 6
                lado     = math.sin(self.t * 0.05)
                x_icono  = self.x + 1 if lado > 0 else self.x - 1 - self.icono.get_width()
                surface.blit(
                    self.icono,
                    (int(x_icono), int(self.y - self.icono.get_height() // 2 + offset_y))
                )


class Particula:
    def __init__(self, x, y):
        self.x     = x + random.uniform(-25, 25)
        self.y     = y + random.uniform(-25, 25)
        self.vx    = random.uniform(-5, 5)
        self.vy    = random.uniform(-8, 2)
        self.vida  = random.randint(25, 55)
        self.radio = random.randint(3, 10)
        self.color = random.choice([ROJO, AMARILLO, NARANJA, BLANCO])

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.3
        self.vida -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), max(1, self.radio))

    def muerta(self):
        return self.vida <= 0


def draw_hud(surface, fuente, puntaje, velocidad, vidas, radio):
    hud = pygame.Surface((ANCHO, 50), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 160))
    surface.blit(hud, (0, 0))
    surface.blit(fuente.render(f"PUNTAJE: {puntaje:05d}", True, AMARILLO), (10, 13))
    km  = int(80 + velocidad * 12)
    txt = fuente.render(f"{km} km/h", True, BLANCO)
    surface.blit(txt, (ANCHO - txt.get_width() - 10, 13))
    vidas_txt = fuente.render(f"VIDAS: {vidas}", True, ROJO)
    surface.blit(vidas_txt, (ANCHO//2 - vidas_txt.get_width()//2, 13))

    # Indicador de radio encendida
    if radio.enabled and radio.nombre_estaciones:
        nombre = radio.nombre_estaciones[radio.estacion_actual_idx]
        radio_txt = fuente.render(f"📻 {nombre}", True, CELESTE)
        surface.blit(radio_txt, (10, ALTO - 30))


def draw_gameover(surface, fg, f, puntaje):
    ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 185))
    surface.blit(ov, (0, 0))
    cx = ANCHO // 2
    for fuente, texto, color, y in [
        (fg, "PRESA!",                    ROJO,          ALTO//2 - 90),
        (f,  "Chocaste en el Coyol",      BLANCO,        ALTO//2 - 20),
        (f,  f"Puntaje: {puntaje:05d}",   AMARILLO,      ALTO//2 + 25),
        (f,  "[ R ] Reiniciar",           VERDE_CR,      ALTO//2 + 70),
        (f,  "[ ESC ] Salir",             (160,160,160), ALTO//2 +105),
    ]:
        s = fuente.render(texto, True, color)
        surface.blit(s, s.get_rect(center=(cx, y)))


def draw_inicio(surface, fg, f, fs):
    ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 200))
    surface.blit(ov, (0, 0))
    cx = ANCHO // 2
    for fuente, texto, color, y in [
        (fg, "CHEPEPRESAS",                 VERDE_CR,      ALTO//2 - 160),
        (f,  "Sobrevivi el trafico",         AMARILLO,      ALTO//2 -  90),
        (f,  "josefino...",                  AMARILLO,      ALTO//2 -  58),
        (fs, "WASD / Flechas para moverse",  BLANCO,        ALTO//2 +   5),
        (fs, "ESPACIO para saltar",          BLANCO,        ALTO//2 +  35),
        (fs, "Z encender radio | X cambiar | C apagar", (200,200,200), ALTO//2 +  63),
        (fs, "Evita los carros y no te quedes en presa", (200,200,200), ALTO//2 +  91),
        (f,  "[ ESPACIO ] para iniciar",     AMARILLO,      ALTO//2 + 135),
    ]:
        s = fuente.render(texto, True, color)
        surface.blit(s, s.get_rect(center=(cx, y)))

def cargar_fondos():
    img_files = {
        0: "ImagenBase1.png",
        500: "ImagenesBase5Tarde.png",
        1000: "ImagenesBase3Noche.png",
        1500: "ImagenesBase4Noche.png",
        2000: "ImagenesBase6Tarde.png"
    }
    fondos = {}
    for puntaje, fname in img_files.items():
        img = cargar_imagen(fname)
        if img is not None:
            fondos[puntaje] = img
    if not fondos:
        fondos[0] = fondo_procedural()
    return fondos


def main():
    pygame.init()
    pygame.display.set_caption(TITULO)
    screen = pygame.display.set_mode((ANCHO, ALTO))
    reloj  = pygame.time.Clock()

    try:
        pygame.mixer.init()
    except Exception:
        pass

    radio = SistemaRadio()

    fg = pygame.font.SysFont("Arial", 54, bold=True)
    f  = pygame.font.SysFont("Arial", 22, bold=True)
    fs = pygame.font.SysFont("Arial", 18)

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
        txt = fuente_tmp.render("?", True, NEGRO)
        icono_ebrio.blit(txt, (12, 8))

    fondos = cargar_fondos()
    scroll = ScrollFondo(fondos)

    def reset():
        return dict(
            player           = Player(),
            enemigos         = [],
            particulas       = [],
            puntaje          = 0,
            velocidad        = float(VEL_BASE),
            spawn_timer      = 0,
            game_over        = False,
            inicio           = True,
            enemigos_creados = 0,
            vidas            = 5,
        )

    estado = reset()

    while True:
        reloj.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if estado["inicio"] and ev.key == pygame.K_SPACE:
                    estado["inicio"] = False
                if estado["game_over"] and ev.key == pygame.K_r:
                    estado = reset()
                    estado["inicio"] = False
                    radio.apagar()
                if not estado["inicio"] and not estado["game_over"]:
                    if ev.key == pygame.K_SPACE:
                        estado["player"].saltar()
                # Controles de radio
                if ev.key == pygame.K_z:
                    radio.encender()
                elif ev.key == pygame.K_x:
                    radio.siguiente_estacion()
                elif ev.key == pygame.K_c:
                    radio.apagar()

        if not estado["inicio"] and not estado["game_over"]:
            estado["player"].mover(pygame.key.get_pressed())
            estado["player"].actualizar()
            estado["velocidad"] = min(VEL_BASE + estado["puntaje"] / 600, VEL_MAX)
            vel = estado["velocidad"]

            scroll.actualizar(vel * FONDO_FACTOR, estado["puntaje"])

            # Spawn de enemigos
            estado["spawn_timer"] += 1
            intervalo = max(28, int(INTV_BASE - estado["puntaje"] / 100))
            if estado["spawn_timer"] >= intervalo and estado["enemigos_creados"] < 80:
                estado["spawn_timer"] = 0
                ocupados = {e.carril for e in estado["enemigos"] if e.y < CARRO_H * 2}
                libres   = [c for c in range(3) if c not in ocupados]
                if libres:
                    carril = random.choice(libres)
                    nuevo  = Enemy(vel, icono_ebrio)
                    nuevo.carril = carril
                    nuevo.x      = float(CARRILES_X[carril])
                    estado["enemigos"].append(nuevo)

            for e in estado["enemigos"]:
                e.actualizar(vel)

            # Puntaje por enemigos esquivados
            vivos = []
            for e in estado["enemigos"]:
                if e.fuera():
                    estado["puntaje"] += 10
                else:
                    vivos.append(e)
            estado["enemigos"] = vivos

            # Colisiones
            nuevos_enemigos = []
            for e in estado["enemigos"]:
                if not estado["player"].saltando and estado["player"].colisiona_con(e):
                    # Sí es zigzag → activar confusión de controles
                    if e.zigzag:
                        estado["player"].activar_confusion()

                    estado["vidas"] -= 1

                    for _ in range(80):
                        estado["particulas"].append(
                            Particula(estado["player"].x, estado["player"].y)
                        )

                    if estado["vidas"] <= 0:
                        estado["game_over"] = True
                        radio.apagar()
                    else:
                        estado["player"].x       = float(CARRILES_X[1])
                        estado["player"].y       = float(Y_JUGADOR)
                        estado["player"].vel_x   = 0
                        estado["player"].vel_y_mov = 0
                else:
                    nuevos_enemigos.append(e)

            estado["enemigos"] = nuevos_enemigos

            estado["particulas"] = [p for p in estado["particulas"] if not p.muerta()]
            for p in estado["particulas"]:
                p.update()

            estado["puntaje"] += 1

        elif estado["inicio"]:
            scroll.actualizar(2.0, estado["puntaje"])

        radio.update()

        # ── DIBUJO ──
        scroll.dibujar(screen)

        if estado["inicio"]:
            draw_inicio(screen, fg, f, fs)
        else:
            for e in sorted(estado["enemigos"], key=lambda e: e.y):
                e.dibujar(screen)

            if not estado["game_over"]:
                estado["player"].dibujar(screen)

            for p in estado["particulas"]:
                p.draw(screen)

            draw_hud(screen, f, estado["puntaje"], estado["velocidad"],
                     estado["vidas"], radio)

            if estado["game_over"]:
                draw_gameover(screen, fg, f, estado["puntaje"])

        pygame.display.flip()


if __name__ == "__main__":
    main()