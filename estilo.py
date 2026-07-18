import time
import customtkinter as ctk
from tkinter import ttk

import estado

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG_BASE      = "#0a0a0a"
COLOR_BG_CARD      = "#111111"
COLOR_BG_CARD_ALT  = "#1a1a1a"
COLOR_BG_INPUT     = "#1e1e1e"
COLOR_ACCENT       = "#e52222"
COLOR_ACCENT_DIM   = "#7a1010"
COLOR_ACCENT2      = "#f0a500"
COLOR_TEXT_MAIN    = "#f0f0f0"
COLOR_TEXT_DIM     = "#888888"
COLOR_BORDER       = "#2a2a2a"
COLOR_SUCCESS      = "#22c55e"
COLOR_DANGER       = "#e52222"

ENTRY_STYLE = {
    "fg_color": COLOR_BG_INPUT,
    "text_color": COLOR_TEXT_MAIN,
    "border_color": COLOR_BORDER,
    "border_width": 1,
    "corner_radius": 4,
    "font": ("Segoe UI", 13)
}

LABEL_STYLE = {
    "font": ("Segoe UI", 10, "bold"),
    "text_color": COLOR_TEXT_DIM
}

BTN_TOP_NAV = {
    "fg_color": "transparent",
    "text_color": COLOR_TEXT_DIM,
    "hover_color": "#1e1e1e",
    "corner_radius": 0,
    "font": ("Segoe UI", 12, "bold"),
    "border_width": 0,
}

popup_lista = None


def animar_entrada(ventana):
    ventana.attributes("-alpha", 0.0)
    for i in range(1, 11):
        if ventana.winfo_exists():
            ventana.attributes("-alpha", i / 10)
            ventana.update()
            time.sleep(0.01)


def efecto_maquina_escribir(textbox, texto, tag, entry_widget, index=0):
    if index == 0:
        textbox.configure(state="normal")
        entry_widget.configure(state="disabled")
    if not textbox.winfo_exists(): return
    if index < len(texto):
        textbox.insert("end", texto[index], tag)
        textbox.see("end")
        textbox.after(8, efecto_maquina_escribir, textbox, texto, tag, entry_widget, index + 1)
    else:
        textbox.configure(state="disabled")
        entry_widget.configure(state="normal")
        entry_widget.focus()


def configurar_estilo_tablas():
    style = ttk.Style()
    style.theme_use("default")
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
    style.configure("Treeview",
                    background=COLOR_BG_CARD,
                    foreground=COLOR_TEXT_MAIN,
                    rowheight=42,
                    fieldbackground=COLOR_BG_CARD,
                    borderwidth=0,
                    font=("Segoe UI", 12))
    style.map('Treeview',
              background=[('selected', COLOR_ACCENT)],
              foreground=[('selected', "#ffffff")])
    style.configure("Treeview.Heading",
                    background="#1a1a1a",
                    foreground=COLOR_ACCENT,
                    relief="flat",
                    padding=(10, 12),
                    font=("Segoe UI", 12, "bold"))


def configurar_combobox_oscuro(root):
    style = ttk.Style()
    style.configure("Dark.TCombobox",
                    fieldbackground=COLOR_BG_INPUT,
                    background=COLOR_BG_INPUT,
                    foreground=COLOR_TEXT_MAIN,
                    arrowcolor=COLOR_ACCENT,
                    bordercolor=COLOR_BORDER,
                    lightcolor=COLOR_BG_INPUT,
                    darkcolor=COLOR_BG_INPUT,
                    padding=6)
    style.map("Dark.TCombobox",
              fieldbackground=[('readonly', COLOR_BG_INPUT)],
              foreground=[('readonly', COLOR_TEXT_MAIN)],
              background=[('readonly', COLOR_BG_INPUT)])
    root.option_add("*TCombobox*Listbox.background", COLOR_BG_INPUT)
    root.option_add("*TCombobox*Listbox.foreground", COLOR_TEXT_MAIN)
    root.option_add("*TCombobox*Listbox.selectBackground", COLOR_ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))


def hacer_boton_accion(parent, texto, color, comando, icono=""):
    texto_completo = f"{icono}  {texto}" if icono else texto
    return ctk.CTkButton(parent, text=texto_completo, fg_color=color,
                         hover_color=COLOR_ACCENT_DIM if color == COLOR_ACCENT else color,
                         text_color=COLOR_TEXT_MAIN, corner_radius=4, height=42,
                         font=("Segoe UI", 12, "bold"), command=comando)


def mostrar_autocomplete(entry_widget, tipo):
    global popup_lista
    if popup_lista and popup_lista.winfo_exists(): popup_lista.destroy()
    texto = entry_widget.get().lower()
    if not texto: return
    opciones = []
    if tipo == "cliente":
        opciones = [c[1] for c in estado.lista_clientes_data if texto in c[1].lower()]
    elif tipo == "auto":
        opciones = [str(v) for v in estado.lista_autos_vin if texto in str(v).lower()]
    elif tipo == "parte":
        opciones = [p[1] for p in estado.lista_inventario_data if texto in p[1].lower()]
    opciones = opciones[:5]
    if not opciones: return
    x = entry_widget.winfo_rootx()
    y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
    popup_lista = ctk.CTkToplevel(entry_widget)
    popup_lista.wm_overrideredirect(True)
    popup_lista.geometry(f"{entry_widget.winfo_width()}x{len(opciones)*38+8}+{x}+{y}")
    popup_lista.configure(fg_color=COLOR_BG_INPUT)
    f_int = ctk.CTkFrame(popup_lista, fg_color="transparent", corner_radius=4,
                         border_width=1, border_color=COLOR_ACCENT)
    f_int.pack(fill="both", expand=True, padx=1, pady=1)
    def seleccionar(op):
        entry_widget.delete(0, 'end'); entry_widget.insert(0, op); popup_lista.destroy()
    for op in opciones:
        ctk.CTkButton(f_int, text=op, fg_color="transparent", text_color=COLOR_TEXT_MAIN,
                      hover_color="#2a0000", anchor="w", height=34, font=("Segoe UI", 12),
                      command=lambda o=op: seleccionar(o)).pack(fill="x", padx=4, pady=1)
