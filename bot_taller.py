import requests
import json
from conexion import conectar

def obtener_contexto_bd():
    """Obtiene un resumen de los datos actuales de la BD para dárselo al bot"""
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Clientes
        cursor.execute("SELECT Id_Customer, Name, LastName, Cellphone FROM Customers")
        clientes = cursor.fetchall()
        
        # Autos
        cursor.execute("SELECT VIN, Make, Model, ModelYear, Color, Id_Customer FROM Carts")
        autos = cursor.fetchall()
        
        # Servicios
        cursor.execute("SELECT Id_Service, ReplacedPart, Duration, Price, Worker, VIN FROM Services")
        servicios = cursor.fetchall()
        
        conn.close()
        
        ctx = "DATOS ACTUALES DE LA BASE DE DATOS DEL TALLER:\n\n"
        
        ctx += "=== CLIENTES ===\n"
        for c in clientes:
            ctx += f"ID:{c[0]} | {c[1]} {c[2]} | Tel: {c[3]}\n"
        
        ctx += "\n=== VEHÍCULOS (Carts) ===\n"
        for a in autos:
            ctx += f"VIN:{a[0]} | {a[1]} {a[2]} {a[3]} | Color:{a[4]} | ID_Cliente:{a[5]}\n"
        
        ctx += "\n=== SERVICIOS / ÓRDENES ===\n"
        for s in servicios:
            ctx += f"ID:{s[0]} | Trabajo:{s[1]} | Duración:{s[2]} | Precio:${s[3]} | Mecánico:{s[4]} | VIN:{s[5]}\n"
        
        return ctx
    except Exception as e:
        return f"Error al leer BD: {str(e)}"

def procesar_lenguaje_natural(texto_usuario):
    """Llama a la API de Claude con el contexto completo de la BD"""
    
    contexto_bd = obtener_contexto_bd()
    
    system_prompt = f"""Eres el asistente inteligente del "Taller Cruz PRO". 
Tu trabajo es responder preguntas sobre los datos del taller de forma clara y útil en español.

Tienes acceso completo a los datos actuales del taller:

{contexto_bd}

INSTRUCCIONES:
- Responde SIEMPRE en español
- Usa los datos reales de la BD que se te proporcionaron arriba
- Para relacionar tablas: Customers.Id_Customer = Carts.Id_Customer, Carts.VIN = Services.VIN
- Si preguntan por el "último servicio", busca el de ID más alto
- Sé conciso pero informativo
- Si no encuentras datos, dilo claramente
- Usa emojis ocasionalmente para hacer la respuesta más amigable (🔧 🚗 👤 💰)
- Nunca inventes datos que no estén en la BD"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": texto_usuario}
                ]
            }
        )
        
        data = response.json()
        
        if "content" in data and len(data["content"]) > 0:
            return data["content"][0]["text"]
        elif "error" in data:
            return f"Error de API: {data['error'].get('message', 'Error desconocido')}"
        else:
            return "No pude obtener una respuesta del sistema de IA."
            
    except Exception as e:
        return f"Error de conexión con IA: {str(e)}"