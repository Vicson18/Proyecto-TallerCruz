import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from conexion import conectar

def dibujar(contenedor):
    """Consulta la BD y dibuja las gráficas en el contenedor especificado"""
    for widget in contenedor.winfo_children():
        widget.destroy()
        
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Worker, SUM(Price) FROM Services WHERE Price IS NOT NULL GROUP BY Worker")
        datos_ganancias = cursor.fetchall()
        mecanicos = [row[0] for row in datos_ganancias] if datos_ganancias else ["Sin datos"]
        ganancias = [float(row[1]) for row in datos_ganancias] if datos_ganancias else [0]
        
        cursor.execute("SELECT Make, COUNT(*) FROM Carts GROUP BY Make")
        datos_marcas = cursor.fetchall()
        marcas = [row[0] for row in datos_marcas] if datos_marcas else ["Sin datos"]
        cantidades = [int(row[1]) for row in datos_marcas] if datos_marcas else [1]
        conn.close()

        fig = Figure(figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor('#ffffff') 
        
        ax1 = fig.add_subplot(121)
        ax1.bar(mecanicos, ganancias, color="#3498db")
        ax1.set_title('Ganancias por Mecánico', fontweight="bold")
        ax1.set_ylabel('Dinero Ingresado ($)')
        ax1.tick_params(axis='x', rotation=15) 
        
        ax2 = fig.add_subplot(122)
        colores_pastel = ['#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#34495e', '#e67e22', '#1abc9c']
        ax2.pie(cantidades, labels=marcas, autopct='%1.1f%%', startangle=90, colors=colores_pastel)
        ax2.set_title('Distribución de Marcas de Autos', fontweight="bold")
        
        fig.tight_layout() 
        
        canvas = FigureCanvasTkAgg(fig, master=contenedor)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
    except Exception as e:
        ctk.CTkLabel(contenedor, text=f"Error al cargar gráficos: {e}", text_color="#e74c3c").pack(pady=20)