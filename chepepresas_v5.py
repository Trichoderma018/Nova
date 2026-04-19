"""
╔══════════════════════════════════════════════════════╗
║           CHEPEPRESAS v5 🚗💨                       ║
║   Scroll con ImagenBase1.png + ImagenBase2.png       ║
║   Carros bajando suavemente por los carriles         ║
╚══════════════════════════════════════════════════════╝

Controles:
  ← →    : Mover el carro (también A/D)
  R      : Reiniciar después de Game Over
  ESC    : Salir

Requisitos:
  pip install pygame

Estructura de archivos:
  chepepresas_v5.py   este archivo
  ImagenBase1.png     misma carpeta
  ImagenBase2.png     misma carpeta
"""

import pygame
import random
import sys
import os

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

# Geometria de la carretera (imagenes 1024x1024 escaladas a 480x750)
# Asfalto: x=140..333  |  divisores en x~180 y x~263
# Centros de carril: izq=160  centro=222  der=298
# Medidos directamente del juego en ejecucion (captura 596px -> juego 480px)
# Asfalto: x=126..361  |  divisores: x~189 y x~269
# Centros: izq=156  centro=229  der=317
# Medidos con letras P/M/F de referencia visual en captura 592x978 -> juego 480x750
CARRILES_X = [155, 223, 314]
LIMITE_IZQ = 120
LIMITE_DER = 360

Y_SPAWN   = -80     # enemigos nacen fuera de pantalla (entran desde arriba)
Y_JUGADOR = 610    # posicion Y inicial del jugador
Y_FUERA   = 700

# Limites verticales del area jugable (movimiento libre arriba/abajo)
LIMITE_SUP = 80     # justo debajo del HUD
LIMITE_INF = 690    # antes de salir de pantalla

ESCALA_FIJA = 1.0   # todos los carros se dibujan al tamano completo

CARRO_W = 46
CARRO_H = 76

VEL_BASE  = 2.0     # velocidad inicial del juego (progresion lenta)
VEL_MAX   = 9.0     # velocidad maxima del juego
INTV_BASE = 105

# Factor de velocidad del fondo respecto a vel_juego.
# El fondo se mueve lento para simular avance del jugador;
# los enemigos se mueven mucho mas rapido (vienen de frente).
FONDO_FACTOR = 0.45

# Rango de factor individual de cada enemigo.
# Minimo > 1.0 garantiza que SIEMPRE bajan mas rapido que el fondo.
ENEMIGO_FACTOR_MIN = 1.6
ENEMIGO_FACTOR_MAX = 2.4

COLORES_ENEMIGO = [
    (  0, 100, 200), (160, 160,   0), ( 40, 160,  70),
    (160,  50, 160), (220, 110,   0), ( 60, 170, 170),
    (150,  40,  40), ( 60,  60, 160), (200,  90,  50),
]


def get_escala(y):
    """Escala fija: todos los vehiculos se muestran al tamano completo"""
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
    def __init__(self, img_a, img_b):
        self.imgs   = [img_a, img_b]
        self.idx    = 0
        self.offset = 0.0

    def actualizar(self, vel):
        self.offset += vel
        if self.offset >= ALTO:
            self.offset -= ALTO
            self.idx = 1 - self.idx

    def dibujar(self, surface):
        off = int(self.offset)
        surface.blit(self.imgs[self.idx],     (0,  off))
        surface.blit(self.imgs[1 - self.idx], (0,  off - ALTO))


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


