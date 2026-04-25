#region Librerias del Asistente
import pyttsx3 #Libreria para el motor de voz de nuestro asistente
import speech_recognition as sr #Libreria para el reconocimiento de voz
import pywhatkit #Libreria para busquedas en internet
import webbrowser #Para interactuar con el navegador
import datetime #Para datos de fecha y hora
import wikipedia #Para interactuar con wikipedia
import pyjokes #para chistes y bromas
import subprocess #Para ejecutar procesos externos (PyCharm, Python, venv)
import os #Para manejo de archivos y directorios
import sys #Para obtener el interprete de Python actual al lanzar el juego
#endregion

#region Configuracion de rutas
# Ruta del ejecutable de PyCharm (ajustar segun instalacion)
RUTA_PYCHARM = r"C:\Program Files\JetBrains\PyCharm 2025.3.3\bin\pycharm64.exe"
# Ruta base por defecto para proyectos Python
RUTA_BASE_PROYECTOS = r"D:\2026\PrograFinal\Proyecto final\Proyecto Radio y Borrachos\Proyecto"
# Archivo del juego que el asistente puede ejecutar bajo demanda
JUEGO_PY = "chepepresas_v5.py"
#endregion

# Voz por defecto del asistente (español Mexico - Sabina)
idioma3 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0'

#region 1 MICROFONOS DISPONIBLES
#Funcion para verificar que el microfono está disponible
def verificar_microfono():
    """Verifica y lista todos los microfonos conectados al sistema"""
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
    """Muestra en consola todas las voces instaladas en el sistema operativo
    y define las rutas de registro de los idiomas disponibles"""
    motor_voz = pyttsx3.init()

    # Recorre e imprime cada voz instalada en el sistema
    for voz in motor_voz.getProperty('voices'):
        print(voz)

    # Rutas de registro de Windows para cada idioma disponible
    idioma1 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0'
    idioma2 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
    idioma3 = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0'
#endregion

#region 3 CAPTURAR AUDIO DESDE MICROFONO
#Funcion que permite capturar el audio del micrófono y convertirlo en texto
def transformar_audio_en_texto():
    """Escucha al usuario por el microfono y convierte lo que dice a texto
    usando el servicio de reconocimiento de Google en español de Costa Rica.
    Retorna el texto reconocido o 'Intenta de nuevo' si falla."""
    reconocimiento_voz = sr.Recognizer()

    try:
        with sr.Microphone() as origen:
            #Ajustar el umbral de ruido ambiente
            reconocimiento_voz.adjust_for_ambient_noise(origen, duration=1)
            # Tiempo maximo de pausa antes de cortar la escucha
            reconocimiento_voz.pause_threshold = 3
            # Limite de tiempo maximo para una frase
            reconocimiento_voz.phrase_time_limit = 15
            print("Por favor hable al micrófono ahora......")
            audio = reconocimiento_voz.listen(origen)
            #Intentar reconocer lo que solicita el usuario
            solicitud = reconocimiento_voz.recognize_google(audio, language="es-CR")
            print("Audio reconocido: " + solicitud)
            return solicitud
    except sr.UnknownValueError:
        # No se pudo entender lo que dijo el usuario
        print("Lo siento, no entendi tu solicitud, intenta de nuevo!!!!")
        return "Intenta de nuevo"
    except sr.RequestError as e:
        # Fallo de conexion con el servicio de reconocimiento de voz
        print(f"Error de conexión al servicio de reconocimiento {e}, intenta de nuevo!!!")
        return "Intenta de nuevo"
    except Exception as e:
        # Cualquier otro error inesperado
        print(f"Error inesperado {e}, intenta de nuevo!!!")
        return "Intenta de nuevo"
#endregion

#region 4 REPRODUCIR VOZ
#Funcion que permite al asistente ser escuchado, capacidad de hablar
def hablar(mensaje):
    """Recibe un texto y lo reproduce como voz usando el motor pyttsx3
    con la voz configurada en idioma3 (español Mexico)"""
    #Encender el motor de pyttsx3
    motor_voz = pyttsx3.init()

    # Asignar la voz en español al motor
    motor_voz.setProperty('voice', idioma3)

    #pronunciar o hablar el contenido del mensaje
    motor_voz.say(mensaje)

    # Esperar a que termine de hablar antes de continuar
    motor_voz.runAndWait()

