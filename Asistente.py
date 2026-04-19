#region Librerias del Asisten
import pyttsx3 #Libreria para el motor de voz de nuestro asistente
import speech_recognition as sr #Libreria para el reconocimiento de voz
import pywhatkit #Libreria para busquedas en internet
import webbrowser #Para interactuar con el navegador
import datetime #Para datos de fecha y hora
import wikipedia #Para interactuar con wikipedia
import pyaudio #Para funciones de audio
from wikipedia import languages #Para interactuar con lenguajes especificos de wikipedia
import pyjokes #para chistes y bromas
import subprocess #Para ejecutar procesos externos (PyCharm, Python, venv)
import os #Para manejo de archivos y directorios
import sys #Para obtener el interprete de Python actual al lanzar el juego
#endregion

#region Configuracion de rutas
# Ruta del ejecutable de PyCharm (ajustar segun instalacion)
PYCHARM_PATH = r"C:\Program Files\JetBrains\PyCharm 2025.3.3\bin\pycharm64.exe"
# Ruta base por defecto para proyectos Python
RUTA_BASE_PROYECTOS = r"D:\python"
# Archivo del juego que el asistente puede ejecutar bajo demanda
JUEGO_PY = "chepepresas_v5.py"
#endregion

# Voz por defecto
idioma3 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0'

#region 1 MICROFONOS DISPONIBLES
#Funcion para verificar que el microfono está disponible
def verificar_microfono():
    lista_microfonos = sr.Microphone.list_microphone_names()

    if lista_microfonos:
        print("Microfonos disponibles: ")
        for iterador, microfono in enumerate(lista_microfonos):
            print(f"{iterador}: {microfono}")
    else:
        print("No se encontraron micrófonos disponibles")
#endregion

#region 2 LENGUAJES DISPONIBLES
#Funcion para validar los lenguajes disponibles que existen en el sistema operativo
def lenguajes_disponibles():
    motor_voz = pyttsx3.init()

    for voz in motor_voz.getProperty('voices'):
        print(voz)

    idioma1 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0'
    idioma2 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
    idioma3 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0'
#endregion

#region 3 CAPTURAR AUDIO DESDE MICROFONO
#Funcion que permite capturar el audio del micrófono y convertirlo en texto
def transformar_audio_en_texto():
    reconocimiento_voz = sr.Recognizer()

    try:
        with sr.Microphone() as origen:
            #Ajustar el umbral de ruido ambiente
            reconocimiento_voz.adjust_for_ambient_noise(origen, duration=1)
            reconocimiento_voz.pause_threshold = 3
            reconocimiento_voz.phrase_time_limit = 15
            print("Por favor hable al micrófono ahora......")
            audio = reconocimiento_voz.listen(origen)
            #Intentar reconocer lo que solicita el usuario
            solicitud = reconocimiento_voz.recognize_google(audio, language="es-CR")
            print("Audio reconocido: " + solicitud)
            return solicitud
    except sr.UnknownValueError:
        print("Lo siento, no entendi tu solicitud, intenta de nuevo!!!!")
        return "Intenta de nuevo"
    except sr.RequestError as e:
        print(f"Error de conexión al servicio de reconocimiento {e}, intenta de nuevo!!!")
        return "Intenta de nuevo"
    except Exception as e:
        print(f"Error inesperado {e}, intenta de nuevo!!!")
        return "Intenta de nuevo"
#endregion

#region 4 REPRODUCIR VOZ
#Funcion que permite al asistente ser escuchado, capacidad de hablar
def hablar(mensaje):
    #Encender el motor de pyttsx3
    motor_voz = pyttsx3.init()

    motor_voz.setProperty('voice', idioma3)

    #pronunciar o hablar el contenido del mensaje
    motor_voz.say(mensaje)

    motor_voz.runAndWait()

#Funcion para comunicar el dia de la semana
def informar_dia():
    fecha = datetime.date.today()
    print(fecha)

    #variable para el dia de la semana
    num_dia = fecha.weekday()
    print(num_dia)

    #Diccionario de dias de la semana
    nombre_dia = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miércoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo'
    }

    #Comunique el dia de la semana
    hablar(f'Hoy es {nombre_dia[num_dia]}')
