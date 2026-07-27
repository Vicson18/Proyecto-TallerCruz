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

def formato_fecha(fecha):
    """Formatea una fecha de la BD como 'dd/mm/aaaa'; si es None (servicios
    antiguos registrados antes de tener esta columna) indica que no hay fecha."""
    if not fecha:
        return "Fecha no registrada"
    return fecha.strftime("%d/%m/%Y")

def condicion_nombre(nombre, alias="Cu"):
    """Genera una condición SQL que exige que cada palabra escrita por el
    usuario aparezca en el Name o en el LastName del cliente (en cualquier
    orden). Así 'Juan Perez' encuentra al cliente con Name='Juan' y
    LastName='Perez' aunque ninguna columna por separado contenga el texto
    completo."""
    prefijo = f"{alias}." if alias else ""
    tokens = [t for t in nombre.split() if t]
    if not tokens:
        return "1=0", []
    partes, params = [], []
    for t in tokens:
        partes.append(f"({prefijo}Name LIKE ? OR {prefijo}LastName LIKE ?)")
        params.extend([f"%{t}%", f"%{t}%"])
    return " AND ".join(partes), params

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

📦 INVENTARIO
  • "stock de [refacción]"
  • "precio de [refacción]"
  • "qué refacciones tienen poco stock"
  • "cuántas refacciones hay"

📋 ÓRDENES
  • "detalle de la orden [número]"

💰 FINANZAS
  • "cuánto hemos facturado"
  • "ganancias totales"
  • "quién es el mejor mecánico"

