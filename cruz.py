import customtkinter as ctk
import pyodbc
from tkinter import messagebox
from tkinter import ttk 
import os
from PIL import Image 

import bot_taller # Tu archivo del bot

# --- CONFIGURACIÓN DEL TEMA ---
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("green") 

# --- Estilos Personalizados ---
COLOR_BLANCO = "white"
COLOR_NEGRO = "black"
COLOR_GRIS_CLARO = "#f0f0f0"
COLOR_GRIS_BORDE = "#dcdcdc"
COLOR_VERDE_PRINCIPAL = "#2ecc71"
COLOR_VERDE_HOVER = "#27ae60"
COLOR_ROJO = "#e74c3c"
COLOR_AZUL = "#3498db"
COLOR_AZUL_HOVER = "#2980b9"
COLOR_GRIS_OSCURO = "#7f8c8d"
COLOR_PLACA_TITULO = "#2c3e50" 

ENTRY_STYLE = {"fg_color": COLOR_BLANCO, "text_color": COLOR_NEGRO, "border_color": COLOR_GRIS_BORDE, "border_width": 1}
LABEL_STYLE = {"font": ("Arial", 12, "bold"), "text_color": "#666666"}

lista_clientes_combo = []

def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  
        'DATABASE=taller;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )

def configurar_estilo_tablas():
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=COLOR_BLANCO, foreground=COLOR_NEGRO, rowheight=25, fieldbackground=COLOR_BLANCO, bordercolor=COLOR_GRIS_BORDE, borderwidth=1)
    style.map('Treeview', background=[('selected', COLOR_VERDE_PRINCIPAL)], foreground=[('selected', COLOR_BLANCO)])
    style.configure("Treeview.Heading", background=COLOR_GRIS_CLARO, foreground=COLOR_NEGRO, relief="flat", font=("Arial", 10, "bold"))
    style.map("Treeview.Heading", background=[('active', COLOR_GRIS_BORDE)])

# ==========================================
# FUNCIONES: BUSCADOR DE CLIENTES NORMAL
# ==========================================
def actualizar_clientes_combo():
    global lista_clientes_combo
    lista_clientes_combo.clear()
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Customer, Name, LastName FROM Customers")
        for row in cursor.fetchall():
            lista_clientes_combo.append(f"{row[0]} - {row[1]} {row[2]}")
        conn.close()
        if 'combo_customer' in globals():
            combo_customer.configure(values=lista_clientes_combo)
    except Exception as e:
        print("Error al actualizar buscador:", e)

def filtrar_clientes(event):
    if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return'): return
    texto_busqueda = combo_customer.get().lower()
    if texto_busqueda == "":
        combo_customer.configure(values=lista_clientes_combo)
    else:
        filtrados = [c for c in lista_clientes_combo if texto_busqueda in c.lower()]
        combo_customer.configure(values=filtrados)

# ==========================================
# FUNCIONES DEL MENÚ GUIADO DEL BOT
# ==========================================
def limpiar_frame_opciones():
    for widget in frame_opciones.winfo_children():
        widget.destroy()

def dibujar_menu_principal_bot():
    limpiar_frame_opciones()
    ctk.CTkButton(frame_opciones, text="📊 Ver Reportes Rápidos", font=("Arial", 14, "bold"), fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER, command=dibujar_menu_reportes_bot).pack(side="left", padx=10, expand=True, fill="x", ipady=8)
    ctk.CTkButton(frame_opciones, text="🔍 Buscar un Cliente", font=("Arial", 14, "bold"), fg_color=COLOR_VERDE_PRINCIPAL, hover_color=COLOR_VERDE_HOVER, command=accion_buscar_cliente_bot).pack(side="left", padx=10, expand=True, fill="x", ipady=8)

