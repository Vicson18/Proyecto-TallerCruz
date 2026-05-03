from conexion import conectar
import unicodedata
import difflib
import re

def normalizar_texto(texto):
    """Elimina acentos, signos de puntuación y pasa a minúsculas"""
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    for char in ["?", "¿", ",", ".", "!", "¡"]:
        texto = texto.replace(char, "")
    return texto

def procesar_lenguaje_natural(texto_usuario):
    """Motor NLP Ligero con Regex, Extracción de Múltiples Entidades y Fuzzy Matching"""
    texto_limpio = normalizar_texto(texto_usuario)
    
    if not texto_limpio:
        return "Por favor, escribe algo para que pueda ayudarte."

    # ========================================================
    # 1. EVALUACIÓN DE FRASES COMPLEJAS (REGEX)
    # ========================================================
    match_especifico = re.search(r"ultima vez que se (le )?hizo (.*?) a (.*)", texto_limpio)
    if match_especifico:
        servicio = match_especifico.group(2).strip()
        nombre = match_especifico.group(3).strip()
        return ejecutar_comando("ULTIMO_SERVICIO_ESPECIFICO", f"{servicio}|{nombre}")

    if "ultimo servicio de" in texto_limpio or "ultima reparacion de" in texto_limpio:
        partes = texto_limpio.split(" de ")
        nombre = partes[-1].strip() if len(partes) > 1 else ""
        if nombre:
            return ejecutar_comando("ULTIMO_SERVICIO_CLIENTE", nombre)

    # ========================================================
    # 2. EVALUACIÓN DE INTENCIONES SIMPLES (FUZZY MATCHING)
    # ========================================================
    intenciones = {
        "GANANCIAS": ["ganancia", "dinero", "cuanto", "venta", "ingreso", "caja", "total", "vendido", "cobrado", "facturado"],
        "TOTAL_CLIENTES": ["cuantos clientes", "poblacion", "registrados", "usuarios"],
        "TOTAL_AUTOS": ["cuantos autos", "vehiculos", "coches", "carros", "flota", "unidades"],
        "MEJOR_MECANICO": ["mejor", "estrella", "productivo", "destacado", "mas trabaja"],
        "BUSCAR_CLIENTE": ["busca", "buscar", "encuentra", "quien", "telefono", "celular", "contacto"],
        "AUTOS_CLIENTE": ["que autos tiene", "carros de", "vehiculos de", "propiedad de"],
        "HISTORIAL_VIN": ["historial", "servicios de", "reparaciones de", "que le hicimos", "vin"]
    }

    intencion_detectada = None
    texto_sin_clave = texto_limpio # Variable para guardar el texto sin la "frase clave"

    for intencion, claves in intenciones.items():
        # 1. Buscar coincidencia de frase exacta
        clave_encontrada = next((c for c in claves if c in texto_limpio), None)
        if clave_encontrada:
            intencion_detectada = intencion
            # ¡LA CORRECCIÓN! Borramos la frase clave detectada ("que autos tiene") para que solo quede ("juan")
            texto_sin_clave = texto_limpio.replace(clave_encontrada, "")
            break
            
        # 2. Fuzzy matching (por si hay errores ortográficos)
        for palabra in texto_limpio.split():
            if difflib.get_close_matches(palabra, claves, n=1, cutoff=0.8):
                intencion_detectada = intencion
                texto_sin_clave = texto_limpio.replace(palabra, "")
                break
        if intencion_detectada: break

    # Extracción de Entidades simples: Ahora usamos 'texto_sin_clave'
    # Agregué más "palabras basura" a ignorar para limpiar mejor el nombre
    palabras_basura = ["a", "el", "la", "los", "las", "de", "del", "por", "favor", "un", "una", "necesito", "quiero", "saber", "sobre", "vin", "auto", "cliente", "es", "son", "tiene", "que"]
    posibles_datos = [p for p in texto_sin_clave.split() if p not in palabras_basura]
    parametro_texto = " ".join(posibles_datos).strip() 

    numeros = re.findall(r'\d+', texto_limpio)
    parametro_num = numeros[0] if numeros else ""

    # ========================================================
    # 3. ENRUTAMIENTO FINAL
    # ========================================================
    if not intencion_detectada:
        return (
            "Mis sistemas no lograron interpretar eso. Intenta:\n"
            " • '¿Cuál fue el último servicio de Juan?'\n"
            " • '¿Cuándo fue la última vez que se le hizo frenos a María?'\n"
            " • '¿Qué autos tiene Carlos?'\n"
            " • 'Busca a Martinez'"
        )

    if intencion_detectada in ["GANANCIAS", "TOTAL_CLIENTES", "TOTAL_AUTOS", "MEJOR_MECANICO"]:
        return ejecutar_comando(intencion_detectada)
    elif intencion_detectada in ["BUSCAR_CLIENTE", "AUTOS_CLIENTE"]:
        if not parametro_texto: return "Necesito que me digas el nombre de la persona."
        return ejecutar_comando(intencion_detectada, parametro=parametro_texto)
    elif intencion_detectada == "HISTORIAL_VIN":
        if not parametro_num: return "Necesito que me digas el número de VIN (ej. 'historial del vin 5')."
        return ejecutar_comando(intencion_detectada, parametro=parametro_num)