#Funcion para cominicar la hora actual
def informar_hora():
    #variable para los datos de la hora
    hora_actual = datetime.datetime.now()
    print(hora_actual)

    hora_actual = (f'En este momento son las {hora_actual.hour} horas con {hora_actual.minute} minutos y {hora_actual.second} segundos')

    hablar(hora_actual)

#Funcion para saludar segun la hora de ejecucion
def saludo(nombre):
    hora_actual = datetime.datetime.now()

    if hora_actual.hour < 6 or hora_actual.hour>=19:
        msj_saludo='Buenas noches'
    elif hora_actual.hour>=6 and hora_actual.hour<12:
        msj_saludo = 'Buenos dias'
    else:
        msj_saludo = 'Buenas tardes'

    hablar(f'Hola {msj_saludo} {nombre}. Cómo te puedo ayudar hoy?')
#endregion

#region 6 FUNCIONES DE PYCHARM - Interaccion con el IDE

#Mapeo de palabras dictadas a simbolos de Python
MAPEO_VOZ_SINTAXIS = {
    'abrir paréntesis': '(',
    'cerrar paréntesis': ')',
    'abrir corchete': '[',
    'cerrar corchete': ']',
    'abrir llave': '{',
    'cerrar llave': '}',
    'dos puntos': ':',
    'punto y coma': ';',
    'comillas': '"',
    'comilla simple': "'",
    'igual': '=',
    'doble igual': '==',
    'diferente': '!=',
    'mayor que': '>',
    'menor que': '<',
    'mayor o igual': '>=',
    'menor o igual': '<=',
    'más': '+',
    'menos': '-',
    'por': '*',
    'entre': '/',
    'coma': ',',
    'punto': '.',
    'tabulación': '\t',
    'espacio': ' ',
    'flecha': '->',
    'hashtag': '#',
    'arroba': '@',
    'guion bajo': '_',
    'and': 'and',
    'or': 'or',
    'not': 'not',
}

def listar_comandos():
    """Informa al usuario todos los comandos disponibles"""
    comandos = (
        "Estos son los comandos que puedo ejecutar: "
        "Uno, abrir youtube. "
        "Dos, abrir navegador. "
        "Tres, qué día es hoy. "
        "Cuatro, qué hora es. "
        "Cinco, busca en wikipedia, seguido de tu consulta. "
        "Seis, busca en internet, seguido de tu consulta. "
        "Siete, reproducir, seguido del nombre del video. "
        "Ocho, chiste, para escuchar un chiste. "
        "Nueve, crear proyecto de python. "
        "Diez, abrir proyecto, para abrir un proyecto existente. "
        "Once, crear archivo, para crear un archivo Python en el proyecto. "
        "Doce, dictar código, para entrar en modo dictado y elegir el archivo. "
        "Trece, ejecutar programa, para correr el archivo actual. "
        "Catorce, guardar cambios, para guardar el archivo en edición. "
        "Quince, qué puedes hacer, para escuchar esta lista. "
        "Dieciséis, abrir juego, para lanzar Chepe Presas. "
        "Y diecisiete, adiós, para despedirnos."
    )
    hablar(comandos)

def preguntar_si_no(pregunta):
    """Pregunta al usuario algo y espera respuesta si/no"""
    hablar(pregunta)
    respuesta = transformar_audio_en_texto().lower()
    return 'sí' in respuesta or 'si' in respuesta

