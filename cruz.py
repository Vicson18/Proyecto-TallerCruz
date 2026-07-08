import customtkinter as ctk
from tkinter import messagebox, ttk
import pyodbc
import time

from conexion import conectar
import bot_taller
import reportes
import graficos

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

lista_clientes_data = []
lista_autos_vin = []
popup_lista = None
chat_scroll = None

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

def mostrar_autocomplete(entry_widget, tipo):
    global popup_lista
    if popup_lista and popup_lista.winfo_exists(): popup_lista.destroy()
    texto = entry_widget.get().lower()
    if not texto: return
    opciones = []
    if tipo == "cliente":
        opciones = [c[1] for c in lista_clientes_data if texto in c[1].lower()]
    elif tipo == "auto":
        opciones = [str(v) for v in lista_autos_vin if texto in str(v).lower()]
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

def hacer_boton_accion(parent, texto, color, comando, icono=""):
    texto_completo = f"{icono}  {texto}" if icono else texto
    return ctk.CTkButton(parent, text=texto_completo, fg_color=color,
                         hover_color=COLOR_ACCENT_DIM if color == COLOR_ACCENT else color,
                         text_color=COLOR_TEXT_MAIN, corner_radius=4, height=42,
                         font=("Segoe UI", 12, "bold"), command=comando)

# ==========================================
# CRUDs
# ==========================================
def cargar_clientes():
    for row in tree_clientes.get_children(): tree_clientes.delete(row)
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Customer, Name, LastName, Cellphone FROM Customers")
        for i, row in enumerate(cursor.fetchall()):
            tag = 'even' if i % 2 == 0 else 'odd'
            tree_clientes.insert("", "end", values=[str(v) if v is not None else "" for v in row], tags=(tag,))
        tree_clientes.tag_configure('even', background=COLOR_BG_CARD)
        tree_clientes.tag_configure('odd', background=COLOR_BG_CARD_ALT)
        conn.close()
    except Exception as e: print(e)