def ejecutar_comando(comando, parametro=""):
    """Se conecta a la BD y ejecuta lógica de negocio con JOINs, omitiendo el uso de fechas"""
    try:
        conn = conectar()
        cursor = conn.cursor()
        respuesta = ""

        if comando == "ULTIMO_SERVICIO_CLIENTE":
            cursor.execute("""
                SELECT TOP 1 S.ReplacedPart, S.Price, C.Make, C.Model, S.Worker, Cu.Name, Cu.LastName
                FROM Services S 
                JOIN Carts C ON S.VIN = C.VIN 
                JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer 
                WHERE Cu.Name LIKE ? OR Cu.LastName LIKE ? 
                ORDER BY S.Id_Service DESC
            """, (f'%{parametro}%', f'%{parametro}%'))
            res = cursor.fetchone()
            if res:
                respuesta = f"El último servicio de {res[5]} {res[6]} fue un '{res[0]}' en su {res[2]} {res[3]}. Lo atendió {res[4]} y el costo fue de ${res[1]:,.2f}."
            else:
                respuesta = f"No encontré ningún historial de servicio a nombre de '{parametro.title()}'."

        elif comando == "ULTIMO_SERVICIO_ESPECIFICO":
            servicio, nombre = parametro.split("|")
            cursor.execute("""
                SELECT TOP 1 S.Price, C.Make, Cu.Name, Cu.LastName, S.Worker
                FROM Services S 
                JOIN Carts C ON S.VIN = C.VIN 
                JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer 
                WHERE (Cu.Name LIKE ? OR Cu.LastName LIKE ?) 
                AND S.ReplacedPart LIKE ? 
                ORDER BY S.Id_Service DESC
            """, (f'%{nombre}%', f'%{nombre}%', f'%{servicio}%'))
            res = cursor.fetchone()
            if res:
                respuesta = f"La última vez que se le hizo '{servicio.title()}' a {res[2]} {res[3]} (en su {res[1]}) cobramos ${res[0]:,.2f}. Trabajo hecho por {res[4]}."
            else:
                respuesta = f"No tengo registros de haberle hecho '{servicio}' a nadie llamado '{nombre.title()}'."

        elif comando == "GANANCIAS":
            cursor.execute("SELECT SUM(Price) FROM Services WHERE Price IS NOT NULL")
            total = cursor.fetchone()[0]
            respuesta = f"Históricamente, el taller ha facturado ${total:,.2f}." if total else "Sin ingresos registrados."

        elif comando == "TOTAL_CLIENTES":
            cursor.execute("SELECT COUNT(*) FROM Customers")
            respuesta = f"Contamos con {cursor.fetchone()[0]} clientes en el sistema."
            
        elif comando == "TOTAL_AUTOS":
            cursor.execute("SELECT COUNT(*) FROM Carts")
            respuesta = f"Hay {cursor.fetchone()[0]} vehículos registrados en la flota."

        elif comando == "MEJOR_MECANICO":
            cursor.execute("SELECT TOP 1 Worker, SUM(Price) as Generado FROM Services GROUP BY Worker ORDER BY Generado DESC")
            res = cursor.fetchone()
            respuesta = f"El mecánico estrella es 🏆 {res[0]} con ${res[1]:,.2f} facturados." if res else "Aún no hay datos de mecánicos."

        elif comando == "BUSCAR_CLIENTE":
            cursor.execute("SELECT Name, LastName, Cellphone FROM Customers WHERE Name LIKE ? OR LastName LIKE ?", (f'%{parametro}%', f'%{parametro}%'))
            resultados = cursor.fetchall()
            if resultados:
                respuesta = f"Resultados para '{parametro.title()}':\n"
                for r in resultados: respuesta += f"   👤 {r[0]} {r[1]} - 📞 {r[2]}\n"
            else:
                respuesta = f"No encontré a '{parametro.title()}' en el sistema."

        elif comando == "AUTOS_CLIENTE":
            cursor.execute("""
                SELECT C.Make, C.Model, C.Color 
                FROM Carts C JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer 
                WHERE Cu.Name LIKE ? OR Cu.LastName LIKE ?
            """, (f'%{parametro}%', f'%{parametro}%'))
            resultados = cursor.fetchall()
            if resultados:
                respuesta = f"Vehículos propiedad de '{parametro.title()}':\n"
                for r in resultados: respuesta += f"   🚗 {r[0]} {r[1]} ({r[2]})\n"
            else:
                respuesta = f"No encontré vehículos a nombre de '{parametro.title()}'."

        elif comando == "HISTORIAL_VIN":
            cursor.execute("SELECT ReplacedPart, Price, Worker FROM Services WHERE VIN = ?", (parametro,))
            resultados = cursor.fetchall()
            if resultados:
                respuesta = f"Historial del VIN {parametro}:\n"
                for r in resultados: respuesta += f"   🔧 {r[0]} | ${r[1]} | Por: {r[2]}\n"
            else:
                respuesta = f"El VIN {parametro} no tiene servicios registrados."
            
        conn.close()
        return respuesta
    except Exception as e:
        return f"Error crítico de SQL: {str(e)}"