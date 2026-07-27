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


def dibujar_productividad_semanal(contenedor, semanas=8):
    for widget in contenedor.winfo_children(): widget.destroy()
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute(
            "SELECT DATEADD(WEEK, DATEDIFF(WEEK, 0, O.OrderDate), 0) AS Semana, "
            "S.Worker, SUM(S.Price) "
            "FROM Services S JOIN Orders O ON S.Id_Order = O.Id_Order "
            "WHERE S.Price IS NOT NULL AND S.Worker IS NOT NULL "
            "AND O.OrderDate >= DATEADD(WEEK, ?, CAST(GETDATE() AS DATE)) "
            "GROUP BY DATEADD(WEEK, DATEDIFF(WEEK, 0, O.OrderDate), 0), S.Worker "
            "ORDER BY Semana", (-(semanas - 1),))
        filas = cursor.fetchall()
        conn.close()

        if not filas:
            ctk.CTkLabel(contenedor, text="Sin datos suficientes para mostrar productividad semanal.",
                         text_color=COLOR_TEXT_MAIN, font=("Segoe UI", 11)).pack(pady=30)
            return

        semanas_lista = sorted({row[0] for row in filas})
        mecanicos = sorted({row[1] for row in filas})
        datos = {mec: [0.0] * len(semanas_lista) for mec in mecanicos}
        for semana, worker, total in filas:
            datos[worker][semanas_lista.index(semana)] = float(total)

        etiquetas_semana = [s.strftime("%d-%b") for s in semanas_lista]

        plt.rcParams['text.color'] = COLOR_TEXT_MAIN
        plt.rcParams['axes.labelcolor'] = COLOR_TEXT_MAIN
        plt.rcParams['font.family'] = 'Segoe UI'

        fig = Figure(figsize=(15, 4.6), dpi=100, facecolor=COLOR_BG_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLOR_BG_CARD)

        x = list(range(len(semanas_lista)))
        base = [0.0] * len(semanas_lista)
        for i, mec in enumerate(mecanicos):
            valores = datos[mec]
            ax.bar(x, valores, bottom=base, label=mec, color=PALETA[i % len(PALETA)], width=0.55)
            base = [b + v for b, v in zip(base, valores)]

        ax.set_xticks(x)
        ax.set_xticklabels(etiquetas_semana, color=COLOR_TEXT_MAIN, fontsize=9)
        ax.set_title("PRODUCTIVIDAD SEMANAL POR MECÁNICO", color=COLOR_TEXT_MAIN,
                      fontweight="bold", fontsize=11, pad=14)
        ax.tick_params(axis='y', colors=COLOR_TEXT_MAIN, labelsize=8)
        ax.grid(axis='y', color=COLOR_BORDER, linewidth=0.6, alpha=0.6)
        ax.set_axisbelow(True)
        for s in ax.spines.values(): s.set_visible(False)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=min(len(mecanicos), 5),
                  fontsize=8, frameon=False, labelcolor=COLOR_TEXT_MAIN)

        fig.tight_layout(pad=2.5)
        canvas = FigureCanvasTkAgg(fig, master=contenedor)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)

    except Exception as e:
        ctk.CTkLabel(contenedor, text=f"Fallo al cargar productividad semanal: {e}", text_color="#ef4444").pack(pady=30)
