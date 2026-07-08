import re
import unicodedata
from conexion import conectar

# ============================================================
# UTILIDADES
# ============================================================
def normalizar(texto):
    """Minúsculas, sin acentos, sin puntuación"""
    texto = texto.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    for ch in "¿?¡!.,;:": texto = texto.replace(ch, "")
    return texto

def extraer_nombre(texto_limpio, palabras_clave):
    """Elimina las palabras clave y palabras basura, devuelve lo que queda como nombre"""
    resultado = texto_limpio
    for clave in sorted(palabras_clave, key=len, reverse=True):
        resultado = resultado.replace(clave, "")
    basura = {"a", "el", "la", "los", "las", "de", "del", "al", "por",
              "un", "una", "me", "que", "le", "se", "fue", "hizo",
              "cual", "cuando", "cuanto", "quien", "como", "cuantos",
              "ultimo", "ultima", "servicio", "servicios", "reparacion",
              "tiene", "tienen", "son", "es", "hay", "nuestro", "nuestra",
              "vin", "vehiculo", "auto", "carro", "cliente", "mecanico",
              "veces", "vez", "historial", "registro", "registros"}
    palabras = [p for p in resultado.split() if p not in basura and len(p) > 1]
    return " ".join(palabras).strip()

# ============================================================
# AYUDA — lista de comandos disponibles
# ============================================================
AYUDA = """Puedo responder estas consultas:

👤 CLIENTES
  • "busca a [nombre]"
  • "teléfono de [nombre]"
  • "cuántos clientes hay"

🚗 VEHÍCULOS
  • "qué autos tiene [nombre]"
  • "cuántos autos hay"
  • "busca el vin [número/texto]"

🔧 SERVICIOS
  • "último servicio de [nombre]"
  • "historial del vin [vin]"
  • "servicios de [nombre]"
  • "cuándo se le hizo [trabajo] a [nombre]"

💰 FINANZAS
  • "cuánto hemos facturado"
  • "ganancias totales"
  • "quién es el mejor mecánico"

Escribe "ayuda" en cualquier momento para ver esta lista."""

# ============================================================
# CONSULTAS A LA BASE DE DATOS
# ============================================================
def db_buscar_cliente(nombre):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT Name, LastName, Cellphone 
                      FROM Customers 
                      WHERE Name LIKE ? OR LastName LIKE ?""",
                   (f'%{nombre}%', f'%{nombre}%'))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_autos_de_cliente(nombre):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT C.VIN, C.Make, C.Model, C.ModelYear, C.Color,
                             Cu.Name, Cu.LastName
                      FROM Carts C
                      JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer
                      WHERE Cu.Name LIKE ? OR Cu.LastName LIKE ?""",
                   (f'%{nombre}%', f'%{nombre}%'))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_ultimo_servicio(nombre):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT TOP 1 S.ReplacedPart, S.Duration, S.Price,
                             S.Worker, C.Make, C.Model, Cu.Name, Cu.LastName, S.VIN
                      FROM Services S
                      JOIN Carts C ON S.VIN = C.VIN
                      JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer
                      WHERE Cu.Name LIKE ? OR Cu.LastName LIKE ?
                      ORDER BY S.Id_Service DESC""",
                   (f'%{nombre}%', f'%{nombre}%'))
    row = cursor.fetchone(); conn.close()
    return row

def db_historial_vin(vin):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT S.Id_Service, S.ReplacedPart, S.Duration, S.Price, S.Worker
                      FROM Services S
                      WHERE S.VIN = ?
                      ORDER BY S.Id_Service DESC""", (vin,))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_todos_servicios_cliente(nombre):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT S.ReplacedPart, S.Price, S.Worker, C.Make, C.Model
                      FROM Services S
                      JOIN Carts C ON S.VIN = C.VIN
                      JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer
                      WHERE Cu.Name LIKE ? OR Cu.LastName LIKE ?
                      ORDER BY S.Id_Service DESC""",
                   (f'%{nombre}%', f'%{nombre}%'))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_servicio_especifico(trabajo, nombre):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT TOP 1 S.ReplacedPart, S.Price, S.Worker,
                             C.Make, C.Model, Cu.Name, Cu.LastName
                      FROM Services S
                      JOIN Carts C ON S.VIN = C.VIN
                      JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer
                      WHERE (Cu.Name LIKE ? OR Cu.LastName LIKE ?)
                        AND S.ReplacedPart LIKE ?
                      ORDER BY S.Id_Service DESC""",
                   (f'%{nombre}%', f'%{nombre}%', f'%{trabajo}%'))
    row = cursor.fetchone(); conn.close()
    return row

def db_total_clientes():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Customers")
    n = cursor.fetchone()[0]; conn.close()
    return n

def db_total_autos():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Carts")
    n = cursor.fetchone()[0]; conn.close()
    return n

def db_ganancias():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT SUM(Price) FROM Services WHERE Price IS NOT NULL")
    total = cursor.fetchone()[0]; conn.close()
    return total

