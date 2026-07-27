from conexion import conectar

lista_clientes_data = []
lista_autos_vin = []
lista_inventario_data = []


def actualizar_datos_precarga():
    global lista_clientes_data, lista_autos_vin, lista_inventario_data
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Customer, Name, LastName FROM Customers")
        lista_clientes_data = [(r[0], f"{r[1]} {r[2]} (ID:{r[0]})") for r in cursor.fetchall()]
        cursor.execute("SELECT VIN FROM Carts")
        lista_autos_vin = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT Id_Part, PartName, Stock, Price FROM Inventory WHERE IsDeleted = 0")
        lista_inventario_data = [(r[0], r[1], r[2], float(r[3])) for r in cursor.fetchall()]
        conn.close()
    except: pass
