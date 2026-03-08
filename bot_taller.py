import pyodbc

# Conexión a SQL Server
def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  
        'DATABASE=taller;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )

def procesar_comando(comando, parametro=""):
    """Recibe comandos exactos desde los botones y devuelve la respuesta"""
    respuesta = ""
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        if comando == "GANANCIAS":
            cursor.execute("SELECT SUM(Price) FROM Services")
            total = cursor.fetchone()[0]
            if total:
                respuesta = f"🤖 Hasta ahora, el taller ha generado un total de ${total:,.2f}."
            else:
                respuesta = "🤖 Aún no hay servicios registrados con precio."

        elif comando == "TOTAL_CLIENTES":
            cursor.execute("SELECT COUNT(*) FROM Customers")
            total_clientes = cursor.fetchone()[0]
            respuesta = f"🤖 Actualmente tienes {total_clientes} clientes registrados en el sistema."
            
        elif comando == "TOTAL_AUTOS":
            cursor.execute("SELECT COUNT(*) FROM Carts")
            total_autos = cursor.fetchone()[0]
            respuesta = f"🤖 Hay {total_autos} vehículos registrados en el taller."

        elif comando == "BUSCAR_CLIENTE":
            # Separa lo que el usuario escribió (Ej: "Juan Perez" -> ["Juan", "Perez"])
            palabras = parametro.split()
            
            # Preparcion de la consulta base
            consulta_sql = "SELECT Name, LastName, Cellphone FROM Customers WHERE "
            condiciones = []
            parametros_sql = []
            
            # Exige que cada palabra exista en el Nombre O en el Apellido
            for palabra in palabras:
                condiciones.append("(Name LIKE ? OR LastName LIKE ?)")
                parametros_sql.extend([f'%{palabra}%', f'%{palabra}%'])
            
            # Se unen las condiciones con "AND"
            consulta_sql += " AND ".join(condiciones)
            
            cursor.execute(consulta_sql, parametros_sql)
            resultados = cursor.fetchall()
            
            if resultados:
                respuesta = f"🤖 Encontré esto sobre '{parametro}':\n"
                for row in resultados:
                    respuesta += f"   👤 {row[0]} {row[1]} - 📞 Tel: {row[2]}\n"
            else:
                respuesta = f"🤖 No encontré a ningún cliente llamado '{parametro}'."
            
        conn.close()
    except Exception as e:
        respuesta = f"🤖 Ups, tuve un error al revisar la base de datos: {e}"
        
    return respuesta