def guardar_cliente():
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (Name, LastName, Cellphone, InsertedDate) VALUES (?,?,?, GETDATE())",
                       (entry_name.get(), entry_lastname.get(), entry_cellphone.get()))
        conn.commit(); conn.close()
        cargar_clientes(); actualizar_datos_precarga(); limpiar_cliente()
        messagebox.showinfo("Éxito", "Cliente registrado.")
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_cliente():
    seleccion = tree_clientes.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente.")
    id_cliente = int(str(tree_clientes.item(seleccion, 'values')[0]).replace(',', ''))
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Customers SET Name=?, LastName=?, Cellphone=? WHERE Id_Customer=?",
                       (entry_name.get(), entry_lastname.get(), entry_cellphone.get(), id_cliente))
        conn.commit(); conn.close()
        messagebox.showinfo("Éxito", "Datos actualizados."); limpiar_cliente(); cargar_clientes(); actualizar_datos_precarga()
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_cliente():
    seleccion = tree_clientes.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente.")
    id_cliente = int(str(tree_clientes.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Eliminar cliente permanentemente?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Customers WHERE Id_Customer=?", (id_cliente,))
            conn.commit(); conn.close()
            limpiar_cliente(); cargar_clientes(); actualizar_datos_precarga()
        except Exception: messagebox.showerror("Error", "No se puede eliminar (tiene autos registrados).")

def limpiar_cliente():
    entry_name.delete(0, 'end'); entry_lastname.delete(0, 'end'); entry_cellphone.delete(0, 'end')

def seleccionar_cliente(event):
    item = tree_clientes.focus()
    if item:
        v = tree_clientes.item(item, 'values')
        limpiar_cliente()
        entry_name.insert(0, v[1]); entry_lastname.insert(0, v[2]); entry_cellphone.insert(0, v[3])

def cargar_autos():
    for row in tree_autos.get_children(): tree_autos.delete(row)
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT VIN, Make, Model, ModelYear, Color, Id_Customer FROM Carts")
        for i, row in enumerate(cursor.fetchall()):
            tag = 'even' if i % 2 == 0 else 'odd'
            tree_autos.insert("", "end", values=[str(v) for v in row], tags=(tag,))
        tree_autos.tag_configure('even', background=COLOR_BG_CARD)
        tree_autos.tag_configure('odd', background=COLOR_BG_CARD_ALT)
        conn.close()
    except Exception as e: print(e)

def guardar_auto():
    texto = search_customer.get()
    vin_valor = entry_vin.get().strip()
    if not vin_valor: return messagebox.showwarning("Error", "El VIN es obligatorio.")
    if "(ID:" not in texto: return messagebox.showwarning("Error", "Selecciona un cliente de la lista.")
    try:
        id_cli = int(texto.split("(ID:")[1].replace(")", ""))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Carts (VIN, Make, Model, ModelYear, Color, Id_Customer) VALUES (?,?,?,?,?,?)",
                       (vin_valor, entry_make.get(), entry_model.get(), entry_year.get(), entry_color.get(), id_cli))
        conn.commit(); conn.close(); cargar_autos(); actualizar_datos_precarga(); limpiar_auto()
        messagebox.showinfo("Éxito", "Vehículo registrado.")
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_auto():
    seleccion = tree_autos.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto.")
    vin_original = str(tree_autos.item(seleccion, 'values')[0]).replace(',', '')
    texto = search_customer.get()
    if "(ID:" not in texto: return messagebox.showwarning("Error", "Seleccione un propietario válido.")
    try:
        id_cli = int(texto.split("(ID:")[1].replace(")", ""))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Carts SET VIN=?, Make=?, Model=?, ModelYear=?, Color=?, Id_Customer=? WHERE VIN=?",
                       (entry_vin.get().strip(), entry_make.get(), entry_model.get(), entry_year.get(), entry_color.get(), id_cli, vin_original))
        conn.commit(); conn.close(); cargar_autos(); actualizar_datos_precarga(); limpiar_auto()
        messagebox.showinfo("Éxito", "Vehículo actualizado.")
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_auto():
    seleccion = tree_autos.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto.")
    vin = str(tree_autos.item(seleccion, 'values')[0]).replace(',', '')
    if messagebox.askyesno("Confirmar", "¿Eliminar vehículo del sistema?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Carts WHERE VIN=?", (vin,))
            conn.commit(); conn.close(); cargar_autos(); actualizar_datos_precarga(); limpiar_auto()
        except Exception: messagebox.showerror("Error", "No se puede eliminar (tiene servicios vinculados).")

def limpiar_auto():
    entry_vin.delete(0, 'end'); entry_make.delete(0, 'end'); entry_model.delete(0, 'end')
    entry_year.delete(0, 'end'); entry_color.delete(0, 'end'); search_customer.delete(0, 'end')

def seleccionar_auto(event):
    seleccion = tree_autos.focus()
    if seleccion:
        valores = tree_autos.item(seleccion, 'values')
        limpiar_auto()
        entry_vin.insert(0, valores[0]); entry_make.insert(0, valores[1])
        entry_model.insert(0, valores[2]); entry_year.insert(0, valores[3])
        entry_color.insert(0, valores[4])
        id_buscado = str(valores[5]).replace(',', '')
        for cli_id, cli_nombre in lista_clientes_data:
            if str(cli_id) == id_buscado:
                search_customer.insert(0, cli_nombre); break

def cargar_servicios():
    for row in tree_servicios.get_children(): tree_servicios.delete(row)
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Service, ReplacedPart, Duration, Price, Worker, VIN FROM Services")
        for i, row in enumerate(cursor.fetchall()):
            tag = 'even' if i % 2 == 0 else 'odd'
            tree_servicios.insert("", "end", values=[str(v) for v in row], tags=(tag,))
        tree_servicios.tag_configure('even', background=COLOR_BG_CARD)
        tree_servicios.tag_configure('odd', background=COLOR_BG_CARD_ALT)
        conn.close()
    except Exception as e: print(e)

