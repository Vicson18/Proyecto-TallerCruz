import customtkinter as ctk

import graficos
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT, COLOR_ACCENT_DIM,
                     COLOR_ACCENT2, COLOR_SUCCESS, COLOR_TEXT_MAIN, COLOR_TEXT_DIM)


class FrameMetricas:
    def __init__(self, parent):
        self.build(parent)
        self.actualizar()

    def build(self, parent):
        dash_outer = ctk.CTkFrame(parent, fg_color="transparent")
        dash_outer.pack(expand=True, fill="both", padx=32, pady=(20, 20))

        # Header tipo tarjeta: icono + título + descripción, botón de refresco a la derecha
        dash_header = ctk.CTkFrame(dash_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                    border_width=1, border_color=COLOR_BORDER, height=60)
        dash_header.pack(fill="x", pady=(0, 16))
        dash_header.pack_propagate(False)
        ctk.CTkFrame(dash_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        dash_header_txt = ctk.CTkFrame(dash_header, fg_color="transparent")
        dash_header_txt.pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(dash_header_txt, text="📊  MÉTRICAS Y RENDIMIENTO",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(dash_header_txt, text="Panorama financiero y operativo del taller en tiempo real",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(dash_header, text="🔄  ACTUALIZAR",
                      height=36, width=140, font=("Segoe UI", 11, "bold"),
                      fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM, corner_radius=4,
                      command=self.actualizar).pack(side="right", padx=20)

        # Fila de tarjetas KPI
        kpi_row = ctk.CTkFrame(dash_outer, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 16))

        self.kpi_clientes = self._kpi_card(kpi_row, "👤", "CLIENTES REGISTRADOS", COLOR_ACCENT)
        self.kpi_vehiculos = self._kpi_card(kpi_row, "🚗", "VEHÍCULOS EN FLOTA", COLOR_ACCENT2)
        self.kpi_ordenes = self._kpi_card(kpi_row, "🔧", "ÓRDENES REALIZADAS", COLOR_SUCCESS)
        self.kpi_ingresos = self._kpi_card(kpi_row, "💰", "INGRESOS TOTALES", COLOR_ACCENT2)

        # Pestañas: producción total vs. producción semanal
        self.tabs = ctk.CTkTabview(dash_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                    border_width=1, border_color=COLOR_BORDER,
                                    segmented_button_selected_color=COLOR_ACCENT,
                                    segmented_button_selected_hover_color=COLOR_ACCENT_DIM,
                                    text_color=COLOR_TEXT_MAIN)
        self.tabs.pack(expand=True, fill="both")
        tab_total = self.tabs.add("📊  PRODUCCIÓN TOTAL")
        tab_semanal = self.tabs.add("🗓️  PRODUCCIÓN SEMANAL")

        self.f_graf = ctk.CTkFrame(tab_total, fg_color=COLOR_BG_CARD, corner_radius=6)
        self.f_graf.pack(expand=True, fill="both", padx=2, pady=2)

        self.f_graf_semanal = ctk.CTkFrame(tab_semanal, fg_color=COLOR_BG_CARD, corner_radius=6)
        self.f_graf_semanal.pack(expand=True, fill="both", padx=2, pady=2)

    def _kpi_card(self, parent, icono, titulo, color_barra):
        card = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=6,
                             border_width=1, border_color=COLOR_BORDER, height=88)
        card.pack(side="left", expand=True, fill="both", padx=(0, 12))
        card.pack_propagate(False)
        ctk.CTkFrame(card, fg_color=color_barra, height=3, corner_radius=0).pack(fill="x", side="top")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=16, pady=(8, 10))

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", anchor="w")
        ctk.CTkLabel(top_row, text=icono, font=("Segoe UI", 15)).pack(side="left")
        ctk.CTkLabel(top_row, text=titulo, font=("Segoe UI", 10, "bold"),
                     text_color=COLOR_TEXT_DIM).pack(side="left", padx=(8, 0))

        lbl_valor = ctk.CTkLabel(inner, text="—", font=("Segoe UI", 24, "bold"), text_color=COLOR_TEXT_MAIN)
        lbl_valor.pack(anchor="w", pady=(4, 0))
        return lbl_valor

    def actualizar(self):
        self._actualizar_kpis()
        graficos.dibujar_profesional(self.f_graf)
        graficos.dibujar_productividad_semanal(self.f_graf_semanal)

    def _actualizar_kpis(self):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Customers")
            total_clientes = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Carts")
            total_vehiculos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Services")
            total_ordenes = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(Price) FROM Services WHERE Price IS NOT NULL")
            ingresos = cursor.fetchone()[0] or 0
            conn.close()

            self.kpi_clientes.configure(text=f"{total_clientes:,}")
            self.kpi_vehiculos.configure(text=f"{total_vehiculos:,}")
            self.kpi_ordenes.configure(text=f"{total_ordenes:,}")
            self.kpi_ingresos.configure(text=f"${float(ingresos):,.2f}")
        except Exception as e:
            print(e)