class Player:
    VEL_MAX_MOV  = 5.0   # velocidad maxima de movimiento (px/frame)
    ACELERACION  = 0.4   # incremento por frame mientras se mantiene la tecla
    FRICCION     = 0.3   # desaceleracion por frame al soltar la tecla

    def __init__(self):
        self.x   = float(CARRILES_X[1])
        self.y   = float(Y_JUGADOR)
        self.esc = get_escala(self.y)
        self.vel_x = 0.0  # velocidad horizontal actual (progresiva)
        self.vel_y_mov = 0.0  # velocidad vertical de movimiento (progresiva)

        # Salto (eje Y temporal con gravedad, independiente del movimiento)
        self.saltando = False
        self.salto_offset = 0.0   # desplazamiento visual del salto
        self.vel_salto   = 0.0
        self.gravedad    = 0.6
        self.fuerza_salto = -12

    def _rect(self):
        """Rectangulo de colision basado en posicion real (sin offset de salto)"""
        w = int(CARRO_W * self.esc)
        h = int(CARRO_H * self.esc)
        return pygame.Rect(int(self.x)-w//2, int(self.y)-h//2, w, h)

    def _aplicar_friccion(self, vel):
        """Aplica friccion progresiva a una velocidad"""
        if abs(vel) < self.FRICCION:
            return 0.0
        return vel - self.FRICCION if vel > 0 else vel + self.FRICCION

    def mover(self, teclas):
        hw = int(CARRO_W * self.esc) // 2
        hh = int(CARRO_H * self.esc) // 2

        # Lectura de teclas: flechas y WASD
        izq   = teclas[pygame.K_LEFT]  or teclas[pygame.K_a]
        der   = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]
        arriba = teclas[pygame.K_UP]   or teclas[pygame.K_w]
        abajo  = teclas[pygame.K_DOWN] or teclas[pygame.K_s]

        # --- Eje horizontal (igual que antes) ---
        if izq and not der:
            self.vel_x = max(-self.VEL_MAX_MOV, self.vel_x - self.ACELERACION)
        elif der and not izq:
            self.vel_x = min( self.VEL_MAX_MOV, self.vel_x + self.ACELERACION)
        else:
            self.vel_x = self._aplicar_friccion(self.vel_x)

        nueva_x = self.x + self.vel_x
        if nueva_x - hw < LIMITE_IZQ:
            nueva_x = LIMITE_IZQ + hw
            self.vel_x = 0.0
        elif nueva_x + hw > LIMITE_DER:
            nueva_x = LIMITE_DER - hw
            self.vel_x = 0.0
        self.x = nueva_x

        # --- Eje vertical (movimiento libre arriba/abajo) ---
        if arriba and not abajo:
            self.vel_y_mov = max(-self.VEL_MAX_MOV, self.vel_y_mov - self.ACELERACION)
        elif abajo and not arriba:
            self.vel_y_mov = min( self.VEL_MAX_MOV, self.vel_y_mov + self.ACELERACION)
        else:
            self.vel_y_mov = self._aplicar_friccion(self.vel_y_mov)

        nueva_y = self.y + self.vel_y_mov
        if nueva_y - hh < LIMITE_SUP:
            nueva_y = LIMITE_SUP + hh
            self.vel_y_mov = 0.0
        elif nueva_y + hh > LIMITE_INF:
            nueva_y = LIMITE_INF - hh
            self.vel_y_mov = 0.0
        self.y = nueva_y

    def saltar(self):
        """Inicia el salto (solo si no esta ya saltando)"""
        if not self.saltando:
            self.saltando = True
            self.salto_offset = 0.0
            self.vel_salto = self.fuerza_salto

    def actualizar(self):
        """Actualiza la fisica del salto (offset visual independiente)"""
        if self.saltando:
            self.salto_offset += self.vel_salto
            self.vel_salto += self.gravedad

            # El salto termina cuando el offset vuelve a 0 (nivel del suelo)
            if self.salto_offset >= 0.0:
                self.salto_offset = 0.0
                self.saltando = False
                self.vel_salto = 0.0

    def dibujar(self, surface):
        # Posicion visual: posicion real + offset de salto (negativo = arriba)
        visual_y = self.y + self.salto_offset
        esc = self.esc * 1.15 if self.saltando else self.esc
        dibujar_carro(surface, self.x, visual_y, esc, ROJO, es_jugador=True)

    def colisiona_con(self, enemy):
        """Colision basada en posicion real (sin offset de salto)"""
        return self._rect().colliderect(enemy.rect())


class Enemy:
    def __init__(self, vel_juego):
        self.carril  = random.randint(0, 2)
        self.x       = float(CARRILES_X[self.carril])
        self.y       = float(Y_SPAWN)
        self.color   = random.choice(COLORES_ENEMIGO)
        self._factor = random.uniform(ENEMIGO_FACTOR_MIN, ENEMIGO_FACTOR_MAX)
        self.vel     = vel_juego * self._factor

    def actualizar(self, vel_juego):
        # mantener factor propio pero escalar con el juego
        self.vel  = vel_juego * self._factor
        # movimiento constante hacia abajo
        self.y   += self.vel

    def esc(self):
        return get_escala(self.y)

    def rect(self):
        e = self.esc()
        w = int(CARRO_W * e)
        h = int(CARRO_H * e)
        return pygame.Rect(int(self.x)-w//2, int(self.y)-h//2, w, h)

    def fuera(self):
        return self.y > Y_FUERA

    def dibujar(self, surface):
        # Dibujar solo cuando el carro es visible en pantalla
        if self.y >= -CARRO_H:
            dibujar_carro(surface, self.x, self.y, self.esc(), self.color)


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
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.3
        self.vida -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), max(1, self.radio))

    def muerta(self):
        return self.vida <= 0