def db_mejor_mecanico():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT TOP 1 Worker, COUNT(*) as Servicios, SUM(Price) as Total
                      FROM Services
                      WHERE Worker IS NOT NULL
                      GROUP BY Worker
                      ORDER BY Total DESC""")
    row = cursor.fetchone(); conn.close()
    return row

def db_buscar_vin(vin):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT C.VIN, C.Make, C.Model, C.ModelYear, C.Color,
                             Cu.Name, Cu.LastName
                      FROM Carts C
                      JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer
                      WHERE C.VIN LIKE ?""", (f'%{vin}%',))
    rows = cursor.fetchall(); conn.close()
    return rows

# ============================================================
# MOTOR DE INTENCIONES
# ============================================================
INTENCIONES = [
    # (id, [palabras clave que deben aparecer en el texto])
    ("AYUDA",            ["ayuda", "help", "que puedes", "que sabes", "comandos"]),
    ("GANANCIAS",        ["facturado", "ganancia", "ganancias", "ingreso", "ingresos",
                          "dinero", "total cobrado", "total facturado"]),
    ("MEJOR_MECANICO",   ["mejor mecanico", "mecanico estrella", "mas trabaja",
                          "mas factura", "quien es el mejor"]),
    ("TOTAL_CLIENTES",   ["cuantos clientes", "total clientes", "numero de clientes",
                          "clientes hay", "clientes tenemos"]),
    ("TOTAL_AUTOS",      ["cuantos autos", "cuantos vehiculos", "cuantos carros",
                          "total de autos", "autos hay", "vehiculos hay"]),
    ("SERVICIO_ESP",     ["cuando se le hizo", "ultima vez que se le hizo",
                          "cuando le hicieron", "se le hizo"]),
    ("ULTIMO_SERVICIO",  ["ultimo servicio de", "ultima reparacion de",
                          "ultimo trabajo de", "que se le hizo a"]),
    ("HISTORIAL_VIN",    ["historial del vin", "historial vin", "servicios del vin",
                          "reparaciones del vin", "que le hicimos al vin"]),
    ("SERVICIOS_CLI",    ["servicios de", "reparaciones de", "historial de",
                          "trabajos de", "que servicios tiene"]),
    ("AUTOS_CLIENTE",    ["que autos tiene", "autos de", "vehiculos de",
                          "carros de", "que carros tiene", "que vehiculos tiene"]),
    ("BUSCAR_VIN",       ["busca el vin", "buscar vin", "vin:", "numero vin"]),
    ("BUSCAR_CLIENTE",   ["busca a", "buscar a", "busca cliente", "telefono de",
                          "numero de", "contacto de", "informacion de", "datos de"]),
]

def detectar_intencion(texto_norm):
    """Devuelve (intencion, clave_encontrada) o (None, None)"""
    for intent_id, claves in INTENCIONES:
        for clave in sorted(claves, key=len, reverse=True):
            if clave in texto_norm:
                return intent_id, clave
    return None, None

