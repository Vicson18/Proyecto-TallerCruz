import customtkinter as ctk
from tkinter import messagebox, ttk
import pyodbc
import time

# --- IMPORTACION DE MÓDULOS ---
from conexion import conectar
import bot_taller
import reportes
import graficos

# --- CONFIGURACIÓN DEL TEMA DARK SAAS PREMIUM ---
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

# --- PALETA DE COLORES "SLATE & INDIGO" ---
COLOR_BG_BASE = "#0f172a"       
COLOR_BG_CARD = "#1e293b"       
COLOR_BG_CARD_ALT = "#27354a"   
COLOR_BG_INPUT = "#334155"      
COLOR_ACCENT = "#6366f1"        
COLOR_TEXT_MAIN = "#f8fafc"     
COLOR_TEXT_DIM = "#94a3b8"      
COLOR_BORDER = "#475569"        
COLOR_SUCCESS = "#10b981"       
COLOR_DANGER = "#ef4444"        

ENTRY_STYLE = {
    "fg_color": COLOR_BG_INPUT, 
    "text_color": COLOR_TEXT_MAIN, 
    "border_color": COLOR_BORDER, 
    "border_width": 1, 
    "corner_radius": 8,
    "font": ("Segoe UI", 14)
}

LABEL_STYLE = {"font": ("Segoe UI", 13, "bold"), "text_color": COLOR_TEXT_DIM}

BTN_TOP_NAV = {
    "fg_color": "transparent", 
    "text_color": COLOR_TEXT_DIM, 
    "hover_color": COLOR_BG_INPUT, 
    "corner_radius": 6,
    "font": ("Segoe UI", 15, "bold"),
}

lista_clientes_data = [] 
lista_autos_vin = []
popup_lista = None 

# ==========================================
# FUNCIONES DE UX Y ANIMACIÓN
# ==========================================
def animar_entrada(ventana):
    ventana.attributes("-alpha", 0.0)
    for i in range(1, 11):
        if ventana.winfo_exists():
            ventana.attributes("-alpha", i/10)
            ventana.update()
            time.sleep(0.01)

def efecto_maquina_escribir(textbox, texto, tag, entry_widget, index=0):
    """Escribe letra por letra sin congelar el programa usando el mainloop"""
    if index == 0:
        textbox.configure(state="normal")
        entry_widget.configure(state="disabled") # Bloquea el input mientras el bot escribe
        
    if not textbox.winfo_exists(): return

    if index < len(texto):
        textbox.insert("end", texto[index], tag)
        textbox.see("end")
        # Controla la velocidad de escritura (10 ms por letra)
        textbox.after(10, efecto_maquina_escribir, textbox, texto, tag, entry_widget, index + 1)
    else:
        textbox.configure(state="disabled")
        entry_widget.configure(state="normal") # Libera el input al terminar
        entry_widget.focus()

def configurar_estilo_tablas():
    style = ttk.Style()
    style.theme_use("default")
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
    style.configure("Treeview", 
                    background=COLOR_BG_CARD, 
                    foreground=COLOR_TEXT_MAIN, 
                    rowheight=45, 
                    fieldbackground=COLOR_BG_CARD, 
                    borderwidth=0,
                    font=("Segoe UI", 13)) 
    style.map('Treeview', background=[('selected', COLOR_ACCENT)], foreground=[('selected', "#ffffff")])
    style.configure("Treeview.Heading", 
                    background=COLOR_BG_INPUT, 
                    foreground=COLOR_TEXT_MAIN, 
                    relief="flat", 
                    padding=(10, 15),
                    font=("Segoe UI", 14, "bold"))