def dibujar_menu_reportes_bot():
    limpiar_frame_opciones()
    ctk.CTkButton(frame_opciones, text="💰 Ganancias", fg_color=COLOR_AZUL, command=lambda: ejecutar_comando_bot("GANANCIAS", "¿Cuáles son las ganancias totales?")).pack(side="left", padx=2, expand=True, fill="x", ipady=5)
    ctk.CTkButton(frame_opciones, text="👥 Clientes", fg_color=COLOR_AZUL, command=lambda: ejecutar_comando_bot("TOTAL_CLIENTES", "¿Cuántos clientes tenemos?")).pack(side="left", padx=2, expand=True, fill="x", ipady=5)
    ctk.CTkButton(frame_opciones, text="🚗 Autos", fg_color=COLOR_AZUL, command=lambda: ejecutar_comando_bot("TOTAL_AUTOS", "¿Cuántos autos hay?")).pack(side="left", padx=2, expand=True, fill="x", ipady=5)
    
    ctk.CTkButton(frame_opciones, text="🔙 Volver", fg_color=COLOR_GRIS_OSCURO, command=dibujar_menu_principal_bot).pack(side="left", padx=10, expand=True, fill="x", ipady=5)

def accion_buscar_cliente_bot():
    dialog = ctk.CTkInputDialog(text="Ingresa el nombre y/o apellido a buscar:", title="Buscador Inteligente")
    nombre_ingresado = dialog.get_input()
    if nombre_ingresado: 
        ejecutar_comando_bot("BUSCAR_CLIENTE", f"Quiero buscar los datos de '{nombre_ingresado}'", parametro=nombre_ingresado)

def ejecutar_comando_bot(comando, texto_usuario, parametro=""):
    chat_display.configure(state="normal")
    chat_display.insert("end", f"🧑 Tú: {texto_usuario}\n\n")
    chat_display.update()
    
    respuesta_bot = bot_taller.procesar_comando(comando, parametro)
    
    chat_display.insert("end", f"{respuesta_bot}\n")
    chat_display.insert("end", "-"*50 + "\n\n")
    chat_display.configure(state="disabled")
    chat_display.see("end")

# ==========================================
# FUNCIONES CRUD (Clientes, Autos, Servicios)
# ==========================================
def cargar_clientes():
    for row in tree_clientes.get_children(): tree_clientes.delete(row)
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Customer, Name, LastName, Cellphone FROM Customers")
        for row in cursor.fetchall(): tree_clientes.insert("", "end", values=[str(val) if val is not None else "" for val in row])
        conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))

def limpiar_cliente():
    entry_name.delete(0, 'end'); entry_lastname.delete(0, 'end'); entry_cellphone.delete(0, 'end')
    if tree_clientes.selection(): tree_clientes.selection_remove(tree_clientes.selection())

def seleccionar_cliente(event):
    seleccion = tree_clientes.focus()
    if seleccion:
        valores = tree_clientes.item(seleccion, 'values')
        limpiar_cliente()
        entry_name.insert(0, valores[1]); entry_lastname.insert(0, valores[2]); entry_cellphone.insert(0, valores[3])

def guardar_cliente():
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (Name, LastName, Cellphone, InsertedDate) VALUES (?,?,?, GETDATE())", (entry_name.get(), entry_lastname.get(), entry_cellphone.get()))
        conn.commit(); conn.close()
        messagebox.showinfo("Éxito", "Cliente guardado"); limpiar_cliente(); cargar_clientes(); actualizar_clientes_combo() 
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_cliente():
    seleccion = tree_clientes.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla")
    id_cliente = int(str(tree_clientes.item(seleccion, 'values')[0]).replace(',', ''))
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Customers SET Name=?, LastName=?, Cellphone=? WHERE Id_Customer=?", (entry_name.get(), entry_lastname.get(), entry_cellphone.get(), id_cliente))
        conn.commit(); conn.close()
        messagebox.showinfo("Éxito", "Cliente actualizado"); limpiar_cliente(); cargar_clientes(); actualizar_clientes_combo() 
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_cliente():
    seleccion = tree_clientes.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla")
    id_cliente = int(str(tree_clientes.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este cliente?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Customers WHERE Id_Customer=?", (id_cliente,))
            conn.commit(); conn.close()
            messagebox.showinfo("Éxito", "Cliente eliminado"); limpiar_cliente(); cargar_clientes(); actualizar_clientes_combo() 
        except pyodbc.IntegrityError: messagebox.showerror("Error de Integridad", "No se puede eliminar el cliente porque tiene autos registrados.")
        except Exception as e: messagebox.showerror("Error", str(e))

def cargar_autos():
    for row in tree_autos.get_children(): tree_autos.delete(row)
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT VIN, Make, Model, ModelYear, Color, Id_Customer FROM Carts")
        for row in cursor.fetchall(): tree_autos.insert("", "end", values=[str(val) if val is not None else "" for val in row])
        conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))