def draw_hud(surface, fuente, puntaje, velocidad, vidas):
    hud = pygame.Surface((ANCHO, 50), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 160))
    surface.blit(hud, (0, 0))
    surface.blit(fuente.render(f"PUNTAJE: {puntaje:05d}", True, AMARILLO), (10, 13))
    km  = int(80 + velocidad * 12)
    txt = fuente.render(f"{km} km/h", True, BLANCO)
    surface.blit(txt, (ANCHO - txt.get_width() - 10, 13))
    # NUEVO: mostrar vidas
    vidas_txt = fuente.render(f"VIDAS: {vidas}", True, ROJO)
    surface.blit(vidas_txt, (ANCHO//2 - vidas_txt.get_width()//2, 13))

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
        (fg, "CHEPEPRESAS",               VERDE_CR,      ALTO//2 - 160),
        (f,  "Sobrevi el trafico",        AMARILLO,      ALTO//2 -  90),
        (f,  "josefino...",               AMARILLO,      ALTO//2 -  58),
        (fs, "WASD / Flechas para moverse", BLANCO,        ALTO//2 +   5),
        (fs, "ESPACIO para saltar",           BLANCO,        ALTO//2 +  35),
        (fs, "Evita los carros y no",     (200,200,200), ALTO//2 +  63),
        (fs, "te quedes en presa",        (200,200,200), ALTO//2 +  91),
        (f,  "[ ESPACIO ] para iniciar",  AMARILLO,      ALTO//2 + 135),
    ]:
        s = fuente.render(texto, True, color)
        surface.blit(s, s.get_rect(center=(cx, y)))


def main():
    pygame.init()
    pygame.display.set_caption(TITULO)
    screen = pygame.display.set_mode((ANCHO, ALTO))
    reloj  = pygame.time.Clock()

    fg = pygame.font.SysFont("Arial", 54, bold=True)
    f  = pygame.font.SysFont("Arial", 22, bold=True)
    fs = pygame.font.SysFont("Arial", 18)

    img1 = cargar_imagen("ImagenBase1.png")
    img2 = cargar_imagen("ImagenBase2.png")
    if img1 is None and img2 is None:
        img1 = img2 = fondo_procedural()
    elif img1 is None:
        img1 = img2
    elif img2 is None:
        img2 = img1

    scroll = ScrollFondo(img1, img2)

    def reset():
        return dict(
            player      = Player(),
            enemigos    = [],
            particulas  = [],
            puntaje     = 0,
            velocidad   = float(VEL_BASE),
            spawn_timer = 0,
            game_over   = False,
            inicio      = True,
            enemigos_creados=0,
            vidas       = 5,   # NUEVO: contador de vidas
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
                # Salto con espacio (solo durante juego activo)
                if not estado["inicio"] and not estado["game_over"]:
                    if ev.key == pygame.K_SPACE:
                        estado["player"].saltar()

        if not estado["inicio"] and not estado["game_over"]:
            estado["player"].mover(pygame.key.get_pressed())
            estado["player"].actualizar()
            estado["velocidad"] = min(VEL_BASE + estado["puntaje"] / 600, VEL_MAX)
            vel = estado["velocidad"]

            scroll.actualizar(vel * FONDO_FACTOR)

            # Spawn
            estado["spawn_timer"] += 1
            intervalo = max(28, int(INTV_BASE - estado["puntaje"] / 100))
            if estado["spawn_timer"] >= intervalo and estado["enemigos_creados"] < 80:
                estado["spawn_timer"] = 0
                ocupados = {e.carril for e in estado["enemigos"]
                            if e.y < CARRO_H * 2}
                libres = [c for c in range(3) if c not in ocupados]
                if libres:
                    carril = random.choice(libres)
                    nuevo = Enemy(vel)
                    nuevo.carril = carril
                    nuevo.x = float(CARRILES_X[carril])
                    estado["enemigos"].append(nuevo)

            # Actualizar enemigos
            for e in estado["enemigos"]:
                e.actualizar(vel)

            # Eliminar + puntaje
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
                if (
                        not estado["player"].saltando
                        and estado["player"].colisiona_con(e)
                ):
                    estado["vidas"] -= 1

                    for _ in range(80):
                        estado["particulas"].append(
                            Particula(estado["player"].x, estado["player"].y)
                        )

                    if estado["vidas"] <= 0:
                        estado["game_over"] = True
                    else:
                        # Resetear jugador sin reiniciar juego
                        estado["player"] = Player()

                    # NO agregamos el enemigo → desaparece (evita múltiples golpes)
                    if estado["vidas"] <= 0:
                        estado["game_over"] = True
                else:
                    nuevos_enemigos.append(e)

            estado["enemigos"] = nuevos_enemigos

            # Particulas
            estado["particulas"] = [p for p in estado["particulas"] if not p.muerta()]
            for p in estado["particulas"]:
                p.update()

            estado["puntaje"] += 1

        elif estado["inicio"]:
            scroll.actualizar(2.0)

        # Dibujo
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

            draw_hud(screen, f, estado["puntaje"], estado["velocidad"], estado["vidas"])


            if estado["game_over"]:
                draw_gameover(screen, fg, f, estado["puntaje"])

        pygame.display.flip()


if __name__ == "__main__":
    main()