def crear_proyecto_python():
    """Guia al usuario para crear un nuevo proyecto de Python con PyCharm"""
    hablar("Vamos a crear un nuevo proyecto en Python. Dime el nombre del proyecto.")
    nombre_proyecto = transformar_audio_en_texto().lower().strip()
    # Limpiar caracteres no validos para nombre de carpeta
    nombre_proyecto = nombre_proyecto.replace(" ", "_")
    hablar(f"El proyecto se llamará {nombre_proyecto}")

    # Preguntar ubicacion
    hablar(f"La ubicación por defecto es {RUTA_BASE_PROYECTOS}. ¿Deseas usar esta ubicación?")
    respuesta_ubicacion = transformar_audio_en_texto().lower()
    if 'sí' in respuesta_ubicacion or 'si' in respuesta_ubicacion:
        ruta_proyecto = os.path.join(RUTA_BASE_PROYECTOS, nombre_proyecto)
    else:
        hablar("Dime la ruta donde quieres crear el proyecto")
        ruta_personalizada = transformar_audio_en_texto().strip()
        ruta_proyecto = os.path.join(ruta_personalizada, nombre_proyecto)

    # Preguntar opciones adicionales
    crear_git = preguntar_si_no("¿Deseas crear un repositorio Git para este proyecto?")
    crear_welcome = preguntar_si_no("¿Deseas crear un script de bienvenida, main punto py?")

    # Preguntar tipo de interprete
    hablar("¿Qué tipo de intérprete deseas? Las opciones son: project venv, uv, base conda, o custom. Di el nombre.")
    tipo_interprete = transformar_audio_en_texto().lower()

    # Crear la estructura de carpetas del proyecto
    try:
        os.makedirs(ruta_proyecto, exist_ok=True)
        hablar(f"Carpeta del proyecto creada en {ruta_proyecto}")

        # Crear entorno virtual si aplica (project venv por defecto)
        if 'conda' not in tipo_interprete and 'custom' not in tipo_interprete:
            hablar("Creando entorno virtual, esto puede tomar un momento")
            ruta_venv = os.path.join(ruta_proyecto, '.venv')
            subprocess.run(['python', '-m', 'venv', ruta_venv], check=True)
            hablar("Entorno virtual creado exitosamente")

        # Inicializar repositorio Git si se solicito
        if crear_git:
            subprocess.run(['git', 'init'], cwd=ruta_proyecto, check=True)
            hablar("Repositorio Git inicializado")

        # Crear welcome script si se solicito
        if crear_welcome:
            ruta_main = os.path.join(ruta_proyecto, 'main.py')
            with open(ruta_main, 'w', encoding='utf-8') as archivo:
                archivo.write('# Proyecto: ' + nombre_proyecto + '\n')
                archivo.write('# Creado con Nova - Asistente Virtual\n\n')
                archivo.write('print("Hola mundo! Bienvenido al proyecto ' + nombre_proyecto + '")\n')
            hablar("Script de bienvenida creado")

        # Abrir PyCharm con el proyecto
        hablar("Abriendo PyCharm con tu nuevo proyecto")
        subprocess.Popen([PYCHARM_PATH, ruta_proyecto])
        hablar("Listo, PyCharm se está abriendo con tu proyecto")

        return ruta_proyecto

    except Exception as e:
        print(f"Error al crear proyecto: {e}")
        hablar(f"Hubo un error al crear el proyecto: {e}")
        return None

def abrir_proyecto(nombre_usuario):
    """Abre un proyecto existente en PyCharm"""
    hablar("¿Cuál es el nombre del proyecto que deseas abrir?")
    nombre_proyecto = transformar_audio_en_texto().lower().strip().replace(" ", "_")

    ruta_proyecto = os.path.join(RUTA_BASE_PROYECTOS, nombre_proyecto)

    if os.path.isdir(ruta_proyecto):
        hablar(f"Abriendo el proyecto {nombre_proyecto} en PyCharm")
        subprocess.Popen([PYCHARM_PATH, ruta_proyecto])
        hablar(f"{nombre_usuario}, PyCharm se está abriendo con tu proyecto")
        return ruta_proyecto
    else:
        hablar(f"No encontré el proyecto {nombre_proyecto} en la carpeta de proyectos")
        hablar("¿Deseas dictar la ruta completa?")
        respuesta = transformar_audio_en_texto().lower()
        if 'sí' in respuesta or 'si' in respuesta:
            hablar("Dime la ruta completa del proyecto")
            ruta_completa = transformar_audio_en_texto().strip()
            if os.path.isdir(ruta_completa):
                subprocess.Popen([PYCHARM_PATH, ruta_completa])
                hablar("PyCharm se está abriendo")
                return ruta_completa
            else:
                hablar("La ruta no existe, verifica e intenta de nuevo")
        return None

