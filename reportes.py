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

def crear_pdf_profesional(id_order):
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("""SELECT O.Id_Order, O.VIN, O.OrderDate, O.TotalAmount, Cu.Name, Cu.LastName
                          FROM Orders O JOIN Customers Cu ON O.Id_Customer = Cu.Id_Customer
                          WHERE O.Id_Order = ?""", (id_order,))
        orden = cursor.fetchone()
        if not orden:
            conn.close()
            return False, "La orden no existe."

        vehiculo = None
        if orden[1]:
            cursor.execute("SELECT Make, Model FROM Carts WHERE VIN = ?", (orden[1],))
            vehiculo = cursor.fetchone()

        cursor.execute("""SELECT COALESCE(I.PartName, 'Servicio general') AS Descripcion,
                                  S.Price, COUNT(*) AS Cantidad
                          FROM Services S
                          LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                          WHERE S.Id_Order = ?
                          GROUP BY COALESCE(I.PartName, 'Servicio general'), S.Price
                          ORDER BY MIN(S.Id_Service)""", (id_order,))
        lineas = cursor.fetchall()
        conn.close()

        pdf = PDF_Profesional()
        pdf.add_page()
        pdf.ln(35)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"ORDEN FOLIO: #{orden[0]}", ln=True)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

        # Datos en blanco y gris limpio
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"CLIENTE: {orden[4]} {orden[5]}", ln=True)
        if vehiculo:
            pdf.cell(0, 8, f"VEHÍCULO: {vehiculo[0]} {vehiculo[1]} (VIN: {orden[1]})", ln=True)
        fecha = orden[2].strftime('%d/%m/%Y') if orden[2] else "—"
        pdf.cell(0, 8, f"FECHA: {fecha}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(80, 8, "DESCRIPCIÓN", border='B')
        pdf.cell(25, 8, "CANT.", border='B', align='C')
        pdf.cell(35, 8, "VALOR UNIT.", border='B', align='R')
        pdf.cell(40, 8, "VALOR TOTAL", border='B', ln=True, align='R')
        pdf.set_font("Arial", '', 10)
        total_general = 0
        for descripcion, precio_unitario, cantidad in lineas:
            precio_unitario = precio_unitario if precio_unitario is not None else 0
            valor_total = precio_unitario * cantidad
            total_general += valor_total
            pdf.cell(80, 8, str(descripcion))
            pdf.cell(25, 8, str(cantidad), align='C')
            pdf.cell(35, 8, f"$ {precio_unitario:,.2f}", align='R')
            pdf.cell(40, 8, f"$ {valor_total:,.2f}", ln=True, align='R')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 15, f"TOTAL A PAGAR: $ {total_general:,.2f}", border=1, ln=True, align='C')

        nombre = f"Orden_{orden[0]}.pdf"
        pdf.output(nombre)
        os.startfile(nombre)
        return True, "Reporte Generado con éxito"
    except Exception as e: return False, str(e)