#Funcion para comunicar el dia de la semana
def informar_dia():
    """Obtiene la fecha actual del sistema y le dice al usuario
    que dia de la semana es hoy mediante voz"""
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

#Funcion para comunicar la hora actual
def informar_hora():
    """Obtiene la hora actual del sistema y la comunica al usuario
    indicando horas, minutos y segundos"""
    #variable para los datos de la hora
    hora_actual = datetime.datetime.now()
    print(hora_actual)

    # Formatear el mensaje con la hora completa
    hora_actual = (f'En este momento son las {hora_actual.hour} horas con {hora_actual.minute} minutos y {hora_actual.second} segundos')

    hablar(hora_actual)

#Funcion para saludar segun la hora de ejecucion
def saludo(nombre):
    """Genera un saludo personalizado segun la hora del dia:
    - Antes de las 6am o despues de las 7pm: Buenas noches
    - De 6am a 12pm: Buenos dias
    - De 12pm a 7pm: Buenas tardes"""
    hora_actual = datetime.datetime.now()

    # Determinar el saludo segun el rango de horas
    if hora_actual.hour < 6 or hora_actual.hour>=19:
        msj_saludo='Buenas noches'
    elif hora_actual.hour>=6 and hora_actual.hour<12:
        msj_saludo = 'Buenos dias'
    else:
        msj_saludo = 'Buenas tardes'

    hablar(f'Hola {msj_saludo} {nombre}. Cómo te puedo ayudar hoy?')
#endregion

#region 5 FUNCIONES DE ASISTENCIA VIRTUAL
def asistir_usuario():
    """Funcion principal del asistente virtual Nova.
    Inicia la interaccion con el usuario, le pide su nombre,
    lo saluda y entra en un bucle infinito donde escucha comandos
    de voz y ejecuta la accion correspondiente segun la solicitud."""
    hablar("Bienvenido")
    hablar("Mi nombre es Nova, soy tu asistente virtual")
    hablar("Por favor, dime tu nombre")
    # Capturar el nombre del usuario por voz
    nombre_usuario = transformar_audio_en_texto().lower()
    saludo(nombre_usuario)

    # Variables de estado para manejo de proyectos y archivos
    proyecto_actual = None  # Ruta del proyecto activo
    archivo_actual = None   # Ruta del archivo en edicion
    contenido_codigo = []   # Contenido del archivo en memoria

    #variable para el control del bucle
    iniciar = True

    while iniciar:
        #Activar el microfono para capturar la solicitud del usuario
        solicitud = transformar_audio_en_texto().lower()

        #Evaluamos la peticion del usuario para encontrar coincidencias de tipos de solicitud

        # Comando: abrir youtube en el navegador
        if 'abrir youtube' in solicitud:
            hablar(f"Con gusto {nombre_usuario}, aqui tienes Youtube")
            webbrowser.open("https://www.youtube.com")
            continue
        # Comando: abrir el navegador en Google
        elif 'abrir navegador' in solicitud:
            hablar(f"Claro {nombre_usuario}, acabo de abrir el navegador, dime si necesitas algo más")
            webbrowser.open("https://www.google.com")
            continue
        # Comando: consultar que dia de la semana es
        elif 'qué dia es hoy' in solicitud:
            informar_dia()
            continue
        # Comando: consultar la hora actual
        elif 'qué hora es' in solicitud:
            informar_hora()
            continue
        # Comando: buscar informacion en Wikipedia
        elif 'busca en wikipedia' in solicitud:
            hablar("Buscando en wikipedia, por favor espera")
            # Quitar el comando para dejar solo el termino de busqueda
            solicitud = solicitud.replace("busca en wikipedia", "")
            wikipedia.set_lang('es')
            resultado = wikipedia.summary(solicitud, sentences=1)
            hablar("Wikipedia contiene la siguiente información")
            hablar(resultado)
            continue
        # Comando: buscar algo en internet con Google
        elif 'busca en internet' in solicitud:
            hablar("Buscando en internet, por favor espera")
            solicitud = solicitud.replace("busca en internet", "")
            pywhatkit.search(solicitud)
            hablar("Esto es lo que encontré")
            continue
        # Comando: reproducir un video en YouTube
        elif 'reproducir' in solicitud:
            hablar("Buscando para reproducir")
            solicitud = solicitud.replace("reproducir", "")
            pywhatkit.playonyt(solicitud)
            hablar(f"{nombre_usuario}, esto es lo que he encontrado, dime si requieres algo más.")
            continue
        # Comando: contar un chiste en español
        elif 'chiste' in solicitud:
            hablar(pyjokes.get_joke('es'))
            continue
        #region Nuevos comandos de PyCharm
        # Comando: listar todos los comandos disponibles
        elif 'qué puedes hacer' in solicitud:
            listar_comandos()
            continue
        # Comando: crear un nuevo proyecto de Python
        elif 'crear proyecto de python' in solicitud:
            ruta = crear_proyecto_python()
            if ruta:
                proyecto_actual = ruta
                archivo_actual = None
                contenido_codigo = []
            continue
        # Comando: abrir un proyecto existente en PyCharm
        elif 'abrir proyecto' in solicitud:
            ruta = abrir_proyecto(nombre_usuario)
            if ruta:
                proyecto_actual = ruta
                archivo_actual = None
                contenido_codigo = []
            continue
        # Comando: crear un archivo .py dentro del proyecto activo
        elif 'crear archivo' in solicitud:
            ruta = crear_archivo(proyecto_actual)
            if ruta:
                archivo_actual = ruta
                contenido_codigo = []
            continue
        # Comando: entrar en modo dictado de codigo por voz
        elif 'dictar código' in solicitud or 'dictar codigo' in solicitud:
            archivo_actual, contenido_codigo = dictar_codigo(proyecto_actual, archivo_actual, contenido_codigo)
            continue
        # Comando: ejecutar el archivo Python activo
        elif 'ejecutar programa' in solicitud:
            ejecutar_programa(proyecto_actual, archivo_actual, nombre_usuario)
            continue
        # Comando: guardar el contenido del buffer al archivo
        elif 'guardar cambios' in solicitud:
            guardar_cambios(archivo_actual, contenido_codigo)
            continue
        #endregion
        # Comando para lanzar el juego Chepepresas.py
        elif 'abrir juego' in solicitud or 'abre el juego' in solicitud or 'abrir el juego' in solicitud:
            abrir_juego()
            continue
        # Comando: despedirse y cerrar el asistente
        elif 'adiós' in solicitud:
            hablar(f"De acuerdo {nombre_usuario}. Me voy a descansar, cualquier cosa que necesites aqui estaré")
            break
