import os
import datetime
from fpdf import FPDF
from conexion import conectar

def crear_pdf(id_servicio, repuesto, precio, vin):
    """Genera el documento PDF y devuelve un mensaje de éxito o error"""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT C.Make, C.Model, Cu.Name, Cu.LastName
            FROM Carts C
            JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer
            WHERE C.VIN = ?
        """, (vin,))
        resultado = cursor.fetchone()
        conn.close()

        if not resultado:
            return False, "No se encontraron los datos completos del cliente o auto."

        marca, modelo, nombre, apellido = resultado

        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(200, 10, txt="TALLER MECÁNICO CRUZ", ln=True, align='C')
        
        pdf.set_font("Arial", '', 10)
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        pdf.cell(200, 10, txt=f"Fecha de emisión: {fecha_actual}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="DATOS DEL CLIENTE Y VEHÍCULO:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 8, txt=f"Cliente: {nombre} {apellido}", ln=True)
        pdf.cell(200, 8, txt=f"Vehículo: {marca} {modelo} (VIN: {vin})", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="DETALLE DEL SERVICIO:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 8, txt=f"Folio de Servicio: #{id_servicio}", ln=True)
        pdf.cell(200, 8, txt=f"Descripción / Repuesto: {repuesto}", ln=True)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 15, txt=f"Total a Pagar: ${precio}", ln=True)
        pdf.ln(15)

        pdf.set_font("Arial", 'I', 12)
        pdf.cell(200, 10, txt="¡Gracias por su preferencia!", ln=True, align='C')

        nombre_archivo = f"Ticket_Servicio_{id_servicio}.pdf"
        pdf.output(nombre_archivo)

        if os.name == 'nt':
            os.startfile(nombre_archivo)
            
        return True, f"Ticket generado correctamente como '{nombre_archivo}'"

    except Exception as e:
        return False, f"No se pudo generar el ticket: {e}"