Escribe "ayuda" en cualquier momento para ver esta lista."""

# ============================================================
# CONSULTAS A LA BASE DE DATOS
# ============================================================
def db_clientes_coincidentes(nombre):
    """Devuelve TODOS los clientes que coinciden con el nombre buscado
    (reconociendo nombre y apellido juntos). Sirve para detectar cuando
    hay más de un cliente con el mismo nombre."""
    cond, params = condicion_nombre(nombre, alias="")
    conn = conectar(); cursor = conn.cursor()
    cursor.execute(f"""SELECT Id_Customer, Name, LastName, Cellphone
                      FROM Customers
                      WHERE {cond}""", params)
    rows = cursor.fetchall(); conn.close()
    return rows

def db_autos_de_cliente_id(id_customer):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT VIN, Make, Model, ModelYear, Color
                      FROM Carts
                      WHERE Id_Customer = ?""", (id_customer,))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_ultimo_servicio_id(id_customer):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT TOP 1 COALESCE(I.PartName, 'Servicio general'), S.Duration, S.Price,
                             S.Worker, COALESCE(C.Make, ''), COALESCE(C.Model, ''), O.VIN, S.InsertedDate
                      FROM Services S
                      JOIN Orders O ON S.Id_Order = O.Id_Order
                      LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                      LEFT JOIN Carts C ON O.VIN = C.VIN
                      WHERE O.Id_Customer = ?
                      ORDER BY S.Id_Service DESC""", (id_customer,))
    row = cursor.fetchone(); conn.close()
    return row

def db_historial_vin(vin):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT S.Id_Service, COALESCE(I.PartName, 'Servicio general'), S.Duration, S.Price, S.Worker, S.InsertedDate
                      FROM Services S
                      JOIN Orders O ON S.Id_Order = O.Id_Order
                      LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                      WHERE O.VIN = ?
                      ORDER BY S.Id_Service DESC""", (vin,))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_todos_servicios_cliente_id(id_customer):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT COALESCE(I.PartName, 'Servicio general'), S.Price, S.Worker,
                             COALESCE(C.Make, ''), COALESCE(C.Model, ''), S.InsertedDate
                      FROM Services S
                      JOIN Orders O ON S.Id_Order = O.Id_Order
                      LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                      LEFT JOIN Carts C ON O.VIN = C.VIN
                      WHERE O.Id_Customer = ?
                      ORDER BY S.Id_Service DESC""", (id_customer,))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_servicio_especifico(trabajo, nombre):
    cond, params = condicion_nombre(nombre, alias="Cu")
    conn = conectar(); cursor = conn.cursor()
    cursor.execute(f"""SELECT TOP 1 COALESCE(I.PartName, 'Servicio general'), S.Price, S.Worker,
                             COALESCE(C.Make, ''), COALESCE(C.Model, ''), Cu.Name, Cu.LastName, S.InsertedDate
                      FROM Services S
                      JOIN Orders O ON S.Id_Order = O.Id_Order
                      JOIN Customers Cu ON O.Id_Customer = Cu.Id_Customer
                      LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                      LEFT JOIN Carts C ON O.VIN = C.VIN
                      WHERE ({cond})
                        AND COALESCE(I.PartName, '') LIKE ?
                      ORDER BY S.Id_Service DESC""",
                   params + [f'%{trabajo}%'])
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

def db_stock_parte(nombre):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT PartName, Stock, Price FROM Inventory
                      WHERE IsDeleted = 0 AND PartName LIKE ?
                      ORDER BY PartName""", (f'%{nombre}%',))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_stock_bajo(umbral=3):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT PartName, Stock FROM Inventory
                      WHERE IsDeleted = 0 AND Stock <= ?
                      ORDER BY Stock ASC""", (umbral,))
    rows = cursor.fetchall(); conn.close()
    return rows

def db_total_inventario():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(Stock) FROM Inventory WHERE IsDeleted = 0")
    row = cursor.fetchone(); conn.close()
    return row

def db_orden_detalle(id_order):
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("""SELECT O.Id_Order, Cu.Name, Cu.LastName, O.VIN, O.OrderDate, O.TotalAmount
                      FROM Orders O JOIN Customers Cu ON O.Id_Customer = Cu.Id_Customer
                      WHERE O.Id_Order = ?""", (id_order,))
    orden = cursor.fetchone()
    if not orden:
        conn.close()
        return None, []
    cursor.execute("""SELECT COALESCE(I.PartName, 'Servicio general'), S.Duration, S.Price, S.Worker
                      FROM Services S
                      LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                      WHERE S.Id_Order = ?
                      ORDER BY S.Id_Service""", (id_order,))
    servicios = cursor.fetchall(); conn.close()
    return orden, servicios

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
    ("ORDEN_DETALLE",    ["detalle de la orden", "detalle de orden", "total de la orden",
                          "la orden numero", "orden numero", "ver la orden"]),
    ("STOCK_BAJO",       ["poco stock", "stock bajo", "bajo stock", "refacciones agotandose",
                          "refacciones por acabarse", "que se esta acabando", "que esta por acabarse"]),
    ("TOTAL_INVENTARIO", ["cuantas refacciones hay", "total de refacciones", "refacciones tenemos",
                          "cuantas piezas hay", "inventario total", "cuanto inventario hay"]),
    ("PRECIO_PARTE",     ["precio de", "cuanto cuesta", "cuanto vale"]),
    ("STOCK_PARTE",      ["stock de", "cuantas hay de", "hay stock de", "cuanto stock hay de",
                          "cuanto hay de", "cuantas quedan de"]),
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

        # ── INVENTARIO ────────────────────────────────────────
        elif intencion == "TOTAL_INVENTARIO":
            total_partes, total_stock = db_total_inventario()
            total_stock = total_stock or 0
            return (f"📦 Hay {total_partes} refacción(es) registrada(s) en inventario, "
                    f"con {total_stock} unidad(es) en stock en total.")

        elif intencion == "STOCK_BAJO":
            rows = db_stock_bajo()
            if not rows:
                return "✅ No hay refacciones con poco stock (todas tienen más de 3 unidades disponibles)."
            resp = "⚠️ Refacciones con poco stock:\n"
            for nombre, stock in rows:
                resp += f"   📦 {nombre} — quedan {stock} unidad(es)\n"
            return resp.strip()

        elif intencion == "STOCK_PARTE":
            parte = extraer_nombre(texto_norm, [clave])
            if not parte:
                return "¿De qué refacción? Ejemplo: 'stock de balata delantera'"
            rows = db_stock_parte(parte)
            if not rows:
                return f"No encontré ninguna refacción llamada '{parte.title()}' en inventario."
            resp = f"📦 Stock de refacciones que coinciden con '{parte.title()}':\n"
            for nombre, stock, precio in rows:
                resp += f"   • {nombre} — {stock} unidad(es) disponibles — ${float(precio):,.2f} c/u\n"
            return resp.strip()

        elif intencion == "PRECIO_PARTE":
            parte = extraer_nombre(texto_norm, [clave])
            if not parte:
                return "¿De qué refacción? Ejemplo: 'precio de balata delantera'"
            rows = db_stock_parte(parte)
            if not rows:
                return f"No encontré ninguna refacción llamada '{parte.title()}' en inventario."
            resp = f"💲 Precio de refacciones que coinciden con '{parte.title()}':\n"
            for nombre, stock, precio in rows:
                resp += f"   • {nombre} — ${float(precio):,.2f} (stock disponible: {stock})\n"
            return resp.strip()

        # ── ÓRDENES ───────────────────────────────────────────
        elif intencion == "ORDEN_DETALLE":
            m = re.search(r"(\d+)", texto_norm)
            if not m:
                return "¿Cuál es el número de orden? Ejemplo: 'detalle de la orden 12'"
            id_order = int(m.group(1))
            orden, servicios = db_orden_detalle(id_order)
            if not orden:
                return f"No encontré ninguna orden con el número {id_order}."
            total = orden[5] if orden[5] is not None else 0
            vin_txt = orden[3] or "sin vehículo asociado"
            resp = (f"📋 Orden #{orden[0]}\n"
                    f"   Cliente: {orden[1]} {orden[2]}\n"
                    f"   VIN: {vin_txt}\n"
                    f"   Fecha: {formato_fecha(orden[4])}\n"
                    f"   Total: ${total:,.2f}\n")
            if servicios:
                resp += "   Servicios:\n"
                for nombre, duracion, precio, worker in servicios:
                    precio_txt = f"${float(precio):,.2f}" if precio is not None else "$0.00"
                    resp += f"      🔧 {nombre} | {duracion or '—'} | {precio_txt} | {worker}\n"
            else:
                resp += "   Sin servicios registrados todavía.\n"
            return resp.strip()

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
                    return (f"🔧 '{row[0].title()}' a {row[5]} {row[6]}:\n"
                            f"   Vehículo: {row[3]} {row[4]}\n"
                            f"   Costo: ${float(row[1]):,.2f}\n"
                            f"   Mecánico: {row[2]}\n"
                            f"   Fecha: {formato_fecha(row[7])}")
                return f"No encontré registros de '{trabajo}' para '{nombre.title()}'."
            return "No entendí bien. Ejemplo: 'cuándo se le hizo frenos a Juan'"

        # ── ÚLTIMO SERVICIO ───────────────────────────────────
        elif intencion == "ULTIMO_SERVICIO":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿De quién? Ejemplo: 'último servicio de Juan'"
            clientes = db_clientes_coincidentes(nombre)
            if not clientes:
                return f"No encontré servicios para '{nombre.title()}'."
            if len(clientes) == 1:
                cid, nom, ape, _ = clientes[0]
                row = db_ultimo_servicio_id(cid)
                if not row:
                    return f"No encontré servicios para '{nombre.title()}'."
                return (f"🔧 Último servicio de {nom} {ape}:\n"
                        f"   Trabajo: {row[0]}\n"
                        f"   Vehículo: {row[4]} {row[5]}\n"
                        f"   Duración: {row[1]}\n"
                        f"   Costo: ${float(row[2]):,.2f}\n"
                        f"   Mecánico: {row[3]}\n"
                        f"   Fecha: {formato_fecha(row[7])}")
            resp = f"🔍 Encontré {len(clientes)} clientes que coinciden con '{nombre.title()}':\n\n"
            for cid, nom, ape, tel in clientes:
                row = db_ultimo_servicio_id(cid)
                resp += f"👤 {nom} {ape} (📞 {tel}):\n"
                if row:
                    resp += (f"   🔧 {row[0]} — {row[4]} {row[5]} | "
                             f"${float(row[2]):,.2f} | {row[3]} | {formato_fecha(row[7])}\n")
                else:
                    resp += "   Sin servicios registrados.\n"
                resp += "\n"
            return resp.strip()

        # ── HISTORIAL POR VIN ─────────────────────────────────
        elif intencion == "HISTORIAL_VIN":
            vin = extraer_nombre(texto_norm, [clave])
            if not vin:
                return "¿Cuál es el VIN? Ejemplo: 'historial del vin 1HGBH41JXMN109186'"
            rows = db_historial_vin(vin)
            if rows:
                resp = f"📋 Historial del VIN {vin.upper()}:\n"
                for r in rows:
                    resp += f"   🔧 #{r[0]} {r[1]} | {r[2]} | ${float(r[3]):,.2f} | {r[4]} | {formato_fecha(r[5])}\n"
                return resp
            return f"El VIN '{vin}' no tiene servicios registrados."

        # ── TODOS LOS SERVICIOS DE UN CLIENTE ─────────────────
        elif intencion == "SERVICIOS_CLI":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿De quién? Ejemplo: 'servicios de María'"
            clientes = db_clientes_coincidentes(nombre)
            if not clientes:
                return f"No encontré servicios para '{nombre.title()}'."
            if len(clientes) == 1:
                cid, nom, ape, _ = clientes[0]
                rows = db_todos_servicios_cliente_id(cid)
                if not rows:
                    return f"No encontré servicios para '{nombre.title()}'."
                resp = f"📋 Servicios registrados para {nom} {ape}:\n"
                for r in rows:
                    resp += f"   🔧 {r[0]} en {r[3]} {r[4]} | ${float(r[1]):,.2f} | {r[2]} | {formato_fecha(r[5])}\n"
                return resp
            resp = f"🔍 Encontré {len(clientes)} clientes que coinciden con '{nombre.title()}':\n\n"
            for cid, nom, ape, tel in clientes:
                rows = db_todos_servicios_cliente_id(cid)
                resp += f"👤 {nom} {ape} (📞 {tel}):\n"
                if rows:
                    for r in rows:
                        resp += f"   🔧 {r[0]} en {r[3]} {r[4]} | ${float(r[1]):,.2f} | {r[2]} | {formato_fecha(r[5])}\n"
                else:
                    resp += "   Sin servicios registrados.\n"
                resp += "\n"
            return resp.strip()

        # ── AUTOS DE UN CLIENTE ───────────────────────────────
        elif intencion == "AUTOS_CLIENTE":
            nombre = extraer_nombre(texto_norm, [clave])
            if not nombre:
                return "¿De quién? Ejemplo: 'qué autos tiene Carlos'"
            clientes = db_clientes_coincidentes(nombre)
            if not clientes:
                return f"No encontré vehículos a nombre de '{nombre.title()}'."
            if len(clientes) == 1:
                cid, nom, ape, _ = clientes[0]
                autos = db_autos_de_cliente_id(cid)
                if not autos:
                    return f"No encontré vehículos a nombre de '{nombre.title()}'."
                resp = f"🚗 Vehículos de {nom} {ape}:\n"
                for r in autos:
                    resp += f"   • {r[1]} {r[2]} {r[3]} — Color: {r[4]} | VIN: {r[0]}\n"
                return resp
            # Varios clientes coinciden (p.ej. mismo nombre y apellido):
            # se muestra la respuesta con ambos clientes y sus respectivos autos.
            resp = f"🔍 Encontré {len(clientes)} clientes que coinciden con '{nombre.title()}':\n\n"
            for cid, nom, ape, tel in clientes:
                autos = db_autos_de_cliente_id(cid)
                resp += f"👤 {nom} {ape} (📞 {tel}):\n"
                if autos:
                    for r in autos:
                        resp += f"   • {r[1]} {r[2]} {r[3]} — Color: {r[4]} | VIN: {r[0]}\n"
                else:
                    resp += "   Sin vehículos registrados.\n"
                resp += "\n"
            return resp.strip()

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
            clientes = db_clientes_coincidentes(nombre)
            if clientes:
                resp = f"🔍 Resultados para '{nombre.title()}':\n"
                for cid, nom, ape, tel in clientes:
                    resp += f"   👤 {nom} {ape} — 📞 {tel}\n"
                return resp
            return f"No encontré a nadie llamado '{nombre.title()}' en el sistema."

    except Exception as e:
        return f"⚠️ Error al consultar la base de datos: {str(e)}"

    return "No pude procesar esa consulta."