# ==========================================
# COMPONENTE: AUTOCOMPLETE
# ==========================================
def mostrar_autocomplete(entry_widget, tipo):
    global popup_lista
    if popup_lista and popup_lista.winfo_exists(): popup_lista.destroy()
    texto = entry_widget.get().lower()
    if not texto: return

    opciones = []
    if tipo == "cliente": opciones = [c[1] for c in lista_clientes_data if texto in c[1].lower()]
    elif tipo == "auto": opciones = [str(v) for v in lista_autos_vin if texto in str(v).lower()]
    opciones = opciones[:5]
    if not opciones: return

    x = entry_widget.winfo_rootx()
    y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
    popup_lista = ctk.CTkToplevel(entry_widget)
    popup_lista.wm_overrideredirect(True)
    popup_lista.geometry(f"{entry_widget.winfo_width()}x{len(opciones)*40+10}+{x}+{y}")
    popup_lista.configure(fg_color=COLOR_BG_INPUT)
    
    f_int = ctk.CTkFrame(popup_lista, fg_color="transparent", corner_radius=8, border_width=1, border_color=COLOR_BORDER)
    f_int.pack(fill="both", expand=True, padx=2, pady=2)

    def seleccionar(op):
        entry_widget.delete(0, 'end'); entry_widget.insert(0, op); popup_lista.destroy()

    for op in opciones:
        ctk.CTkButton(f_int, text=op, fg_color="transparent", text_color=COLOR_TEXT_MAIN, hover_color=COLOR_BG_BASE, anchor="w", height=35, font=("Segoe UI", 13), command=lambda o=op: seleccionar(o)).pack(fill="x", padx=5, pady=2)

