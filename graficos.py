import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from conexion import conectar

# Paleta sincronizada con cruz.py
COLOR_BG_CARD = "#1e293b"    # Slate 800
COLOR_ACCENT = "#6366f1"     # Indigo 500
COLOR_TEXT_MAIN = "#f8fafc"  # Slate 50
COLOR_BORDER = "#475569"     # Slate 600

def dibujar_profesional(contenedor):
    for widget in contenedor.winfo_children(): widget.destroy()
    try:
        conn = conectar(); cursor = conn.cursor()
        
        cursor.execute("SELECT Worker, SUM(Price) FROM Services WHERE Price IS NOT NULL GROUP BY Worker")
        datos_ganancias = cursor.fetchall()
        mecanicos = [row[0] for row in datos_ganancias] if datos_ganancias else ["Sin datos"]
        ganancias = [float(row[1]) for row in datos_ganancias] if datos_ganancias else [0]
        
        cursor.execute("SELECT Make, COUNT(*) FROM Carts GROUP BY Make")
        datos_marcas = cursor.fetchall()
        marcas = [row[0] for row in datos_marcas] if datos_marcas else ["N/A"]
        cantidades = [int(row[1]) for row in datos_marcas] if datos_marcas else [1]
        conn.close()

        fig = Figure(figsize=(12, 6), dpi=100, facecolor=COLOR_BG_CARD) 
        
        plt.rcParams['text.color'] = COLOR_TEXT_MAIN
        plt.rcParams['axes.labelcolor'] = COLOR_TEXT_MAIN

        # Barras
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(COLOR_BG_CARD)
        ax1.bar(mecanicos, ganancias, color=COLOR_ACCENT)
        ax1.set_title('Productividad Financiera', color=COLOR_TEXT_MAIN, fontweight="bold", fontsize=14)
        ax1.tick_params(axis='both', colors=COLOR_TEXT_MAIN)
        for s in ax1.spines.values(): s.set_edgecolor(COLOR_BORDER)
        
        # Pay
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(COLOR_BG_CARD)
        colors = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#0ea5e9']
        ax2.pie(cantidades, labels=marcas, autopct='%1.1f%%', colors=colors, textprops={'color':COLOR_TEXT_MAIN})
        ax2.set_title('Composición de Flota', color=COLOR_TEXT_MAIN, fontweight="bold", fontsize=14)
        
        fig.tight_layout() 
        canvas = FigureCanvasTkAgg(fig, master=contenedor)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        
    except Exception as e:
        ctk.CTkLabel(contenedor, text=f"Fallo al cargar analíticas: {e}", text_color="#ef4444").pack(pady=30)