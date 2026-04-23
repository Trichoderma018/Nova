Nova - Asistente Virtual + ChepePresas
Proyecto final de Programación: un asistente virtual por voz llamado Nova que integra un juego de esquivar tráfico llamado ChepePresas, ambos desarrollados en Python.
Descripción
Nova (Asistente Virtual)
Asistente controlado por voz que permite:

Abrir YouTube y el navegador.
Consultar la fecha y hora actual.
Buscar en Wikipedia e Internet.
Reproducir videos en YouTube.
Contar chistes en español.
Crear y abrir proyectos Python en PyCharm.
Crear archivos .py y dictar código por voz con mapeo automático de sintaxis (e.g. "abrir paréntesis" → ().
Ejecutar programas Python y escuchar la salida.
Lanzar el juego ChepePresas.

Para ver todos los comandos disponibles, diga "qué puedes hacer" durante la ejecución.
ChepePresas (Juego)
Juego 2D con Pygame donde el jugador conduce un carro por una autopista josefina esquivando tráfico. Características:

Movimiento con WASD o flechas, salto con Espacio.
Enemigos con comportamiento zigzag (conductores ebrios) que invierten los controles al colisionar.
Sistema de radio con emisoras configurables desde la carpeta Radios/.
Fondos dinámicos que cambian según el puntaje (día → tarde → noche).
Sistema de vidas y partículas de explosión al chocar.

Requisitos

Python 3.10+
Windows (el asistente usa voces de Microsoft Speech)
PyCharm (opcional, para los comandos de gestión de proyectos)
Micrófono funcional

Instalación
bash# Clonar el repositorio
git clone <url-del-repositorio>
cd <nombre-del-repositorio>

# Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install pyttsx3 SpeechRecognition pywhatkit wikipedia pyjokes pygame pyaudio
Estructura del Proyecto
├── Asistente.py              # Asistente virtual Nova
├── chepepresas_v5.py         # Juego ChepePresas
├── ImagenBase1.png           # Fondo día
├── ImagenesBase3Noche.png    # Fondo noche 1
├── ImagenesBase4Noche.png    # Fondo noche 2
├── ImagenesBase5Tarde.png    # Fondo tarde 1
├── ImagenesBase6Tarde.png    # Fondo tarde 2
├── icono_ebrio.png           # Ícono de enemigo zigzag
├── Radios/                   # Carpeta de emisoras (MP3)
│   ├── Estacion1/
│   └── Estacion2/
├── .venv/                    # Entorno virtual (no versionado)
├── .gitignore
└── README.md
Uso
Ejecutar el asistente
bashpython Asistente.py
Nova solicitará su nombre por voz y quedará a la espera de comandos.
Ejecutar el juego directamente
bashpython chepepresas_v5.py
Controles del juego
TeclaAcciónWASD / FlechasMover el carroEspacioSaltarZEncender radioXCambiar emisoraCApagar radioRReiniciar (Game Over)ESCSalir
Configuración
En Asistente.py se pueden ajustar las siguientes rutas según el entorno:
pythonPYCHARM_PATH = r"C:\Program Files\JetBrains\PyCharm 2025.3.3\bin\pycharm64.exe"
RUTA_BASE_PROYECTOS = r"D:\2026\PrograFinal\Proyecto final\..."
Autores
Proyecto desarrollado como trabajo final de Programación — 2026.

PruebaVic