def aplicar_mapeo_sintaxis(texto):
    """Reemplaza palabras clave del dictado por simbolos Python"""
    for palabra, simbolo in MAPEO_VOZ_SINTAXIS.items():
        texto = texto.replace(palabra, simbolo)
    return texto

def crear_archivo(proyecto_actual):
    """Crea un archivo .py en el proyecto activo (sin entrar al dictado)"""
    if not proyecto_actual:
        hablar("No hay un proyecto activo. Primero crea o abre un proyecto")
        return None

    hablar("Dime el nombre del archivo que deseas crear")
    nombre_archivo = transformar_audio_en_texto().lower().strip().replace(" ", "_")

    # Agregar extension .py si no la tiene
    if not nombre_archivo.endswith('.py'):
        nombre_archivo += '.py'

    ruta_archivo = os.path.join(proyecto_actual, nombre_archivo)

    # Crear el archivo vacio si no existe
    if not os.path.isfile(ruta_archivo):
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write('')
        hablar(f"Archivo {nombre_archivo} creado exitosamente en el proyecto")
    else:
        hablar(f"El archivo {nombre_archivo} ya existe en el proyecto")

    return ruta_archivo

def seleccionar_archivo(proyecto_actual):
    """Lista los archivos .py del proyecto y permite al usuario elegir uno por voz"""
    if not proyecto_actual:
        hablar("No hay un proyecto activo. Primero crea o abre un proyecto")
        return None

    # Buscar archivos .py en la raiz del proyecto
    archivos_py = [f for f in os.listdir(proyecto_actual) if f.endswith('.py')]

    if not archivos_py:
        hablar("No hay archivos Python en el proyecto. Primero crea un archivo")
        return None

    # Listar los archivos disponibles por voz
    hablar(f"Encontré {len(archivos_py)} archivos Python en el proyecto:")
    for i, archivo in enumerate(archivos_py, 1):
        hablar(f"{i}, {archivo}")

    hablar("Dime el nombre del archivo en el que deseas dictar")
    nombre_elegido = transformar_audio_en_texto().lower().strip().replace(" ", "_")

    # Agregar extension .py si no la dijo
    if not nombre_elegido.endswith('.py'):
        nombre_elegido += '.py'

    ruta_archivo = os.path.join(proyecto_actual, nombre_elegido)

    if os.path.isfile(ruta_archivo):
        hablar(f"Archivo {nombre_elegido} seleccionado")
        return ruta_archivo
    else:
        hablar(f"No encontré el archivo {nombre_elegido} en el proyecto")
        return None

