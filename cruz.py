import customtkinter as ctk

import estado
from estilo import (COLOR_BG_BASE, COLOR_BG_CARD, COLOR_ACCENT, COLOR_TEXT_MAIN,
                     COLOR_TEXT_DIM, BTN_TOP_NAV, configurar_estilo_tablas, animar_entrada)
from Frame_Login import FrameLogin
from Frame_IA import FrameIA
from Frame_Clientes import FrameClientes
from Frame_Flota import FrameFlota
from Frame_Ordenes import FrameOrdenes
from Frame_Metricas import FrameMetricas

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def abrir_menu_principal(ventana_login):
    ventana_menu = ctk.CTkToplevel()
    ventana_menu.protocol("WM_DELETE_WINDOW", ventana_login.destroy)
    ventana_menu.title("Cruz PRO — Sistema de Gestión Automotriz")
    ventana_menu.geometry("1500x900")
    ventana_menu.configure(fg_color=COLOR_BG_BASE)
    configurar_estilo_tablas()

    # ── TOP BAR ──────────────────────────────────────────────
    top_bar = ctk.CTkFrame(ventana_menu, fg_color=COLOR_BG_CARD, height=64, corner_radius=0)
    top_bar.pack(side="top", fill="x")
    top_bar.pack_propagate(False)
    ctk.CTkFrame(top_bar, fg_color=COLOR_ACCENT, height=3, corner_radius=0).pack(side="bottom", fill="x")

    logo_f = ctk.CTkFrame(top_bar, fg_color="transparent")
    logo_f.pack(side="left", padx=28, pady=10)
    ctk.CTkLabel(logo_f, text="⬡ ", font=("Arial", 20), text_color=COLOR_ACCENT).pack(side="left")
    ctk.CTkLabel(logo_f, text="CRUZ", font=("Segoe UI", 19, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
    ctk.CTkLabel(logo_f, text=" PRO", font=("Segoe UI", 19, "bold"), text_color=COLOR_ACCENT).pack(side="left")
    ctk.CTkLabel(logo_f, text="  //  SISTEMA DE GESTIÓN", font=("Segoe UI", 10),
                 text_color=COLOR_TEXT_DIM).pack(side="left", padx=(8, 0))

    nav_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    nav_frame.pack(side="right", padx=12)

    container_main = ctk.CTkFrame(ventana_menu, fg_color="transparent")
    container_main.pack(expand=True, fill="both")

    paginas = {}

    def ir_a(nombre, btn):
        for b in btns.values():
            b.configure(text_color=COLOR_TEXT_DIM, fg_color="transparent")
        btn.configure(text_color="#ffffff", fg_color="#1a0000")
        for p in paginas.values(): p.pack_forget()
        paginas[nombre].pack(expand=True, fill="both")

    btns = {}
    secciones = [("bot","⬡  IA"), ("cli","👤  CLIENTES"), ("au","🚗  FLOTA"),
                 ("ser","🔧  ÓRDENES"), ("dash","📊  MÉTRICAS")]
    for id_p, txt in secciones:
        btns[id_p] = ctk.CTkButton(nav_frame, text=txt,
                                    command=lambda i=id_p: ir_a(i, btns[i]),
                                    width=130, height=64, **BTN_TOP_NAV)
        btns[id_p].pack(side="left", padx=0)

    for p in ["bot", "cli", "au", "ser", "dash"]:
        paginas[p] = ctk.CTkFrame(container_main, fg_color=COLOR_BG_BASE, corner_radius=0)

    FrameIA(paginas["bot"])
    FrameClientes(paginas["cli"])
    FrameFlota(paginas["au"])
    FrameOrdenes(paginas["ser"])
    FrameMetricas(paginas["dash"])

    # ── INIT ──────────────────────────────────────────────────
    estado.actualizar_datos_precarga()
    ir_a("bot", btns["bot"])
    animar_entrada(ventana_menu)


def main():
    FrameLogin(on_success=abrir_menu_principal).run()


if __name__ == "__main__":
    main()