# ==========================================
# LÓGICA DE NEGOCIO (CRUDs)
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
        messagebox.showinfo("Éxito", "Cliente registrado exitosamente.")
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_cliente():
    seleccion = tree_clientes.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla.")
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
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla.")
    id_cliente = int(str(tree_clientes.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Eliminar cliente permanentemente?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Customers WHERE Id_Customer=?", (id_cliente,))
            conn.commit(); conn.close()
            limpiar_cliente(); cargar_clientes(); actualizar_datos_precarga() 
        except Exception: messagebox.showerror("Error", "No se puede eliminar (el cliente tiene autos registrados).")

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
    if "(ID:" not in texto: return messagebox.showwarning("Error", "Selecciona un cliente de la lista sugerida.")
    try:
        id_cli = int(texto.split("(ID:")[1].replace(")", ""))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Carts (Make, Model, ModelYear, Color, Id_Customer) VALUES (?,?,?,?,?)", 
                       (entry_make.get(), entry_model.get(), entry_year.get(), entry_color.get(), id_cli))
        conn.commit(); conn.close(); cargar_autos(); actualizar_datos_precarga(); limpiar_auto()
        messagebox.showinfo("Éxito", "Vehículo registrado.")
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_auto():
    seleccion = tree_autos.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto.")
    vin = int(str(tree_autos.item(seleccion, 'values')[0]).replace(',', ''))
    texto = search_customer.get()
    if "(ID:" not in texto: return messagebox.showwarning("Error", "Seleccione un propietario válido.")
    try:
        id_cli = int(texto.split("(ID:")[1].replace(")", ""))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Carts SET Make=?, Model=?, ModelYear=?, Color=?, Id_Customer=? WHERE VIN=?", 
                       (entry_make.get(), entry_model.get(), entry_year.get(), entry_color.get(), id_cli, vin))
        conn.commit(); conn.close(); cargar_autos(); limpiar_auto()
        messagebox.showinfo("Éxito", "Vehículo actualizado.")
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_auto():
    seleccion = tree_autos.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto.")
    vin = int(str(tree_autos.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Eliminar vehículo del sistema?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Carts WHERE VIN=?", (vin,))
            conn.commit(); conn.close(); cargar_autos(); limpiar_auto()
        except Exception: messagebox.showerror("Error", "No se puede eliminar (tiene servicios vinculados).")

def limpiar_auto():
    entry_make.delete(0, 'end'); entry_model.delete(0, 'end'); entry_year.delete(0, 'end'); entry_color.delete(0, 'end')
    search_customer.delete(0, 'end')

def seleccionar_auto(event):
    seleccion = tree_autos.focus()
    if seleccion:
        valores = tree_autos.item(seleccion, 'values')
        limpiar_auto()
        entry_make.insert(0, valores[1]); entry_model.insert(0, valores[2]); entry_year.insert(0, valores[3]); entry_color.insert(0, valores[4])
        id_buscado = str(valores[5]).replace(',', '')
        for cli_id, cli_nombre in lista_clientes_data:
            if str(cli_id) == id_buscado: search_customer.insert(0, cli_nombre); break

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
        messagebox.showinfo("Éxito", "Servicio generado correctamente.")
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
    if messagebox.askyesno("Confirmar", "¿Borrar servicio?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Services WHERE Id_Service=?", (id_servicio,))
            conn.commit(); conn.close(); cargar_servicios(); limpiar_servicio()
        except Exception as e: messagebox.showerror("Error", str(e))

def limpiar_servicio():
    entry_part.delete(0, 'end'); entry_duration.delete(0, 'end'); entry_price.delete(0, 'end'); entry_worker.delete(0, 'end')
    search_vin.delete(0, 'end')

def seleccionar_servicio(event):
    seleccion = tree_servicios.focus()
    if seleccion:
        valores = tree_servicios.item(seleccion, 'values')
        limpiar_servicio()
        entry_part.insert(0, valores[1]); entry_duration.insert(0, valores[2]); entry_price.insert(0, valores[3]); entry_worker.insert(0, valores[4])
        search_vin.insert(0, valores[5])

def pedir_ticket_pdf():
    seleccion = tree_servicios.focus()
    if not seleccion: return messagebox.showwarning("Error", "Selecciona un servicio de la tabla.")
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

def enviar_mensaje_chat(event=None):
    # Previene que el usuario mande más mensajes mientras el bot está escribiendo
    if entry_chat.cget("state") == "disabled": return 
    
    m = entry_chat.get()
    if not m: return
    chat_display.configure(state="normal")
    chat_display.insert("end", f"👤 Tú: {m}\n\n", "user_tag")
    chat_display.configure(state="disabled")
    entry_chat.delete(0, 'end')
    
    r = bot_taller.procesar_lenguaje_natural(m)
    texto_respuesta = f"🤖 Sistema: {r}\n\n"
    
    # Inicia la animación de máquina de escribir
    efecto_maquina_escribir(chat_display, texto_respuesta, "bot_tag", entry_chat)

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def abrir_menu_principal():
    global entry_name, entry_lastname, entry_cellphone, tree_clientes
    global entry_make, entry_model, entry_year, entry_color, search_customer, tree_autos
    global entry_part, entry_duration, entry_price, entry_worker, search_vin, tree_servicios
    global chat_display, entry_chat

    ventana_menu = ctk.CTkToplevel()
    ventana_menu.protocol("WM_DELETE_WINDOW", ventana_login.destroy)
    ventana_menu.title("Dashboard Empresarial - Taller Cruz PRO")
    ventana_menu.geometry("1500x900")
    ventana_menu.configure(fg_color=COLOR_BG_BASE)
    
    configurar_estilo_tablas()

    top_bar = ctk.CTkFrame(ventana_menu, fg_color=COLOR_BG_CARD, height=80, corner_radius=0, border_width=0)
    top_bar.pack(side="top", fill="x")
    
    ctk.CTkLabel(top_bar, text="🔧 CRUZ PRO", font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(side="left", padx=40)

    nav_btns_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    nav_btns_frame.pack(side="right", padx=30, pady=15)

    container_main = ctk.CTkFrame(ventana_menu, fg_color="transparent")
    container_main.pack(expand=True, fill="both", padx=40, pady=30)
    
    paginas = {}

    def ir_a(nombre, btn):
        for b in btns.values(): 
            b.configure(text_color=COLOR_TEXT_DIM, fg_color="transparent")
        btn.configure(text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BG_INPUT)
        for p in paginas.values(): p.pack_forget()
        paginas[nombre].pack(expand=True, fill="both")

    btns = {}
    secciones = [("bot", "IA Asistente"), ("cli", "Clientes"), ("au", "Flota Vehicular"), ("ser", "Órdenes de Servicio"), ("dash", "Métricas")]
    for id_p, txt in secciones:
        btns[id_p] = ctk.CTkButton(nav_btns_frame, text=txt, command=lambda i=id_p: ir_a(i, btns[i]), width=160, height=50, **BTN_TOP_NAV)
        btns[id_p].pack(side="left", padx=5)

    for p in ["bot", "cli", "au", "ser", "dash"]: paginas[p] = ctk.CTkFrame(container_main, fg_color="transparent")

    # --- PÁGINA: BOT ---
    f_chat = ctk.CTkFrame(paginas["bot"], fg_color=COLOR_BG_CARD, corner_radius=15)
    f_chat.pack(expand=True, fill="both", pady=10)
    chat_display = ctk.CTkTextbox(f_chat, fg_color=COLOR_BG_BASE, text_color=COLOR_TEXT_MAIN, font=("Consolas", 15), border_width=1, border_color=COLOR_BORDER)
    chat_display.pack(expand=True, fill="both", padx=30, pady=(30, 15))
    chat_display.tag_config("user_tag", foreground=COLOR_ACCENT)
    chat_display.tag_config("bot_tag", foreground=COLOR_SUCCESS)
    
    entry_chat = ctk.CTkEntry(f_chat, placeholder_text="Consulta datos usando lenguaje natural...", height=55, **ENTRY_STYLE)
    entry_chat.pack(fill="x", padx=30, pady=(0, 30))
    entry_chat.bind("<Return>", enviar_mensaje_chat)

    # --- PÁGINA: CLIENTES ---
    f_form_cli = ctk.CTkFrame(paginas["cli"], fg_color=COLOR_BG_CARD, width=380, corner_radius=15)
    f_form_cli.pack(side="left", fill="y", padx=(0, 30))
    ctk.CTkLabel(f_form_cli, text="Expediente Cliente", font=("Segoe UI", 20, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=30)
    
    entry_name = ctk.CTkEntry(f_form_cli, placeholder_text="Nombre", width=360, height=45, **ENTRY_STYLE); entry_name.pack(pady=10, padx=30)
    entry_lastname = ctk.CTkEntry(f_form_cli, placeholder_text="Apellido", width=360, height=45, **ENTRY_STYLE); entry_lastname.pack(pady=10, padx=30)
    entry_cellphone = ctk.CTkEntry(f_form_cli, placeholder_text="Teléfono", width=360, height=45, **ENTRY_STYLE); entry_cellphone.pack(pady=10, padx=30)
    
    ctk.CTkButton(f_form_cli, text="Registrar", fg_color=COLOR_SUCCESS, width=360, height=45, font=("Segoe UI", 14, "bold"), command=guardar_cliente).pack(pady=(30,5), padx=30)
    ctk.CTkButton(f_form_cli, text="Actualizar", fg_color=COLOR_ACCENT, width=360, height=45, font=("Segoe UI", 14, "bold"), command=editar_cliente).pack(pady=5, padx=30)
    ctk.CTkButton(f_form_cli, text="Dar de Baja", fg_color=COLOR_DANGER, width=360, height=45, font=("Segoe UI", 14, "bold"), command=eliminar_cliente).pack(pady=5, padx=30)
    ctk.CTkButton(f_form_cli, text="Limpiar Casillas", fg_color="transparent", width=360, border_width=1, border_color=COLOR_BORDER, height=45, command=limpiar_cliente).pack(pady=5, padx=30)

    tree_clientes = ttk.Treeview(paginas["cli"], columns=("ID", "Nombre", "Apellido", "Tel"), show="headings")
    for c in ("ID", "Nombre", "Apellido", "Tel"): tree_clientes.heading(c, text=c)
    tree_clientes.pack(side="right", expand=True, fill="both")
    tree_clientes.bind("<ButtonRelease-1>", seleccionar_cliente)

    # --- PÁGINA: AUTOS ---
    f_form_au = ctk.CTkFrame(paginas["au"], fg_color=COLOR_BG_CARD, corner_radius=15)
    f_form_au.pack(side="left", fill="y", padx=(0, 30))
    ctk.CTkLabel(f_form_au, text="Ficha Técnica", font=("Segoe UI", 20, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)
    
    entry_make = ctk.CTkEntry(f_form_au, placeholder_text="Marca", width=360, height=45, **ENTRY_STYLE); entry_make.pack(pady=8, padx=30)
    entry_model = ctk.CTkEntry(f_form_au, placeholder_text="Modelo", width=360, height=45, **ENTRY_STYLE); entry_model.pack(pady=8, padx=30)
    entry_year = ctk.CTkEntry(f_form_au, placeholder_text="Año", width=360, height=45, **ENTRY_STYLE); entry_year.pack(pady=8, padx=30)
    entry_color = ctk.CTkEntry(f_form_au, placeholder_text="Color", width=360, height=45, **ENTRY_STYLE); entry_color.pack(pady=8, padx=30)
    
    ctk.CTkLabel(f_form_au, text="Vincular a Propietario:", **LABEL_STYLE).pack(padx=30, anchor="w", pady=(15,0))
    search_customer = ctk.CTkEntry(f_form_au, placeholder_text="Buscar por nombre...", width=360, height=45, **ENTRY_STYLE); search_customer.pack(pady=5, padx=30)
    search_customer.bind("<KeyRelease>", lambda e: mostrar_autocomplete(search_customer, "cliente"))
    
    ctk.CTkButton(f_form_au, text="Registrar", fg_color=COLOR_SUCCESS, width=360, height=45, font=("Segoe UI", 14, "bold"), command=guardar_auto).pack(pady=(15,5), padx=30)
    ctk.CTkButton(f_form_au, text="Actualizar", fg_color=COLOR_ACCENT, width=360, height=45, font=("Segoe UI", 14, "bold"), command=editar_auto).pack(pady=5, padx=30)
    ctk.CTkButton(f_form_au, text="Dar de Baja", fg_color=COLOR_DANGER, width=360, height=45, font=("Segoe UI", 14, "bold"), command=eliminar_auto).pack(pady=5, padx=30)

    tree_autos = ttk.Treeview(paginas["au"], columns=("VIN", "Marca", "Modelo", "Año", "Color", "ID_Cli"), show="headings")
    for c in ("VIN", "Marca", "Modelo", "Año", "Color", "ID_Cli"): tree_autos.heading(c, text=c)
    tree_autos.pack(side="right", expand=True, fill="both")
    tree_autos.bind("<ButtonRelease-1>", seleccionar_auto)

    # --- PÁGINA: SERVICIOS ---
    f_form_ser = ctk.CTkFrame(paginas["ser"], fg_color=COLOR_BG_CARD, corner_radius=15)
    f_form_ser.pack(side="left", fill="y", padx=(0, 30))
    ctk.CTkLabel(f_form_ser, text="Orden de Trabajo", font=("Segoe UI", 20, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)
    
    entry_part = ctk.CTkEntry(f_form_ser, placeholder_text="Trabajo / Repuestos", width=360, height=45, **ENTRY_STYLE); entry_part.pack(pady=8, padx=30)
    entry_duration = ctk.CTkEntry(f_form_ser, placeholder_text="Tiempo Estimado", width=360, height=45, **ENTRY_STYLE); entry_duration.pack(pady=8, padx=30)
    entry_price = ctk.CTkEntry(f_form_ser, placeholder_text="Costo Total ($)", width=360, height=45, **ENTRY_STYLE); entry_price.pack(pady=8, padx=30)
    entry_worker = ctk.CTkEntry(f_form_ser, placeholder_text="Mecánico Asignado", width=360, height=45, **ENTRY_STYLE); entry_worker.pack(pady=8, padx=30)
    
    ctk.CTkLabel(f_form_ser, text="Vincular Vehículo (VIN):", **LABEL_STYLE).pack(padx=30, anchor="w", pady=(15,0))
    search_vin = ctk.CTkEntry(f_form_ser, placeholder_text="Escribir VIN...", width=360, height=45, **ENTRY_STYLE); search_vin.pack(pady=5, padx=30)
    search_vin.bind("<KeyRelease>", lambda e: mostrar_autocomplete(search_vin, "auto"))
    
    ctk.CTkButton(f_form_ser, text="Crear Orden", fg_color=COLOR_SUCCESS, width=360, height=45, font=("Segoe UI", 14, "bold"), command=guardar_servicio).pack(pady=(15,5), padx=30)
    ctk.CTkButton(f_form_ser, text="Actualizar Orden", fg_color=COLOR_ACCENT, width=360, height=45, font=("Segoe UI", 14, "bold"), command=editar_servicio).pack(pady=5, padx=30)
    ctk.CTkButton(f_form_ser, text="Exportar a PDF", fg_color="transparent", width=360, border_width=1, border_color=COLOR_ACCENT, text_color=COLOR_TEXT_MAIN, height=45, font=("Segoe UI", 14, "bold"), command=pedir_ticket_pdf).pack(pady=(15, 5), padx=30)

    tree_servicios = ttk.Treeview(paginas["ser"], columns=("ID", "Descripción", "Hrs", "Costo", "Mecánico", "VIN"), show="headings")
    for c in ("ID", "Descripción", "Hrs", "Costo", "Mecánico", "VIN"): tree_servicios.heading(c, text=c)
    tree_servicios.column("ID", width=50, anchor="center")
    tree_servicios.column("Hrs", width=80, anchor="center")
    tree_servicios.column("Costo", width=100, anchor="center")
    tree_servicios.pack(side="right", expand=True, fill="both")
    tree_servicios.bind("<ButtonRelease-1>", seleccionar_servicio)

    # --- PÁGINA: ESTADÍSTICAS ---
    f_graf = ctk.CTkFrame(paginas["dash"], fg_color=COLOR_BG_CARD, corner_radius=15)
    f_graf.pack(expand=True, fill="both")
    ctk.CTkButton(paginas["dash"], text="🔄 Actualizar Métricas", height=45, font=("Segoe UI", 14, "bold"), fg_color=COLOR_ACCENT, command=lambda: graficos.dibujar_profesional(f_graf)).pack(pady=20)

    actualizar_datos_precarga(); cargar_clientes(); cargar_autos(); cargar_servicios()
    ir_a("bot", btns["bot"])
    
    animar_entrada(ventana_menu)

    # Inicia la animación del mensaje de bienvenida una vez que la ventana está visible
    msg_bienvenida = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        " 🔧 SISTEMA DE ASISTENCIA - CRUZ PRO INICIADO \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "¡Hola! Fui actualizado con Inteligencia Artificial.\n"
        "Puedo buscar en los registros y cruzar tablas.\n\n"
        "💡 Intenta preguntarme:\n"
        "  • '¿Cuál fue el último servicio de Juan?'\n"
        "  • '¿Cuándo fue la última vez que se le hizo frenos a María?'\n"
        "  • '¿Qué autos tiene Carlos?'\n"
        "  • '¿Quién es nuestro mejor mecánico?'\n\n"
        "Escribe abajo para comenzar...\n\n"
    )
    efecto_maquina_escribir(chat_display, msg_bienvenida, "bot_tag", entry_chat)

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
        else: messagebox.showerror("Autenticación Fallida", "Usuario o contraseña inválidos.")
        conn.close()
    except Exception as e: messagebox.showerror("Error Crítico", str(e))

ventana_login = ctk.CTk()
ventana_login.title("Autenticación")
ventana_login.geometry("1000x700") 
ventana_login.configure(fg_color=COLOR_BG_BASE)

card = ctk.CTkFrame(ventana_login, fg_color=COLOR_BG_CARD, corner_radius=20, width=450, height=600)
card.pack_propagate(False) 
card.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(card, text="🔧", font=("Arial", 60)).pack(pady=(60, 10))
ctk.CTkLabel(card, text="SYSTEM ACCES", font=("Segoe UI", 26, "bold"), text_color=COLOR_ACCENT).pack(pady=(0, 50))

entry_usuario = ctk.CTkEntry(card, placeholder_text="ID Colaborador", width=360, height=55, **ENTRY_STYLE)
entry_usuario.pack(pady=15)
entry_contraseña = ctk.CTkEntry(card, placeholder_text="Clave de Acceso", show="*", width=360, height=55, **ENTRY_STYLE)
entry_contraseña.pack(pady=15)

ctk.CTkButton(card, text="INICIAR SESIÓN", command=login, width=360, height=60, fg_color=COLOR_ACCENT, font=("Segoe UI", 16, "bold")).pack(pady=50)

animar_entrada(ventana_login)
ventana_login.mainloop()