#endregion


#region 6 FUNCIONES DE PYCHARM - Interaccion con el IDE

# Diccionario que mapea palabras dictadas por voz a los simbolos
# correspondientes de la sintaxis de Python. Permite al usuario
# dictar codigo y que el asistente lo convierta a simbolos reales.
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
    """Informa al usuario todos los comandos disponibles
    mediante voz, enumerandolos del 1 al 17"""
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
    """Pregunta al usuario algo y espera respuesta si/no.
    Retorna True si el usuario dijo 'si' o 'sí', False en caso contrario."""
    hablar(pregunta)
    respuesta = transformar_audio_en_texto().lower()
    return 'sí' in respuesta or 'si' in respuesta

def crear_proyecto_python():
    """Guia al usuario paso a paso para crear un nuevo proyecto de Python.
    Pregunta el nombre, la ubicacion, si quiere Git, script de bienvenida
    y el tipo de interprete. Crea la carpeta, el entorno virtual,
    inicializa Git si aplica y abre PyCharm con el proyecto.
    Retorna la ruta del proyecto creado o None si hubo error."""
    hablar("Vamos a crear un nuevo proyecto en Python. Dime el nombre del proyecto.")
    nombre_proyecto = transformar_audio_en_texto().lower().strip()
    # Limpiar caracteres no validos para nombre de carpeta
    nombre_proyecto = nombre_proyecto.replace(" ", "_")
    hablar(f"El proyecto se llamará {nombre_proyecto}")

    # Preguntar ubicacion donde se va a crear el proyecto
    hablar(f"La ubicación por defecto es {RUTA_BASE_PROYECTOS}. ¿Deseas usar esta ubicación?")
    respuesta_ubicacion = transformar_audio_en_texto().lower()
    if 'sí' in respuesta_ubicacion or 'si' in respuesta_ubicacion:
        ruta_proyecto = os.path.join(RUTA_BASE_PROYECTOS, nombre_proyecto)
    else:
        hablar("Dime la ruta donde quieres crear el proyecto")
        ruta_personalizada = transformar_audio_en_texto().strip()
        ruta_proyecto = os.path.join(ruta_personalizada, nombre_proyecto)

    # Preguntar opciones adicionales al usuario
    crear_git = preguntar_si_no("¿Deseas crear un repositorio Git para este proyecto?")
    crear_bienvenida = preguntar_si_no("¿Deseas crear un script de bienvenida, main punto py?")

    # Preguntar tipo de interprete de Python a usar
    hablar("¿Qué tipo de intérprete deseas? Las opciones son: project venv, uv, base conda, o custom. Di el nombre.")
    tipo_interprete = transformar_audio_en_texto().lower()

    # Crear la estructura de carpetas del proyecto
    try:
        os.makedirs(ruta_proyecto, exist_ok=True)
        hablar(f"Carpeta del proyecto creada en {ruta_proyecto}")

        # Crear entorno virtual si aplica (project venv por defecto)
        if 'conda' not in tipo_interprete and 'custom' not in tipo_interprete:
            hablar("Creando entorno virtual, esto puede tomar un momento")
            ruta_entorno_virtual = os.path.join(ruta_proyecto, '.venv')
            subprocess.run(['python', '-m', 'venv', ruta_entorno_virtual], check=True)
            hablar("Entorno virtual creado exitosamente")

        # Inicializar repositorio Git si se solicito
        if crear_git:
            subprocess.run(['git', 'init'], cwd=ruta_proyecto, check=True)
            hablar("Repositorio Git inicializado")

        # Crear script de bienvenida si se solicito
        if crear_bienvenida:
            ruta_main = os.path.join(ruta_proyecto, 'main.py')
            with open(ruta_main, 'w', encoding='utf-8') as archivo:
                archivo.write('# Proyecto: ' + nombre_proyecto + '\n')
                archivo.write('# Creado con Nova - Asistente Virtual\n\n')
                archivo.write('print("Hola mundo! Bienvenido al proyecto ' + nombre_proyecto + '")\n')
            hablar("Script de bienvenida creado")

        # Abrir PyCharm con el proyecto recien creado
        hablar("Abriendo PyCharm con tu nuevo proyecto")
        subprocess.Popen([RUTA_PYCHARM, ruta_proyecto])
        hablar("Listo, PyCharm se está abriendo con tu proyecto")

        return ruta_proyecto

    except Exception as e:
        print(f"Error al crear proyecto: {e}")
        hablar(f"Hubo un error al crear el proyecto: {e}")
        return None

