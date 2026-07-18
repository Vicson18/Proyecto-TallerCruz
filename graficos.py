import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_ACCENT, COLOR_ACCENT2, COLOR_SUCCESS,
                     COLOR_TEXT_MAIN, COLOR_BORDER)

PALETA = [COLOR_ACCENT, COLOR_ACCENT2, COLOR_SUCCESS, "#0ea5e9", "#a78bfa", "#f472b6"]


def dibujar_profesional(contenedor):
    for widget in contenedor.winfo_children(): widget.destroy()
    try:
        conn = conectar(); cursor = conn.cursor()

        cursor.execute(
            "SELECT Worker, SUM(Price) FROM Services WHERE Price IS NOT NULL "
            "GROUP BY Worker ORDER BY SUM(Price) DESC")
        datos_ganancias = cursor.fetchall()
        mecanicos = [row[0] for row in datos_ganancias] if datos_ganancias else ["Sin datos"]
        ganancias = [float(row[1]) for row in datos_ganancias] if datos_ganancias else [0]

        cursor.execute("SELECT Make, COUNT(*) FROM Carts GROUP BY Make ORDER BY COUNT(*) DESC")
        datos_marcas = cursor.fetchall()
        marcas = [row[0] for row in datos_marcas] if datos_marcas else ["N/A"]
        cantidades = [int(row[1]) for row in datos_marcas] if datos_marcas else [1]

        cursor.execute(
            "SELECT TOP 5 I.PartName, COUNT(*) c FROM Services S "
            "JOIN Inventory I ON S.Id_Part = I.Id_Part "
            "GROUP BY I.PartName ORDER BY c DESC")
        datos_top = cursor.fetchall()
        repuestos = [row[0] for row in datos_top] if datos_top else ["Sin datos"]
        repuestos_cant = [int(row[1]) for row in datos_top] if datos_top else [0]
        conn.close()

        plt.rcParams['text.color'] = COLOR_TEXT_MAIN
        plt.rcParams['axes.labelcolor'] = COLOR_TEXT_MAIN
        plt.rcParams['font.family'] = 'Segoe UI'

        fig = Figure(figsize=(15, 6), dpi=100, facecolor=COLOR_BG_CARD)

        # 1. Productividad financiera por mecánico
        ax1 = fig.add_subplot(131)
        ax1.set_facecolor(COLOR_BG_CARD)
        barras1 = ax1.bar(mecanicos, ganancias, color=COLOR_ACCENT, width=0.6)
        ax1.set_title("PRODUCTIVIDAD POR MECÁNICO", color=COLOR_TEXT_MAIN,
                       fontweight="bold", fontsize=11, pad=14)
        ax1.tick_params(axis='x', colors=COLOR_TEXT_MAIN, labelsize=9, rotation=15)
        ax1.tick_params(axis='y', colors=COLOR_TEXT_MAIN, labelsize=8)
        ax1.grid(axis='y', color=COLOR_BORDER, linewidth=0.6, alpha=0.6)
        ax1.set_axisbelow(True)
        for s in ax1.spines.values(): s.set_visible(False)
        for b in barras1:
            h = b.get_height()
            ax1.text(b.get_x() + b.get_width() / 2, h, f"${h:,.0f}", ha='center', va='bottom',
                      color=COLOR_TEXT_MAIN, fontsize=8, fontweight="bold")

        # 2. Composición de flota (dona, con leyenda)
        ax2 = fig.add_subplot(132)
        ax2.set_facecolor(COLOR_BG_CARD)
        wedges, _, _ = ax2.pie(
            cantidades, autopct='%1.0f%%', pctdistance=0.82, startangle=90,
            colors=PALETA, textprops={'color': "#ffffff", 'fontsize': 8, 'fontweight': 'bold'},
            wedgeprops={'width': 0.42, 'edgecolor': COLOR_BG_CARD, 'linewidth': 2})
        ax2.set_title("COMPOSICIÓN DE FLOTA", color=COLOR_TEXT_MAIN,
                       fontweight="bold", fontsize=11, pad=14)
        ax2.legend(wedges, marcas, loc="upper center", bbox_to_anchor=(0.5, -0.02),
                   ncol=3, fontsize=8, frameon=False, labelcolor=COLOR_TEXT_MAIN)

        # 3. Servicios/repuestos más solicitados
        ax3 = fig.add_subplot(133)
        ax3.set_facecolor(COLOR_BG_CARD)
        y_pos = list(range(len(repuestos)))
        barras3 = ax3.barh(y_pos, repuestos_cant, color=COLOR_ACCENT2, height=0.5)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(repuestos, color=COLOR_TEXT_MAIN, fontsize=9)
        ax3.invert_yaxis()
        ax3.set_title("TOP SERVICIOS SOLICITADOS", color=COLOR_TEXT_MAIN,
                       fontweight="bold", fontsize=11, pad=14)
        ax3.tick_params(axis='x', colors=COLOR_TEXT_MAIN, labelsize=8)
        ax3.grid(axis='x', color=COLOR_BORDER, linewidth=0.6, alpha=0.6)
        ax3.set_axisbelow(True)
        for s in ax3.spines.values(): s.set_visible(False)
        for b in barras3:
            w = b.get_width()
            ax3.text(w, b.get_y() + b.get_height() / 2, f" {int(w)}", va='center',
                      color=COLOR_TEXT_MAIN, fontsize=8, fontweight="bold")

        fig.tight_layout(pad=2.5)
        canvas = FigureCanvasTkAgg(fig, master=contenedor)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)

    except Exception as e:
        ctk.CTkLabel(contenedor, text=f"Fallo al cargar analíticas: {e}", text_color="#ef4444").pack(pady=30)