def limpiar_auto():
    entry_make.delete(0, 'end'); entry_model.delete(0, 'end'); entry_year.delete(0, 'end'); entry_color.delete(0, 'end')
    combo_customer.set("") 
    if tree_autos.selection(): tree_autos.selection_remove(tree_autos.selection())

def seleccionar_auto(event):
    seleccion = tree_autos.focus()
    if seleccion:
        valores = tree_autos.item(seleccion, 'values')
        limpiar_auto()
        entry_make.insert(0, valores[1]); entry_model.insert(0, valores[2]); entry_year.insert(0, valores[3]); entry_color.insert(0, valores[4])
        id_cliente_buscado = str(valores[5]).replace(',', '')
        for cliente in lista_clientes_combo:
            if cliente.startswith(id_cliente_buscado + " -"):
                combo_customer.set(cliente)
                break

def guardar_auto():
    try:
        seleccion_combo = combo_customer.get()
        if not seleccion_combo or " - " not in seleccion_combo: return messagebox.showwarning("Advertencia", "Por favor seleccione un cliente válido de la lista.")
        id_cliente = int(seleccion_combo.split(" - ")[0])
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Carts (Make, Model, ModelYear, Color, Id_Customer) VALUES (?,?,?,?,?)", (entry_make.get(), entry_model.get(), entry_year.get(), entry_color.get(), id_cliente))
        conn.commit(); conn.close()
        limpiar_auto(); cargar_autos()
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_auto():
    seleccion = tree_autos.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto de la tabla")
    vin = int(str(tree_autos.item(seleccion, 'values')[0]).replace(',', ''))
    try:
        seleccion_combo = combo_customer.get()
        if not seleccion_combo or " - " not in seleccion_combo: return messagebox.showwarning("Advertencia", "Por favor seleccione un cliente válido de la lista.")
        id_cliente = int(seleccion_combo.split(" - ")[0])
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Carts SET Make=?, Model=?, ModelYear=?, Color=?, Id_Customer=? WHERE VIN=?", (entry_make.get(), entry_model.get(), entry_year.get(), entry_color.get(), id_cliente, vin))
        conn.commit(); conn.close()
        limpiar_auto(); cargar_autos()
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_auto():
    seleccion = tree_autos.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto de la tabla")
    vin = int(str(tree_autos.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este auto?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Carts WHERE VIN=?", (vin,))
            conn.commit(); conn.close()
            limpiar_auto(); cargar_autos()
        except pyodbc.IntegrityError: messagebox.showerror("Error", "No se puede eliminar porque tiene servicios registrados.")
        except Exception as e: messagebox.showerror("Error", str(e))

def cargar_servicios():
    for row in tree_servicios.get_children(): tree_servicios.delete(row)
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT Id_Service, ReplacedPart, Duration, Price, Worker, VIN FROM Services")
        for row in cursor.fetchall(): tree_servicios.insert("", "end", values=[str(val) if val is not None else "" for val in row])
        conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))

def limpiar_servicio():
    entry_part.delete(0, 'end'); entry_duration.delete(0, 'end'); entry_price.delete(0, 'end'); entry_worker.delete(0, 'end'); entry_vin_servicio.delete(0, 'end')
    if tree_servicios.selection(): tree_servicios.selection_remove(tree_servicios.selection())

def seleccionar_servicio(event):
    seleccion = tree_servicios.focus()
    if seleccion:
        valores = tree_servicios.item(seleccion, 'values')
        limpiar_servicio()
        entry_part.insert(0, valores[1]); entry_duration.insert(0, valores[2]); entry_price.insert(0, valores[3]); entry_worker.insert(0, valores[4]); entry_vin_servicio.insert(0, valores[5])

def guardar_servicio():
    try:
        vin_auto = int(str(entry_vin_servicio.get()).replace(',', ''))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Services (ReplacedPart, Duration, Price, Worker, VIN) VALUES (?,?,?,?,?)", (entry_part.get(), entry_duration.get(), entry_price.get(), entry_worker.get(), vin_auto))
        conn.commit(); conn.close()
        limpiar_servicio(); cargar_servicios()
    except ValueError: messagebox.showerror("Error", "El campo VIN Auto debe ser numérico.")
    except Exception as e: messagebox.showerror("Error", str(e))