def guardar_servicio():
    vin = search_vin.get()
    if not vin: return messagebox.showwarning("Error", "Escribe o selecciona un VIN.")
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Services (ReplacedPart, Duration, Price, Worker, VIN) VALUES (?,?,?,?,?)",
                       (entry_part.get(), entry_duration.get(), entry_price.get(), entry_worker.get(), vin))
        conn.commit(); conn.close(); cargar_servicios(); limpiar_servicio()
        messagebox.showinfo("Éxito", "Orden de servicio creada.")
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_servicio():
    seleccion = tree_servicios.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un servicio.")
    id_servicio = int(str(tree_servicios.item(seleccion, 'values')[0]).replace(',', ''))
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Services SET ReplacedPart=?, Duration=?, Price=?, Worker=?, VIN=? WHERE Id_Service=?",
                       (entry_part.get(), entry_duration.get(), entry_price.get(), entry_worker.get(), search_vin.get(), id_servicio))
        conn.commit(); conn.close(); cargar_servicios(); limpiar_servicio()
        messagebox.showinfo("Éxito", "Servicio modificado.")
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_servicio():
    seleccion = tree_servicios.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un servicio.")
    id_servicio = int(str(tree_servicios.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Borrar esta orden?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Services WHERE Id_Service=?", (id_servicio,))
            conn.commit(); conn.close(); cargar_servicios(); limpiar_servicio()
        except Exception as e: messagebox.showerror("Error", str(e))

def limpiar_servicio():
    entry_part.delete(0, 'end'); entry_duration.delete(0, 'end')
    entry_price.delete(0, 'end'); entry_worker.delete(0, 'end'); search_vin.delete(0, 'end')

def seleccionar_servicio(event):
    seleccion = tree_servicios.focus()
    if seleccion:
        valores = tree_servicios.item(seleccion, 'values')
        limpiar_servicio()
        entry_part.insert(0, valores[1]); entry_duration.insert(0, valores[2])
        entry_price.insert(0, valores[3]); entry_worker.insert(0, valores[4])
        search_vin.insert(0, valores[5])

def pedir_ticket_pdf():
    seleccion = tree_servicios.focus()
    if not seleccion: return messagebox.showwarning("Error", "Selecciona un servicio.")
    valores = tree_servicios.item(seleccion, 'values')
    exito, mensaje = reportes.crear_pdf_profesional(valores[0], valores[1], valores[3], valores[5])
    if exito: messagebox.showinfo("Éxito", mensaje)
    else: messagebox.showerror("Error PDF", mensaje)

def actualizar_datos_precarga():
    global lista_clientes_data, lista_autos_vin
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Customer, Name, LastName FROM Customers")
        lista_clientes_data = [(r[0], f"{r[1]} {r[2]} (ID:{r[0]})") for r in cursor.fetchall()]
        cursor.execute("SELECT VIN FROM Carts")
        lista_autos_vin = [r[0] for r in cursor.fetchall()]
        conn.close()
    except: pass

def agregar_burbuja(texto, tipo):
    """tipo = user (derecha rojo) o bot (izquierda gris)"""
    fila = ctk.CTkFrame(chat_scroll, fg_color="transparent")
    fila.pack(fill="x", padx=16, pady=4)
    if tipo == "user":
        burbuja = ctk.CTkFrame(fila, fg_color=COLOR_ACCENT, corner_radius=14)
        burbuja.pack(side="right", anchor="e")
        ctk.CTkLabel(burbuja, text=texto, font=("Segoe UI", 13),
                     text_color="#ffffff", wraplength=500,
                     justify="right", padx=14, pady=10).pack()
        ctk.CTkLabel(fila, text="Tu", font=("Segoe UI", 9),
                     text_color=COLOR_TEXT_DIM).pack(side="right", anchor="se", padx=(0,4))
    else:
        icono_col = ctk.CTkFrame(fila, fg_color="transparent")
        icono_col.pack(side="left", anchor="nw")
        ctk.CTkLabel(icono_col, text="Cruz PRO", font=("Segoe UI", 9, "bold"),
                     text_color=COLOR_ACCENT, width=30).pack(pady=(4, 0))
        msg_col = ctk.CTkFrame(fila, fg_color="transparent")
        msg_col.pack(side="left", anchor="w", padx=(6, 0))
        burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                               corner_radius=14, border_width=1, border_color=COLOR_BORDER)
        burbuja.pack(anchor="w")
        ctk.CTkLabel(burbuja, text=texto, font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_MAIN, wraplength=500,
                     justify="left", padx=14, pady=10).pack()
    chat_scroll._parent_canvas.yview_moveto(1.0)


def enviar_mensaje_chat(event=None):
    import threading
    if entry_chat.cget("state") == "disabled": return
    m = entry_chat.get().strip()
    if not m: return
    entry_chat.configure(state="disabled")
    entry_chat.delete(0, "end")
    agregar_burbuja(m, "user")
    def obtener_respuesta():
        r = bot_taller.procesar_lenguaje_natural(m)
        chat_scroll.after(0, lambda: _mostrar_bot(r))
    def _mostrar_bot(r):
        agregar_burbuja(r, "bot")
        entry_chat.configure(state="normal")
        entry_chat.focus()
    threading.Thread(target=obtener_respuesta, daemon=True).start()

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def abrir_menu_principal():
    global entry_name, entry_lastname, entry_cellphone, tree_clientes
    global entry_vin, entry_make, entry_model, entry_year, entry_color, search_customer, tree_autos
    global entry_part, entry_duration, entry_price, entry_worker, search_vin, tree_servicios
    global chat_scroll, entry_chat

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

    # ── BOT ───────────────────────────────────────────────────
    bot_outer = ctk.CTkFrame(paginas["bot"], fg_color="transparent")
    bot_outer.pack(expand=True, fill="both", padx=32, pady=24)

    bot_header = ctk.CTkFrame(bot_outer, fg_color="transparent")
    bot_header.pack(fill="x", pady=(0, 12))
    ctk.CTkFrame(bot_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y", padx=(0,12))
    ctk.CTkLabel(bot_header, text="ASISTENTE IA", font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
    ctk.CTkLabel(bot_header, text="  //  Escribe tu consulta abajo",
                 font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(side="left")

    f_chat = ctk.CTkFrame(bot_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                          border_width=1, border_color=COLOR_BORDER)
    f_chat.pack(expand=True, fill="both")
    ctk.CTkFrame(f_chat, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

    # Área de burbujas — scrollable
    chat_scroll = ctk.CTkScrollableFrame(f_chat, fg_color="#0d0d0d", corner_radius=0)
    chat_scroll.pack(expand=True, fill="both", padx=0, pady=0)

    # Mensaje de bienvenida inicial
    bienvenida = (
        "Hola! Soy el asistente de Cruz PRO.\n\n"
        "Puedo consultar la base de datos por ti. Ejemplos:\n"
        "  \u2022 ultimo servicio de Juan\n"
        "  \u2022 que autos tiene Carlos\n"
        "  \u2022 cuanto hemos facturado\n"
        "  \u2022 quien es el mejor mecanico\n\n"
        "Escribe 'ayuda' para ver todos los comandos."
    )

    def agregar_bienvenida():
        fila = ctk.CTkFrame(chat_scroll, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(16, 4))
        icono_col = ctk.CTkFrame(fila, fg_color="transparent")
        icono_col.pack(side="left", anchor="nw")
        ctk.CTkLabel(icono_col, text="Cruz PRO", font=("Segoe UI", 9, "bold"),
                     text_color=COLOR_ACCENT, width=30).pack(pady=(4, 0))
        msg_col = ctk.CTkFrame(fila, fg_color="transparent")
        msg_col.pack(side="left", anchor="w", padx=(6, 0))
        burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                               corner_radius=14, border_width=1, border_color=COLOR_BORDER)
        burbuja.pack(anchor="w")
        ctk.CTkLabel(burbuja, text=bienvenida, font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_MAIN, wraplength=500,
                     justify="left", padx=14, pady=10).pack()

    agregar_bienvenida()

    ctk.CTkFrame(f_chat, fg_color=COLOR_BORDER, height=1, corner_radius=0).pack(fill="x")
    entry_row = ctk.CTkFrame(f_chat, fg_color="transparent")
    entry_row.pack(fill="x", padx=20, pady=12)
    entry_chat = ctk.CTkEntry(entry_row, placeholder_text="Escribe tu consulta y presiona ENTER...",
                               height=44, **ENTRY_STYLE)
    entry_chat.pack(side="left", expand=True, fill="x", padx=(0, 10))
    entry_chat.bind("<Return>", enviar_mensaje_chat)
    ctk.CTkButton(entry_row, text="ENVIAR  ▶", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM,
                  text_color="white", width=110, height=44, corner_radius=4,
                  font=("Segoe UI", 12, "bold"), command=enviar_mensaje_chat).pack(side="right")

    # ── CLIENTES ──────────────────────────────────────────────
    cli_outer = ctk.CTkFrame(paginas["cli"], fg_color="transparent")
    cli_outer.pack(expand=True, fill="both", padx=32, pady=(12, 16))

    # Header compacto
    cli_header = ctk.CTkFrame(cli_outer, fg_color="transparent")
    cli_header.pack(fill="x", pady=(0, 12))
    ctk.CTkFrame(cli_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y", padx=(0,12))
    ctk.CTkLabel(cli_header, text="GESTIÓN DE CLIENTES",
                 font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

    cli_body = ctk.CTkFrame(cli_outer, fg_color="transparent")
    cli_body.pack(expand=True, fill="both")

    # ← FIX: CTkScrollableFrame para que los botones siempre sean accesibles
    f_form_cli = ctk.CTkScrollableFrame(cli_body, fg_color=COLOR_BG_CARD, width=360,
                                         corner_radius=6, border_width=1, border_color=COLOR_BORDER)
    f_form_cli.pack(side="left", fill="y", padx=(0, 20))

    ctk.CTkFrame(f_form_cli, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(f_form_cli, text="EXPEDIENTE", font=("Segoe UI", 10, "bold"),
                 text_color=COLOR_ACCENT).pack(pady=(12, 0))
    ctk.CTkLabel(f_form_cli, text="DATOS DEL CLIENTE", font=("Segoe UI", 14, "bold"),
                 text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

    for lbl, ph, vn in [("NOMBRE", "Nombre", "entry_name"),
                         ("APELLIDO", "Apellido", "entry_lastname"),
                         ("TELÉFONO", "Teléfono", "entry_cellphone")]:
        ctk.CTkLabel(f_form_cli, text=lbl, **LABEL_STYLE).pack(anchor="w", padx=24, pady=(6, 0))
        e = ctk.CTkEntry(f_form_cli, placeholder_text=ph, width=310, height=42, **ENTRY_STYLE)
        e.pack(padx=24, pady=(2, 0))
        globals()[vn] = e

    ctk.CTkFrame(f_form_cli, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
    hacer_boton_accion(f_form_cli, "REGISTRAR", COLOR_ACCENT, guardar_cliente, "＋").pack(fill="x", padx=24, pady=3)
    hacer_boton_accion(f_form_cli, "ACTUALIZAR", "#1a3a1a", editar_cliente, "✎").pack(fill="x", padx=24, pady=3)
    hacer_boton_accion(f_form_cli, "DAR DE BAJA", "#2a1010", eliminar_cliente, "✕").pack(fill="x", padx=24, pady=3)
    ctk.CTkButton(f_form_cli, text="LIMPIAR", fg_color="transparent", border_width=1,
                  border_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM, height=36,
                  corner_radius=4, font=("Segoe UI", 11),
                  command=limpiar_cliente).pack(fill="x", padx=24, pady=(10, 16))

    t_frame_cli = ctk.CTkFrame(cli_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                border_width=1, border_color=COLOR_BORDER)
    t_frame_cli.pack(side="right", expand=True, fill="both")
    ctk.CTkFrame(t_frame_cli, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
    tree_clientes = ttk.Treeview(t_frame_cli, columns=("ID","Nombre","Apellido","Tel"), show="headings")
    for c, w in [("ID",70),("Nombre",220),("Apellido",220),("Tel",160)]:
        tree_clientes.heading(c, text=c); tree_clientes.column(c, width=w)
    tree_clientes.pack(expand=True, fill="both", padx=2, pady=2)
    tree_clientes.bind("<ButtonRelease-1>", seleccionar_cliente)

    # ── AUTOS ─────────────────────────────────────────────────
    au_outer = ctk.CTkFrame(paginas["au"], fg_color="transparent")
    au_outer.pack(expand=True, fill="both", padx=32, pady=(12, 16))

    au_header = ctk.CTkFrame(au_outer, fg_color="transparent")
    au_header.pack(fill="x", pady=(0, 12))
    ctk.CTkFrame(au_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y", padx=(0,12))
    ctk.CTkLabel(au_header, text="FLOTA VEHICULAR",
                 font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

    au_body = ctk.CTkFrame(au_outer, fg_color="transparent")
    au_body.pack(expand=True, fill="both")

    f_form_au = ctk.CTkScrollableFrame(au_body, fg_color=COLOR_BG_CARD, width=380,
                                        corner_radius=6, border_width=1, border_color=COLOR_BORDER)
    f_form_au.pack(side="left", fill="y", padx=(0, 20))
    ctk.CTkFrame(f_form_au, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(f_form_au, text="FICHA TÉCNICA", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
    ctk.CTkLabel(f_form_au, text="DATOS DEL VEHÍCULO", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

    for lbl, ph, vn in [
        ("VIN — NÚMERO DE SERIE", "1HGBH41JXMN109186", "entry_vin"),
        ("MARCA", "Nissan, Toyota, Ford...", "entry_make"),
        ("MODELO", "Sentra, Corolla...", "entry_model"),
        ("AÑO", "2024", "entry_year"),
        ("COLOR", "Color del vehículo", "entry_color"),
    ]:
        ctk.CTkLabel(f_form_au, text=lbl, **LABEL_STYLE).pack(anchor="w", padx=24, pady=(6, 0))
        e = ctk.CTkEntry(f_form_au, placeholder_text=ph, width=320, height=42, **ENTRY_STYLE)
        e.pack(padx=24, pady=(2, 0))
        globals()[vn] = e

    ctk.CTkLabel(f_form_au, text="PROPIETARIO", **LABEL_STYLE).pack(anchor="w", padx=24, pady=(10, 0))
    search_customer = ctk.CTkEntry(f_form_au, placeholder_text="Buscar cliente...", width=320, height=42, **ENTRY_STYLE)
    search_customer.pack(padx=24, pady=(2, 0))
    search_customer.bind("<KeyRelease>", lambda e: mostrar_autocomplete(search_customer, "cliente"))

    ctk.CTkFrame(f_form_au, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
    hacer_boton_accion(f_form_au, "REGISTRAR VEHÍCULO", COLOR_ACCENT, guardar_auto, "＋").pack(fill="x", padx=24, pady=3)
    hacer_boton_accion(f_form_au, "ACTUALIZAR DATOS", "#1a3a1a", editar_auto, "✎").pack(fill="x", padx=24, pady=3)
    hacer_boton_accion(f_form_au, "DAR DE BAJA", "#2a1010", eliminar_auto, "✕").pack(fill="x", padx=24, pady=3)

    t_frame_au = ctk.CTkFrame(au_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                               border_width=1, border_color=COLOR_BORDER)
    t_frame_au.pack(side="right", expand=True, fill="both")
    ctk.CTkFrame(t_frame_au, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
    tree_autos = ttk.Treeview(t_frame_au, columns=("VIN","Marca","Modelo","Año","Color","ID_Cli"), show="headings")
    for c, w in [("VIN",190),("Marca",110),("Modelo",120),("Año",65),("Color",90),("ID_Cli",65)]:
        tree_autos.heading(c, text=c); tree_autos.column(c, width=w)
    tree_autos.pack(expand=True, fill="both", padx=2, pady=2)
    tree_autos.bind("<ButtonRelease-1>", seleccionar_auto)

    # ── SERVICIOS ─────────────────────────────────────────────
    ser_outer = ctk.CTkFrame(paginas["ser"], fg_color="transparent")
    ser_outer.pack(expand=True, fill="both", padx=32, pady=(12, 16))

    ser_header = ctk.CTkFrame(ser_outer, fg_color="transparent")
    ser_header.pack(fill="x", pady=(0, 12))
    ctk.CTkFrame(ser_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y", padx=(0,12))
    ctk.CTkLabel(ser_header, text="ÓRDENES DE SERVICIO",
                 font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

    ser_body = ctk.CTkFrame(ser_outer, fg_color="transparent")
    ser_body.pack(expand=True, fill="both")

    f_form_ser = ctk.CTkScrollableFrame(ser_body, fg_color=COLOR_BG_CARD, width=380,
                                         corner_radius=6, border_width=1, border_color=COLOR_BORDER)
    f_form_ser.pack(side="left", fill="y", padx=(0, 20))
    ctk.CTkFrame(f_form_ser, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(f_form_ser, text="ORDEN DE TRABAJO", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
    ctk.CTkLabel(f_form_ser, text="DETALLE DEL SERVICIO", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

    for lbl, ph, vn in [
        ("TRABAJO / REPUESTOS", "Descripción del servicio", "entry_part"),
        ("TIEMPO ESTIMADO", "Ej: 3 Horas", "entry_duration"),
        ("COSTO TOTAL ($)", "0.00", "entry_price"),
        ("MECÁNICO ASIGNADO", "Nombre del mecánico", "entry_worker"),
    ]:
        ctk.CTkLabel(f_form_ser, text=lbl, **LABEL_STYLE).pack(anchor="w", padx=24, pady=(6, 0))
        e = ctk.CTkEntry(f_form_ser, placeholder_text=ph, width=320, height=42, **ENTRY_STYLE)
        e.pack(padx=24, pady=(2, 0))
        globals()[vn] = e

    ctk.CTkLabel(f_form_ser, text="VIN DEL VEHÍCULO", **LABEL_STYLE).pack(anchor="w", padx=24, pady=(10, 0))
    search_vin = ctk.CTkEntry(f_form_ser, placeholder_text="Escribir o buscar VIN...", width=320, height=42, **ENTRY_STYLE)
    search_vin.pack(padx=24, pady=(2, 0))
    search_vin.bind("<KeyRelease>", lambda e: mostrar_autocomplete(search_vin, "auto"))

    ctk.CTkFrame(f_form_ser, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
    hacer_boton_accion(f_form_ser, "CREAR ORDEN", COLOR_ACCENT, guardar_servicio, "＋").pack(fill="x", padx=24, pady=3)
    hacer_boton_accion(f_form_ser, "ACTUALIZAR ORDEN", "#1a3a1a", editar_servicio, "✎").pack(fill="x", padx=24, pady=3)
    ctk.CTkButton(f_form_ser, text="⬇  EXPORTAR PDF", fg_color="transparent",
                  border_width=1, border_color=COLOR_ACCENT2, text_color=COLOR_ACCENT2,
                  height=42, corner_radius=4, font=("Segoe UI", 12, "bold"),
                  command=pedir_ticket_pdf).pack(fill="x", padx=24, pady=3)

    t_frame_ser = ctk.CTkFrame(ser_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                border_width=1, border_color=COLOR_BORDER)
    t_frame_ser.pack(side="right", expand=True, fill="both")
    ctk.CTkFrame(t_frame_ser, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
    tree_servicios = ttk.Treeview(t_frame_ser,
                                   columns=("ID","Descripción","Hrs","Costo","Mecánico","VIN"),
                                   show="headings")
    for c, w in [("ID",50),("Descripción",230),("Hrs",90),("Costo",100),("Mecánico",140),("VIN",180)]:
        tree_servicios.heading(c, text=c)
        tree_servicios.column(c, width=w, anchor="center" if c in ("ID","Hrs","Costo") else "w")
    tree_servicios.pack(expand=True, fill="both", padx=2, pady=2)
    tree_servicios.bind("<ButtonRelease-1>", seleccionar_servicio)

    # ── MÉTRICAS — FIX: header+botón en una fila, gráfica ocupa todo el resto ──
    dash_outer = ctk.CTkFrame(paginas["dash"], fg_color="transparent")
    dash_outer.pack(expand=True, fill="both", padx=32, pady=(12, 16))

    # Una sola fila compacta: barra roja | título | botón a la derecha
    dash_topbar = ctk.CTkFrame(dash_outer, fg_color="transparent", height=44)
    dash_topbar.pack(fill="x", pady=(0, 10))
    dash_topbar.pack_propagate(False)
    ctk.CTkFrame(dash_topbar, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y", padx=(0,12))
    ctk.CTkLabel(dash_topbar, text="MÉTRICAS Y RENDIMIENTO",
                 font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
    ctk.CTkButton(dash_topbar, text="🔄  ACTUALIZAR",
                  height=36, width=140, font=("Segoe UI", 11, "bold"),
                  fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM, corner_radius=4,
                  command=lambda: graficos.dibujar_profesional(f_graf)).pack(side="right")

    # La gráfica toma TODO el espacio vertical restante
    f_graf = ctk.CTkFrame(dash_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                           border_width=1, border_color=COLOR_BORDER)
    f_graf.pack(expand=True, fill="both")
    ctk.CTkFrame(f_graf, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

    # ── INIT ──────────────────────────────────────────────────
    actualizar_datos_precarga(); cargar_clientes(); cargar_autos(); cargar_servicios()
    ir_a("bot", btns["bot"])
    animar_entrada(ventana_menu)

    # Bienvenida ya incluida como burbuja en la UI

# ==========================================
# LOGIN
# ==========================================
def login():
    u, c = entry_usuario.get(), entry_contraseña.get()
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (u, c))
        if cursor.fetchone():
            ventana_login.withdraw(); abrir_menu_principal()
        else:
            messagebox.showerror("Acceso Denegado", "Credenciales incorrectas.")
        conn.close()
    except Exception as e:
        messagebox.showerror("Error Crítico", str(e))

ventana_login = ctk.CTk()
ventana_login.title("Cruz PRO — Acceso")
ventana_login.geometry("1000x700")
ventana_login.configure(fg_color=COLOR_BG_BASE)
ventana_login.resizable(False, False)

ctk.CTkFrame(ventana_login, fg_color=COLOR_ACCENT, width=5, corner_radius=0).place(x=0, y=0, relheight=1)

card = ctk.CTkFrame(ventana_login, fg_color=COLOR_BG_CARD, corner_radius=6,
                    width=420, height=570, border_width=1, border_color=COLOR_BORDER)
card.pack_propagate(False)
card.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkFrame(card, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

logo_login = ctk.CTkFrame(card, fg_color="transparent")
logo_login.pack(pady=(32, 0))
ctk.CTkLabel(logo_login, text="⬡", font=("Arial", 38), text_color=COLOR_ACCENT).pack()
ctk.CTkLabel(logo_login, text="CRUZ PRO", font=("Segoe UI", 26, "bold"), text_color=COLOR_TEXT_MAIN).pack()
ctk.CTkLabel(logo_login, text="SISTEMA DE GESTIÓN AUTOMOTRIZ",
             font=("Segoe UI", 9, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=(3, 0))

ctk.CTkFrame(card, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=40, pady=24)

ctk.CTkLabel(card, text="USUARIO", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", padx=40)
entry_usuario = ctk.CTkEntry(card, placeholder_text="ID de colaborador", width=340, height=48, **ENTRY_STYLE)
entry_usuario.pack(padx=40, pady=(4, 14))

ctk.CTkLabel(card, text="CONTRASEÑA", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", padx=40)
entry_contraseña = ctk.CTkEntry(card, placeholder_text="Clave de acceso", show="*", width=340, height=48, **ENTRY_STYLE)
entry_contraseña.pack(padx=40, pady=(4, 0))
entry_contraseña.bind("<Return>", lambda e: login())

ctk.CTkFrame(card, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=40, pady=22)

ctk.CTkButton(card, text="INICIAR SESIÓN  ▶", command=login, width=340, height=50,
              fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM,
              text_color="white", corner_radius=4,
              font=("Segoe UI", 13, "bold")).pack(padx=40)

ctk.CTkLabel(card, text="CRUZ PRO  //  v2.0  //  Taller Cruz",
             font=("Segoe UI", 9), text_color="#333333").pack(pady=(16, 0))

animar_entrada(ventana_login)
ventana_login.mainloop()