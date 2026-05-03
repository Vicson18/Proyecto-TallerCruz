import os
import datetime
from fpdf import FPDF
from conexion import conectar

class PDF_Profesional(FPDF):
    def header(self):
        self.set_fill_color(37, 99, 235) # Azul Eléctrico
        self.rect(0, 0, 210, 35, 'F')
        self.set_y(10)
        self.set_font("Arial", 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "REPORTE TALLER CRUZ PRO", ln=True, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y')} | Página {self.page_no()}", align='C')

def crear_pdf_profesional(id_serv, repuesto, precio, vin):
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT C.Make, C.Model, Cu.Name, Cu.LastName FROM Carts C JOIN Customers Cu ON C.Id_Customer = Cu.Id_Customer WHERE C.VIN = ?", (vin,))
        res = cursor.fetchone()
        conn.close()

        pdf = PDF_Profesional()
        pdf.add_page()
        pdf.ln(35)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"SERVICIO FOLIO: #{id_serv}", ln=True)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

        # Datos en blanco y gris limpio
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"CLIENTE: {res[2]} {res[3]}", ln=True)
        pdf.cell(0, 8, f"VEHÍCULO: {res[0]} {res[1]} (VIN: {vin})", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"DESCRIPCIÓN: {repuesto}")
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 15, f"TOTAL A PAGAR: $ {precio}", border=1, ln=True, align='C')

        nombre = f"Servicio_{id_serv}.pdf"
        pdf.output(nombre)
        os.startfile(nombre)
        return True, "Reporte Generado con éxito"
    except Exception as e: return False, str(e)