def dictar_codigo(proyecto_actual, archivo_actual, buffer_codigo):
    """Modo dictado independiente: permite elegir archivo y dictar codigo"""
    if not proyecto_actual:
        hablar("No hay un proyecto activo. Primero crea o abre un proyecto")
        return archivo_actual, buffer_codigo

    # Preguntar si quiere usar el archivo actual o elegir otro
    if archivo_actual:
        nombre_actual = os.path.basename(archivo_actual)
        hablar(f"El archivo activo es {nombre_actual}. ¿Deseas dictar en este archivo?")
        respuesta = transformar_audio_en_texto().lower()
        if 'no' in respuesta:
            archivo_seleccionado = seleccionar_archivo(proyecto_actual)
            if not archivo_seleccionado:
                return archivo_actual, buffer_codigo
            archivo_actual = archivo_seleccionado
            # Cargar contenido existente del archivo al buffer
            with open(archivo_actual, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
                buffer_codigo = contenido.splitlines() if contenido.strip() else []
    else:
        # No hay archivo activo, debe elegir uno
        archivo_seleccionado = seleccionar_archivo(proyecto_actual)
        if not archivo_seleccionado:
            return None, []
        archivo_actual = archivo_seleccionado
        # Cargar contenido existente del archivo al buffer
        with open(archivo_actual, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            buffer_codigo = contenido.splitlines() if contenido.strip() else []

    hablar("Entrando en modo dictado de código")
    hablar("Puedes dictar tu código. Di nueva línea para saltar línea, guardar para guardar, o salir de dictado para terminar")

    # Bucle de dictado de codigo
    while True:
        hablar("Dictando...")
        linea = transformar_audio_en_texto().lower()

        if 'salir de dictado' in linea:
            # Guardar antes de salir si hay contenido
            if buffer_codigo:
                with open(archivo_actual, 'w', encoding='utf-8') as archivo:
                    archivo.write('\n'.join(buffer_codigo) + '\n')
                hablar("Archivo guardado. Saliendo del modo dictado")
            else:
                hablar("Saliendo del modo dictado")
            break
        elif linea == 'guardar':
            with open(archivo_actual, 'w', encoding='utf-8') as archivo:
                archivo.write('\n'.join(buffer_codigo) + '\n')
            hablar("Archivo guardado exitosamente")
            continue
        elif linea == 'nueva línea' or linea == 'nueva linea':
            buffer_codigo.append('')
            hablar("Línea en blanco agregada")
            continue
        elif linea == 'intenta de nuevo':
            continue
        else:
            # Aplicar mapeo de voz a sintaxis Python
            linea_procesada = aplicar_mapeo_sintaxis(linea)
            buffer_codigo.append(linea_procesada)
            print(f"  > {linea_procesada}")
            hablar(f"Línea agregada: {linea_procesada}")

    return archivo_actual, buffer_codigo

def ejecutar_programa(proyecto_actual, archivo_actual, nombre_usuario):
    """Ejecuta el archivo Python actual y lee la salida por voz"""
    if not archivo_actual:
        hablar("No hay un archivo activo para ejecutar. Primero crea o selecciona un archivo")
        return

    if not os.path.isfile(archivo_actual):
        hablar("El archivo no existe, verifica la ruta")
        return

    hablar(f"Ejecutando {os.path.basename(archivo_actual)}")
    try:
        resultado = subprocess.run(
            ['python', archivo_actual],
            capture_output=True, text=True, timeout=30,
            cwd=proyecto_actual
        )

        if resultado.stdout:
            hablar("La salida del programa es la siguiente:")
            print(f"STDOUT:\n{resultado.stdout}")
            hablar(resultado.stdout)
        if resultado.stderr:
            hablar("Se encontraron errores:")
            print(f"STDERR:\n{resultado.stderr}")
            hablar(resultado.stderr)
        if not resultado.stdout and not resultado.stderr:
            hablar("El programa se ejecutó sin producir salida")

    except subprocess.TimeoutExpired:
        hablar("El programa tardó demasiado y fue detenido")
    except Exception as e:
        hablar(f"Error al ejecutar el programa: {e}")

def guardar_cambios(archivo_actual, buffer_codigo):
    """Guarda el buffer de codigo actual al archivo en disco"""
    if not archivo_actual:
        hablar("No hay un archivo activo para guardar")
        return

    try:
        with open(archivo_actual, 'w', encoding='utf-8') as archivo:
            archivo.write('\n'.join(buffer_codigo) + '\n')
        hablar(f"Archivo {os.path.basename(archivo_actual)} guardado exitosamente")
    except Exception as e:
        hablar(f"Error al guardar: {e}")

def abrir_juego(juego_py=JUEGO_PY):
    """Ejecuta el juego .py ubicado en la misma carpeta que este asistente sin bloquear a Nova"""
    # Resolver ruta absoluta del juego junto al script del asistente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_juego = os.path.join(base_dir, juego_py)

    if not os.path.isfile(ruta_juego):
        hablar(f"No encontré el juego {juego_py} en la carpeta del asistente")
        return

    hablar("Abriendo el juego, disfrutalo")
    try:
        # Popen no bloquea: el asistente sigue escuchando mientras corre el juego
        # sys.executable garantiza usar el mismo interprete (y venv) que ejecuta a Nova
        subprocess.Popen([sys.executable, ruta_juego], cwd=base_dir)
    except Exception as e:
        hablar(f"Error al abrir el juego: {e}")
#endregion

#region 5 FUNCIONES DE ASISTENCIA VIRTUAL
def asistir_usuario():
    hablar("Bienvenido")
    hablar("Mi nombre es Nova, soy tu asistente virtual")
    hablar("Por favor, dime tu nombre")
    nombre_usuario = transformar_audio_en_texto().lower()
    saludo(nombre_usuario)

    # Variables de estado para manejo de proyectos y archivos
    proyecto_actual = None  # Ruta del proyecto activo
    archivo_actual = None   # Ruta del archivo en edicion
    buffer_codigo = []      # Contenido del archivo en memoria

    #variable para el control del bucle
    iniciar = True

    while iniciar:
        #Activar el microfono para capturar la solicitud del usuario
        solicitud = transformar_audio_en_texto().lower()

        #Evaluamos la peticion del usuario para encontrar coincidencias de tipos de solicitud
        if 'abrir youtube' in solicitud:
            hablar(f"Con gusto {nombre_usuario}, aqui tienes Youtube")
            webbrowser.open("https://www.youtube.com")
            continue
        elif 'abrir navegador' in solicitud:
            hablar(f"Claro {nombre_usuario}, acabo de abrir el navegador, dime si necesitas algo más")
            webbrowser.open("https://www.google.com")
            continue
        elif 'qué dia es hoy' in solicitud:
            informar_dia()
            continue
        elif 'qué hora es' in solicitud:
            informar_hora()
            continue
        elif 'busca en wikipedia' in solicitud:
            hablar("Buscando en wikipedia, por favor espera")
            solicitud = solicitud.replace("busca en wikipedia", "")
            wikipedia.set_lang('es')
            resultado = wikipedia.summary(solicitud, sentences=1)
            hablar("Wikipedia contiene la siguiente información")
            hablar(resultado)
            continue
        elif 'busca en internet' in solicitud:
            hablar("Buscando en internet, por favor espera")
            solicitud = solicitud.replace("busca en internet", "")
            pywhatkit.search(solicitud)
            hablar("Esto es lo que encontré")
            continue
        elif 'reproducir' in solicitud:
            hablar("Buscando para reproducir")
            solicitud = solicitud.replace("reproducir", "")
            pywhatkit.playonyt(solicitud)
            hablar(f"{nombre_usuario}, esto es lo que he encontrado, dime si requieres algo más.")
            continue
        elif 'chiste' in solicitud:
            hablar(pyjokes.get_joke('es'))
            continue
        #region Nuevos comandos de PyCharm
        elif 'qué puedes hacer' in solicitud:
            listar_comandos()
            continue
        elif 'crear proyecto de python' in solicitud:
            ruta = crear_proyecto_python()
            if ruta:
                proyecto_actual = ruta
                archivo_actual = None
                buffer_codigo = []
            continue
        elif 'abrir proyecto' in solicitud:
            ruta = abrir_proyecto(nombre_usuario)
            if ruta:
                proyecto_actual = ruta
                archivo_actual = None
                buffer_codigo = []
            continue
        elif 'crear archivo' in solicitud:
            ruta = crear_archivo(proyecto_actual)
            if ruta:
                archivo_actual = ruta
                buffer_codigo = []
            continue
        elif 'dictar código' in solicitud or 'dictar codigo' in solicitud:
            archivo_actual, buffer_codigo = dictar_codigo(proyecto_actual, archivo_actual, buffer_codigo)
            continue
        elif 'ejecutar programa' in solicitud:
            ejecutar_programa(proyecto_actual, archivo_actual, nombre_usuario)
            continue
        elif 'guardar cambios' in solicitud:
            guardar_cambios(archivo_actual, buffer_codigo)
            continue
        #endregion
        # Comando para lanzar el juego chepepresas_v5.py
        elif 'abrir juego' in solicitud or 'abre el juego' in solicitud or 'abrir el juego' in solicitud:
            abrir_juego()
            continue
        elif 'adiós' in solicitud:
            hablar(f"De acuerdo {nombre_usuario}. Me voy a descansar, cualquier cosa que necesites aqui estaré")
            break
#endregion

#region Programa Principal
#verificar_microfono()
#lenguajes_disponibles()
#transformar_audio_en_texto()
#hablar("Hola a todos")
#texto = transformar_audio_en_texto()
#hablar(texto)

#informar_dia()
#informar_hora()
#saludo('Dilana')

asistir_usuario()
#endregion