# ============================================================
# PROCESADOR PRINCIPAL
# ============================================================
def procesar_lenguaje_natural(texto_usuario):
    if not texto_usuario.strip():
        return "Escribe algo para comenzar. Puedes escribir 'ayuda' para ver qué puedo hacer."

    texto_norm = normalizar(texto_usuario)

    # Detección de intención
    intencion, clave = detectar_intencion(texto_norm)

    if intencion is None:
        return (
            "No entendí esa consulta. Escribe 'ayuda' para ver los comandos disponibles.\n\n"
            "Ejemplos rápidos:\n"
            "  • 'último servicio de Juan'\n"
            "  • 'qué autos tiene Carlos'\n"
            "  • 'cuánto hemos facturado'"
        )

    try:
        # ── AYUDA ────────────────────────────────────────────
        if intencion == "AYUDA":
            return AYUDA

        # ── ESTADÍSTICAS SIMPLES ─────────────────────────────
        elif intencion == "GANANCIAS":
            total = db_ganancias()
            if total:
                return f"💰 El taller ha facturado un total de ${total:,.2f} en todos los servicios registrados."
            return "Aún no hay servicios con precio registrados."

        elif intencion == "MEJOR_MECANICO":
            row = db_mejor_mecanico()
            if row:
                return (f"🏆 El mecánico estrella es {row[0]}\n"
                        f"   Servicios realizados: {row[1]}\n"
                        f"   Total facturado: ${row[2]:,.2f}")
            return "Aún no hay datos suficientes de mecánicos."

        elif intencion == "TOTAL_CLIENTES":
            n = db_total_clientes()
            return f"👥 Hay {n} cliente(s) registrados en el sistema."

        elif intencion == "TOTAL_AUTOS":
            n = db_total_autos()
            return f"🚗 Hay {n} vehículo(s) registrados en la flota."

        # ── SERVICIO ESPECÍFICO ("cuándo se le hizo X a Y") ──
        elif intencion == "SERVICIO_ESP":
            # Intentar extraer trabajo y nombre con regex
            # Patrón: "se le hizo [trabajo] a [nombre]"
            m = re.search(r"se le hizo (.+?) a (.+)", texto_norm)
            if m:
                trabajo = m.group(1).strip()
                nombre = m.group(2).strip()
                # Limpiar basura del nombre
                for b in ["ultimo", "ultima", "vez", "que", "cuando"]:
                    nombre = nombre.replace(b, "").strip()
                row = db_servicio_especifico(trabajo, nombre)
                if row:
                    return (f"🔧 Último '{row[0].title()}' a {row[5]} {row[6]}:\n"
                            f"   Vehículo: {row[3]} {row[4]}\n"
                            f"   Costo: ${float(row[1]):,.2f}\n"
                            f"   Mecánico: {row[2]}")
                return f"No encontré registros de '{trabajo}' para '{nombre.title()}'."
            return "No entendí bien. Ejemplo: 'cuándo se le hizo frenos a Juan'"

        # ── ÚLTIMO SERVICIO ───────────────────────────────────
        elif intencion == "ULTIMO_SERVICIO":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿De quién? Ejemplo: 'último servicio de Juan'"
            row = db_ultimo_servicio(nombre)
            if row:
                return (f"🔧 Último servicio de {row[6]} {row[7]}:\n"
                        f"   Trabajo: {row[0]}\n"
                        f"   Vehículo: {row[4]} {row[5]}\n"
                        f"   Duración: {row[1]}\n"
                        f"   Costo: ${float(row[2]):,.2f}\n"
                        f"   Mecánico: {row[3]}")
            return f"No encontré servicios para '{nombre.title()}'."

        # ── HISTORIAL POR VIN ─────────────────────────────────
        elif intencion == "HISTORIAL_VIN":
            vin = extraer_nombre(texto_norm, [clave])
            if not vin:
                return "¿Cuál es el VIN? Ejemplo: 'historial del vin 1HGBH41JXMN109186'"
            rows = db_historial_vin(vin)
            if rows:
                resp = f"📋 Historial del VIN {vin.upper()}:\n"
                for r in rows:
                    resp += f"   🔧 #{r[0]} {r[1]} | {r[2]} | ${float(r[3]):,.2f} | {r[4]}\n"
                return resp
            return f"El VIN '{vin}' no tiene servicios registrados."

        # ── TODOS LOS SERVICIOS DE UN CLIENTE ─────────────────
        elif intencion == "SERVICIOS_CLI":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿De quién? Ejemplo: 'servicios de María'"
            rows = db_todos_servicios_cliente(nombre)
            if rows:
                resp = f"📋 Servicios registrados para '{nombre.title()}':\n"
                for r in rows:
                    resp += f"   🔧 {r[0]} en {r[3]} {r[4]} | ${float(r[1]):,.2f} | {r[2]}\n"
                return resp
            return f"No encontré servicios para '{nombre.title()}'."

        # ── AUTOS DE UN CLIENTE ───────────────────────────────
        elif intencion == "AUTOS_CLIENTE":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿De quién? Ejemplo: 'qué autos tiene Carlos'"
            rows = db_autos_de_cliente(nombre)
            if rows:
                resp = f"🚗 Vehículos de {rows[0][5]} {rows[0][6]}:\n"
                for r in rows:
                    resp += f"   • {r[1]} {r[2]} {r[3]} — Color: {r[4]} | VIN: {r[0]}\n"
                return resp
            return f"No encontré vehículos a nombre de '{nombre.title()}'."

        # ── BUSCAR VIN ────────────────────────────────────────
        elif intencion == "BUSCAR_VIN":
            vin = extraer_nombre(texto_norm, [clave])
            if not vin:
                return "¿Cuál es el VIN? Ejemplo: 'busca el vin 1HGBH'"
            rows = db_buscar_vin(vin)
            if rows:
                resp = f"🔍 Resultados para VIN '{vin.upper()}':\n"
                for r in rows:
                    resp += f"   🚗 {r[1]} {r[2]} {r[3]} | Color: {r[4]}\n"
                    resp += f"      Propietario: {r[5]} {r[6]} | VIN: {r[0]}\n"
                return resp
            return f"No encontré ningún vehículo con VIN '{vin}'."

        # ── BUSCAR CLIENTE ────────────────────────────────────
        elif intencion == "BUSCAR_CLIENTE":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿A quién busco? Ejemplo: 'busca a García'"
            rows = db_buscar_cliente(nombre)
            if rows:
                resp = f"🔍 Resultados para '{nombre.title()}':\n"
                for r in rows:
                    resp += f"   👤 {r[0]} {r[1]} — 📞 {r[2]}\n"
                return resp
            return f"No encontré a nadie llamado '{nombre.title()}' en el sistema."

    except Exception as e:
        return f"⚠️ Error al consultar la base de datos: {str(e)}"

    return "No pude procesar esa consulta."