def editar_servicio():
    seleccion = tree_servicios.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un servicio de la tabla")
    id_antiguo = int(str(tree_servicios.item(seleccion, 'values')[0]).replace(',', ''))
    try:
        vin_auto = int(str(entry_vin_servicio.get()).replace(',', ''))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("UPDATE Services SET ReplacedPart=?, Duration=?, Price=?, Worker=?, VIN=? WHERE Id_Service=?", (entry_part.get(), entry_duration.get(), entry_price.get(), entry_worker.get(), vin_auto, id_antiguo))
        conn.commit(); conn.close()
        limpiar_servicio(); cargar_servicios()
    except ValueError: messagebox.showerror("Error", "El campo VIN Auto debe ser numérico.")
    except Exception as e: messagebox.showerror("Error", str(e))

def eliminar_servicio():
    seleccion = tree_servicios.focus()
    if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un servicio de la tabla")
    id_service = int(str(tree_servicios.item(seleccion, 'values')[0]).replace(',', ''))
    if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este servicio?"):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Services WHERE Id_Service=?", (id_service,))
            conn.commit(); conn.close()
            limpiar_servicio(); cargar_servicios()
        except Exception as e: messagebox.showerror("Error", str(e))

def establecer_fondo(ventana):
    try:
        imagen_pillow = Image.open("fondo.webp")
        imagen_fondo_ctk = ctk.CTkImage(light_image=imagen_pillow, dark_image=imagen_pillow, size=(1920, 1080))
        label_fondo = ctk.CTkLabel(ventana, text="", image=imagen_fondo_ctk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception: pass 

# --- Menú principal ---
def abrir_menu_principal():
    global entry_name, entry_lastname, entry_cellphone, tree_clientes
    global entry_make, entry_model, entry_year, entry_color, combo_customer, tree_autos
    global entry_part, entry_duration, entry_price, entry_worker, entry_vin_servicio, tree_servicios
    global chat_display, frame_opciones 

    ventana_menu = ctk.CTkToplevel() 
    ventana_menu.protocol("WM_DELETE_WINDOW", ventana_login.destroy)
    ventana_menu.title("Menú Taller")
    ventana_menu.geometry("1100x700") 
    configurar_estilo_tablas()
    
    # 1. Establecemos el fondo en la ventana principal
    establecer_fondo(ventana_menu)

    # 2. Título "Flat" (Rectangular)
    titulo = ctk.CTkLabel(ventana_menu, text="🔧 Gestión del Taller", font=("Arial", 28, "bold"), text_color=COLOR_BLANCO, fg_color=COLOR_PLACA_TITULO, corner_radius=0, padx=30, pady=10)
    titulo.pack(pady=(20, 10))

    # 3. Contenedor "Flat" (Rectangular) blanco
    main_container = ctk.CTkFrame(ventana_menu, fg_color=COLOR_BLANCO, corner_radius=0)
    main_container.pack(expand=True, fill="both", padx=30, pady=(0, 30))

    tabview = ctk.CTkTabview(main_container, fg_color="transparent", segmented_button_selected_color=COLOR_VERDE_PRINCIPAL, segmented_button_selected_hover_color=COLOR_VERDE_HOVER, text_color=COLOR_NEGRO)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)
    tabview._segmented_button.configure(font=ctk.CTkFont(family="Arial", size=16, weight="bold"))

    # ==========================================
    # PESTAÑA CLIENTES
    # ==========================================
    tab_cliente = tabview.add("Registrar Cliente")
    tab_cliente.grid_columnconfigure(0, weight=1); tab_cliente.grid_columnconfigure(1, weight=2); tab_cliente.grid_rowconfigure(0, weight=1)

    frame_form_cli = ctk.CTkFrame(tab_cliente, fg_color="transparent")
    frame_form_cli.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    ctk.CTkLabel(frame_form_cli, text="Nombre", **LABEL_STYLE).pack(anchor="w")
    entry_name = ctk.CTkEntry(frame_form_cli, width=300, **ENTRY_STYLE); entry_name.pack(pady=(0, 10))
    ctk.CTkLabel(frame_form_cli, text="Apellido", **LABEL_STYLE).pack(anchor="w")
    entry_lastname = ctk.CTkEntry(frame_form_cli, width=300, **ENTRY_STYLE); entry_lastname.pack(pady=(0, 10))
    ctk.CTkLabel(frame_form_cli, text="Teléfono", **LABEL_STYLE).pack(anchor="w")
    entry_cellphone = ctk.CTkEntry(frame_form_cli, width=300, **ENTRY_STYLE); entry_cellphone.pack(pady=(0, 20))

    frame_btn_cli = ctk.CTkFrame(frame_form_cli, fg_color="transparent")
    frame_btn_cli.pack(fill="x")
    ctk.CTkButton(frame_btn_cli, text="Guardar", command=guardar_cliente, fg_color=COLOR_VERDE_PRINCIPAL, width=145).grid(row=0, column=0, padx=(0,5), pady=5)
    ctk.CTkButton(frame_btn_cli, text="Editar", command=editar_cliente, fg_color=COLOR_AZUL, width=145).grid(row=0, column=1, padx=(5,0), pady=5)
    ctk.CTkButton(frame_btn_cli, text="Eliminar", command=eliminar_cliente, fg_color=COLOR_ROJO, width=145).grid(row=1, column=0, padx=(0,5), pady=5)
    ctk.CTkButton(frame_btn_cli, text="Cancelar", command=limpiar_cliente, fg_color=COLOR_GRIS_OSCURO, width=145).grid(row=1, column=1, padx=(5,0), pady=5)

    frame_tabla_cli = ctk.CTkFrame(tab_cliente)
    frame_tabla_cli.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    scroll_cli = ttk.Scrollbar(frame_tabla_cli)
    scroll_cli.pack(side="right", fill="y")
    tree_clientes = ttk.Treeview(frame_tabla_cli, columns=("ID", "Nombre", "Apellido", "Teléfono"), show="headings", yscrollcommand=scroll_cli.set)
    tree_clientes.heading("ID", text="ID"); tree_clientes.column("ID", width=50)
    tree_clientes.heading("Nombre", text="Nombre")
    tree_clientes.heading("Apellido", text="Apellido")
    tree_clientes.heading("Teléfono", text="Teléfono")
    tree_clientes.pack(expand=True, fill="both")
    scroll_cli.config(command=tree_clientes.yview)
    tree_clientes.bind("<ButtonRelease-1>", seleccionar_cliente) 

    # ==========================================
    # PESTAÑA AUTOS
    # ==========================================
    tab_auto = tabview.add("Registrar Auto")
    tab_auto.grid_columnconfigure(0, weight=1); tab_auto.grid_columnconfigure(1, weight=2); tab_auto.grid_rowconfigure(0, weight=1)

    frame_form_auto = ctk.CTkFrame(tab_auto, fg_color="transparent")
    frame_form_auto.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    ctk.CTkLabel(frame_form_auto, text="Marca", **LABEL_STYLE).pack(anchor="w")
    entry_make = ctk.CTkEntry(frame_form_auto, width=300, **ENTRY_STYLE); entry_make.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_auto, text="Modelo", **LABEL_STYLE).pack(anchor="w")
    entry_model = ctk.CTkEntry(frame_form_auto, width=300, **ENTRY_STYLE); entry_model.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_auto, text="Año", **LABEL_STYLE).pack(anchor="w")
    entry_year = ctk.CTkEntry(frame_form_auto, width=300, **ENTRY_STYLE); entry_year.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_auto, text="Color", **LABEL_STYLE).pack(anchor="w")
    entry_color = ctk.CTkEntry(frame_form_auto, width=300, **ENTRY_STYLE); entry_color.pack(pady=(0, 5))
    
    ctk.CTkLabel(frame_form_auto, text="Cliente (Buscar y Seleccionar)", **LABEL_STYLE).pack(anchor="w")
    combo_customer = ctk.CTkComboBox(frame_form_auto, width=300, fg_color=COLOR_BLANCO, text_color=COLOR_NEGRO, border_color=COLOR_GRIS_BORDE, button_color=COLOR_VERDE_PRINCIPAL)
    combo_customer.set("") 
    combo_customer.pack(pady=(0, 15))
    combo_customer.bind("<KeyRelease>", filtrar_clientes)

    frame_btn_auto = ctk.CTkFrame(frame_form_auto, fg_color="transparent")
    frame_btn_auto.pack(fill="x")
    ctk.CTkButton(frame_btn_auto, text="Guardar", command=guardar_auto, fg_color=COLOR_VERDE_PRINCIPAL, width=145).grid(row=0, column=0, padx=(0,5), pady=5)
    ctk.CTkButton(frame_btn_auto, text="Editar", command=editar_auto, fg_color=COLOR_AZUL, width=145).grid(row=0, column=1, padx=(5,0), pady=5)
    ctk.CTkButton(frame_btn_auto, text="Eliminar", command=eliminar_auto, fg_color=COLOR_ROJO, width=145).grid(row=1, column=0, padx=(0,5), pady=5)
    ctk.CTkButton(frame_btn_auto, text="Cancelar", command=limpiar_auto, fg_color=COLOR_GRIS_OSCURO, width=145).grid(row=1, column=1, padx=(5,0), pady=5)

    frame_tabla_auto = ctk.CTkFrame(tab_auto)
    frame_tabla_auto.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    scroll_auto = ttk.Scrollbar(frame_tabla_auto)
    scroll_auto.pack(side="right", fill="y")
    tree_autos = ttk.Treeview(frame_tabla_auto, columns=("VIN", "Marca", "Modelo", "Año", "Color", "ID_Cliente"), show="headings", yscrollcommand=scroll_auto.set)
    for col in ("VIN", "Marca", "Modelo", "Año", "Color", "ID_Cliente"):
        tree_autos.heading(col, text=col)
        tree_autos.column(col, width=80 if col in ("VIN", "Año", "ID_Cliente") else 100)
    tree_autos.pack(expand=True, fill="both")
    scroll_auto.config(command=tree_autos.yview)
    tree_autos.bind("<ButtonRelease-1>", seleccionar_auto)

    # ==========================================
    # PESTAÑA SERVICIOS
    # ==========================================
    tab_servicio = tabview.add("Registrar Servicio")
    tab_servicio.grid_columnconfigure(0, weight=1); tab_servicio.grid_columnconfigure(1, weight=2); tab_servicio.grid_rowconfigure(0, weight=1)

    frame_form_serv = ctk.CTkFrame(tab_servicio, fg_color="transparent")
    frame_form_serv.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    ctk.CTkLabel(frame_form_serv, text="Repuesto", **LABEL_STYLE).pack(anchor="w")
    entry_part = ctk.CTkEntry(frame_form_serv, width=300, **ENTRY_STYLE); entry_part.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_serv, text="Duración", **LABEL_STYLE).pack(anchor="w")
    entry_duration = ctk.CTkEntry(frame_form_serv, width=300, **ENTRY_STYLE); entry_duration.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_serv, text="Precio", **LABEL_STYLE).pack(anchor="w")
    entry_price = ctk.CTkEntry(frame_form_serv, width=300, **ENTRY_STYLE); entry_price.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_serv, text="Mecánico", **LABEL_STYLE).pack(anchor="w")
    entry_worker = ctk.CTkEntry(frame_form_serv, width=300, **ENTRY_STYLE); entry_worker.pack(pady=(0, 5))
    ctk.CTkLabel(frame_form_serv, text="VIN Auto", **LABEL_STYLE).pack(anchor="w")
    entry_vin_servicio = ctk.CTkEntry(frame_form_serv, width=300, **ENTRY_STYLE); entry_vin_servicio.pack(pady=(0, 15))

    frame_btn_serv = ctk.CTkFrame(frame_form_serv, fg_color="transparent")
    frame_btn_serv.pack(fill="x")
    ctk.CTkButton(frame_btn_serv, text="Guardar", command=guardar_servicio, fg_color=COLOR_VERDE_PRINCIPAL, width=145).grid(row=0, column=0, padx=(0,5), pady=5)
    ctk.CTkButton(frame_btn_serv, text="Editar", command=editar_servicio, fg_color=COLOR_AZUL, width=145).grid(row=0, column=1, padx=(5,0), pady=5)
    ctk.CTkButton(frame_btn_serv, text="Eliminar", command=eliminar_servicio, fg_color=COLOR_ROJO, width=145).grid(row=1, column=0, padx=(0,5), pady=5)
    ctk.CTkButton(frame_btn_serv, text="Cancelar", command=limpiar_servicio, fg_color=COLOR_GRIS_OSCURO, width=145).grid(row=1, column=1, padx=(5,0), pady=5)

    frame_tabla_serv = ctk.CTkFrame(tab_servicio)
    frame_tabla_serv.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    scroll_serv = ttk.Scrollbar(frame_tabla_serv)
    scroll_serv.pack(side="right", fill="y")
    tree_servicios = ttk.Treeview(frame_tabla_serv, columns=("ID", "Repuesto", "Duración", "Precio", "Mecánico", "VIN"), show="headings", yscrollcommand=scroll_serv.set)
    for col in ("ID", "Repuesto", "Duración", "Precio", "Mecánico", "VIN"):
        tree_servicios.heading(col, text=col)
        tree_servicios.column(col, width=80 if col in ("ID", "Precio", "VIN") else 100)
    tree_servicios.pack(expand=True, fill="both")
    scroll_serv.config(command=tree_servicios.yview)
    tree_servicios.bind("<ButtonRelease-1>", seleccionar_servicio)

    # ==========================================
    # PESTAÑA ASISTENTE VIRTUAL (BOT)
    # ==========================================
    tab_bot = tabview.add("Asistente Virtual")
    tab_bot.grid_columnconfigure(0, weight=1)
    tab_bot.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(tab_bot, text="🤖 Asistente Inteligente del Taller", font=("Arial", 20, "bold"), text_color=COLOR_VERDE_PRINCIPAL).grid(row=0, column=0, pady=(10, 5))

    chat_display = ctk.CTkTextbox(tab_bot, fg_color=COLOR_BLANCO, text_color=COLOR_NEGRO, border_color=COLOR_GRIS_BORDE, border_width=1, font=("Arial", 14))
    chat_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
    chat_display.insert("end", "🤖 Bot: ¡Hola! Selecciona una de las opciones de abajo para comenzar.\n" + "-"*50 + "\n\n")
    chat_display.configure(state="disabled")

    frame_opciones = ctk.CTkFrame(tab_bot, fg_color="transparent")
    frame_opciones.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")
    
    dibujar_menu_principal_bot()

    cargar_clientes(); cargar_autos(); cargar_servicios(); actualizar_clientes_combo() 
    ventana_menu.mainloop()