def abrir_proyecto(nombre_usuario):
    """Abre un proyecto existente en PyCharm.
    Busca primero en la ruta base de proyectos, si no lo encuentra
    le da la opcion al usuario de dictar la ruta completa.
    Retorna la ruta del proyecto o None si no se encontro."""
    hablar("¿Cuál es el nombre del proyecto que deseas abrir?")
    nombre_proyecto = transformar_audio_en_texto().lower().strip().replace(" ", "_")

    # Construir la ruta completa del proyecto
    ruta_proyecto = os.path.join(RUTA_BASE_PROYECTOS, nombre_proyecto)

    # Verificar si la carpeta del proyecto existe
    if os.path.isdir(ruta_proyecto):
        hablar(f"Abriendo el proyecto {nombre_proyecto} en PyCharm")
        subprocess.Popen([RUTA_PYCHARM, ruta_proyecto])
        hablar(f"{nombre_usuario}, PyCharm se está abriendo con tu proyecto")
        return ruta_proyecto
    else:
        # El proyecto no se encontro en la ruta base
        hablar(f"No encontré el proyecto {nombre_proyecto} en la carpeta de proyectos")
        hablar("¿Deseas dictar la ruta completa?")
        respuesta = transformar_audio_en_texto().lower()
        if 'sí' in respuesta or 'si' in respuesta:
            hablar("Dime la ruta completa del proyecto")
            ruta_completa = transformar_audio_en_texto().strip()
            if os.path.isdir(ruta_completa):
                subprocess.Popen([RUTA_PYCHARM, ruta_completa])
                hablar("PyCharm se está abriendo")
                return ruta_completa
            else:
                hablar("La ruta no existe, verifica e intenta de nuevo")
        return None