# --- Ventana de login ---
def login():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (usuario, contraseña))
        resultado = cursor.fetchone()
        if resultado:
            ventana_login.withdraw() 
            abrir_menu_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        conn.close()
    except Exception as e: messagebox.showerror("Error de Conexión", str(e))

ventana_login = ctk.CTk()
ventana_login.title("Login Taller")
ventana_login.geometry("450x500")

establecer_fondo(ventana_login)

# Login también cuadrado
frame_login = ctk.CTkFrame(ventana_login, fg_color=COLOR_BLANCO, corner_radius=0, border_width=1, border_color=COLOR_GRIS_BORDE)
frame_login.pack(pady=40, padx=40, fill="both", expand=True)

ctk.CTkLabel(frame_login, text="👤 Iniciar Sesión", font=("Arial", 24, "bold"), text_color=COLOR_NEGRO).pack(pady=(40, 25))
ctk.CTkLabel(frame_login, text="Usuario", **LABEL_STYLE).pack(anchor="w", padx=65)
entry_usuario = ctk.CTkEntry(frame_login, width=250, **ENTRY_STYLE); entry_usuario.pack(pady=(0, 15))
ctk.CTkLabel(frame_login, text="Contraseña", **LABEL_STYLE).pack(anchor="w", padx=65)
entry_contraseña = ctk.CTkEntry(frame_login, show="*", width=250, **ENTRY_STYLE); entry_contraseña.pack(pady=(0, 20))

ctk.CTkButton(frame_login, text="Ingresar", command=login, width=250, height=45, fg_color=COLOR_VERDE_PRINCIPAL).pack(pady=(20, 40))

ventana_login.mainloop()