def aplicar_mapeo_sintaxis(texto):
    """Recorre el diccionario MAPEO_VOZ_SINTAXIS y reemplaza cada
    palabra clave encontrada en el texto por su simbolo de Python
    correspondiente. Retorna el texto ya convertido."""
    for palabra, simbolo in MAPEO_VOZ_SINTAXIS.items():
        texto = texto.replace(palabra, simbolo)
    return texto

def crear_archivo(proyecto_actual):
    """Crea un archivo .py vacio en el proyecto activo (sin entrar al dictado).
    Si el archivo ya existe, notifica al usuario.
    Retorna la ruta del archivo creado o None si no hay proyecto activo."""
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
    """Lista los archivos .py del proyecto y permite al usuario elegir uno por voz.
    Muestra todos los archivos Python encontrados y espera que el usuario
    diga el nombre del archivo que quiere seleccionar.
    Retorna la ruta del archivo seleccionado o None si no se encontro."""
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

    # Verificar si el archivo existe en el proyecto
    if os.path.isfile(ruta_archivo):
        hablar(f"Archivo {nombre_elegido} seleccionado")
        return ruta_archivo
    else:
        hablar(f"No encontré el archivo {nombre_elegido} en el proyecto")
        return None

def dictar_codigo(proyecto_actual, archivo_actual, contenido_codigo):
    """Modo dictado independiente: permite elegir archivo y dictar codigo por voz.
    El usuario puede dictar lineas de codigo que se van agregando al contenido.
    Comandos dentro del modo dictado:
    - 'nueva linea': agrega una linea en blanco
    - 'guardar': guarda el archivo en disco
    - 'salir de dictado': guarda y sale del modo dictado
    Retorna la tupla (archivo_actual, contenido_codigo) actualizada."""
    if not proyecto_actual:
        hablar("No hay un proyecto activo. Primero crea o abre un proyecto")
        return archivo_actual, contenido_codigo

    # Preguntar si quiere usar el archivo actual o elegir otro
    if archivo_actual:
        nombre_actual = os.path.basename(archivo_actual)
        hablar(f"El archivo activo es {nombre_actual}. ¿Deseas dictar en este archivo?")
        respuesta = transformar_audio_en_texto().lower()
        if 'no' in respuesta:
            archivo_seleccionado = seleccionar_archivo(proyecto_actual)
            if not archivo_seleccionado:
                return archivo_actual, contenido_codigo
            archivo_actual = archivo_seleccionado
            # Cargar contenido existente del archivo al contenido en memoria
            with open(archivo_actual, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
                contenido_codigo = contenido.splitlines() if contenido.strip() else []
    else:
        # No hay archivo activo, debe elegir uno
        archivo_seleccionado = seleccionar_archivo(proyecto_actual)
        if not archivo_seleccionado:
            return None, []
        archivo_actual = archivo_seleccionado
        # Cargar contenido existente del archivo al contenido en memoria
        with open(archivo_actual, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            contenido_codigo = contenido.splitlines() if contenido.strip() else []

    hablar("Entrando en modo dictado de código")
    hablar("Puedes dictar tu código. Di nueva línea para saltar línea, guardar para guardar, o salir de dictado para terminar")

    # Bucle de dictado de codigo - se mantiene escuchando hasta que el usuario diga 'salir de dictado'
    while True:
        hablar("Dictando...")
        linea = transformar_audio_en_texto().lower()

        if 'salir de dictado' in linea:
            # Guardar antes de salir si hay contenido en memoria
            if contenido_codigo:
                with open(archivo_actual, 'w', encoding='utf-8') as archivo:
                    archivo.write('\n'.join(contenido_codigo) + '\n')
                hablar("Archivo guardado. Saliendo del modo dictado")
            else:
                hablar("Saliendo del modo dictado")
            break
        elif linea == 'guardar':
            # Guardar el contenido actual al archivo en disco
            with open(archivo_actual, 'w', encoding='utf-8') as archivo:
                archivo.write('\n'.join(contenido_codigo) + '\n')
            hablar("Archivo guardado exitosamente")
            continue
        elif linea == 'nueva línea' or linea == 'nueva linea':
            # Agregar una linea vacia al contenido
            contenido_codigo.append('')
            hablar("Línea en blanco agregada")
            continue
        elif linea == 'intenta de nuevo':
            # El reconocimiento fallo, simplemente continuar
            continue
        else:
            # Aplicar mapeo de voz a sintaxis Python y agregar la linea
            linea_procesada = aplicar_mapeo_sintaxis(linea)
            contenido_codigo.append(linea_procesada)
            print(f"  > {linea_procesada}")
            hablar(f"Línea agregada: {linea_procesada}")

    return archivo_actual, contenido_codigo

def ejecutar_programa(proyecto_actual, archivo_actual, nombre_usuario):
    """Ejecuta el archivo Python actual usando subprocess y lee la salida por voz.
    Captura tanto la salida estandar como los errores y los comunica al usuario.
    Tiene un timeout de 30 segundos para evitar que el programa se quede colgado."""
    if not archivo_actual:
        hablar("No hay un archivo activo para ejecutar. Primero crea o selecciona un archivo")
        return

    if not os.path.isfile(archivo_actual):
        hablar("El archivo no existe, verifica la ruta")
        return

    hablar(f"Ejecutando {os.path.basename(archivo_actual)}")
    try:
        # Ejecutar el archivo Python y capturar la salida
        resultado = subprocess.run(
            ['python', archivo_actual],
            capture_output=True, text=True, timeout=30,
            cwd=proyecto_actual
        )

        # Leer la salida estandar si existe
        if resultado.stdout:
            hablar("La salida del programa es la siguiente:")
            print(f"STDOUT:\n{resultado.stdout}")
            hablar(resultado.stdout)
        # Leer los errores si existen
        if resultado.stderr:
            hablar("Se encontraron errores:")
            print(f"STDERR:\n{resultado.stderr}")
            hablar(resultado.stderr)
        # Si no hubo ni salida ni errores
        if not resultado.stdout and not resultado.stderr:
            hablar("El programa se ejecutó sin producir salida")

    except subprocess.TimeoutExpired:
        # El programa excedio el tiempo limite de 30 segundos
        hablar("El programa tardó demasiado y fue detenido")
    except Exception as e:
        hablar(f"Error al ejecutar el programa: {e}")

def guardar_cambios(archivo_actual, contenido_codigo):
    """Guarda el contenido en memoria (lista de lineas) al archivo en disco.
    Escribe cada linea separada por saltos de linea."""
    if not archivo_actual:
        hablar("No hay un archivo activo para guardar")
        return

    try:
        with open(archivo_actual, 'w', encoding='utf-8') as archivo:
            archivo.write('\n'.join(contenido_codigo) + '\n')
        hablar(f"Archivo {os.path.basename(archivo_actual)} guardado exitosamente")
    except Exception as e:
        hablar(f"Error al guardar: {e}")

def abrir_juego(juego_py=JUEGO_PY):
    """Ejecuta el juego .py de forma bloqueante. Nova queda en pausa
    hasta que el usuario cierre el juego, luego retoma el control
    y da la bienvenida de vuelta."""
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    ruta_juego = os.path.join(directorio_base, juego_py)

    if not os.path.isfile(ruta_juego):
        hablar(f"No encontré el juego {juego_py} en la carpeta del asistente")
        return

    hablar("Abriendo el juego, disfrutalo. Te espero cuando termines")
    try:
        # run() bloquea hasta que el juego termine (ESC o cerrar ventana)
        subprocess.run([sys.executable, ruta_juego], cwd=directorio_base)
        hablar("Bienvenido de vuelta. ¿En qué te puedo ayudar?")
    except Exception as e:
        hablar(f"Error al abrir el juego: {e}")
#endregion


#region Programa Principal
# Llamadas de prueba comentadas para desarrollo
#verificar_microfono()
#lenguajes_disponibles()
#transformar_audio_en_texto()
#hablar("Hola a todos")
#texto = transformar_audio_en_texto()
#hablar(texto)

#informar_dia()
#informar_hora()
#saludo('Dilana')

# Punto de entrada: iniciar el asistente virtual Nova
asistir_usuario()
#endregion