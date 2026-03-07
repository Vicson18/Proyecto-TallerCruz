import customtkinter as ctk
import pyodbc
from tkinter import messagebox

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

ENTRY_STYLE = {
    "fg_color": COLOR_BLANCO,
    "text_color": COLOR_NEGRO,
    "border_color": COLOR_GRIS_BORDE,
    "border_width": 1,
    "placeholder_text_color": "gray"
}

BUTTON_STYLE = {
    "fg_color": COLOR_VERDE_PRINCIPAL,
    "hover_color": COLOR_VERDE_HOVER,
    "text_color": COLOR_BLANCO,
    "font": ("Arial", 14, "bold") 
}

LABEL_STYLE = {
    "font": ("Arial", 12, "bold"),
    "text_color": "#666666" # Un gris oscuro para las etiquetas
}
# ------------------------------------

# Conexión a SQL Server
def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  
        'DATABASE=taller;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )

def guardar_cliente(name, lastname, cellphone):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (Name, LastName, Cellphone, InsertedDate) VALUES (?,?,?, GETDATE())",
                       (name, lastname, cellphone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Cliente registrado correctamente")
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", str(e))

def guardar_auto(make, model, year, color, customer):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Carts (Make, Model, ModelYear, Color, Id_Customer) VALUES (?,?,?,?,?)",
                       (make, model, year, color, customer))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Auto registrado correctamente")
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", str(e))

def guardar_servicio(id_service, part, duration, price, worker, vin_referencia):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Services (Id_Service, ReplacedPart, Duration, Price, Worker, VIN) VALUES (?,?,?,?,?,?)",
                       (id_service, part, duration, price, worker, vin_referencia))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Servicio registrado correctamente")
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", str(e))

# --- Menú principal ---
def abrir_menu_principal():
    ventana_menu = ctk.CTk()
    ventana_menu.title("Menú Taller")
    ventana_menu.geometry("800x650") # Ajustado para que el grid respire
    ventana_menu.configure(fg_color=COLOR_GRIS_CLARO)

    # Título con ícono
    titulo = ctk.CTkLabel(ventana_menu, text="🔧 Gestión del Taller", font=("Arial", 28, "bold"), text_color=COLOR_NEGRO)
    titulo.pack(pady=(40, 20))

    tabview = ctk.CTkTabview(
        ventana_menu,
        fg_color=COLOR_BLANCO, 
        segmented_button_fg_color=COLOR_GRIS_CLARO, 
        segmented_button_selected_color=COLOR_VERDE_PRINCIPAL, 
        segmented_button_selected_hover_color=COLOR_VERDE_HOVER, 
        segmented_button_unselected_color=COLOR_GRIS_CLARO, 
        segmented_button_unselected_hover_color="#e0e0e0", 
        text_color=COLOR_NEGRO, 
        corner_radius=12,
        border_width=1,
        border_color=COLOR_GRIS_BORDE,
        height=480
    )
    tabview.pack(expand=True, fill="both", padx=50, pady=(0, 40))

    fuente_pestanas = ctk.CTkFont(family="Arial", size=18, weight="bold")
    tabview._segmented_button.configure(font=fuente_pestanas)

    # ==========================================
    # PESTAÑA 1: REGISTRAR CLIENTE (1 Columna)
    # ==========================================
    tab_cliente = tabview.add("Registrar Cliente")
    
    # Usamos un Frame transparente para centrar todo el formulario
    frame_cliente = ctk.CTkFrame(tab_cliente, fg_color="transparent")
    frame_cliente.pack(pady=20, expand=True)

    ctk.CTkLabel(frame_cliente, text="Nombre", **LABEL_STYLE).pack(anchor="w", padx=5)
    entry_name = ctk.CTkEntry(frame_cliente, width=400, **ENTRY_STYLE)
    entry_name.pack(pady=(0, 15))

    ctk.CTkLabel(frame_cliente, text="Apellido", **LABEL_STYLE).pack(anchor="w", padx=5)
    entry_lastname = ctk.CTkEntry(frame_cliente, width=400, **ENTRY_STYLE)
    entry_lastname.pack(pady=(0, 15))

    ctk.CTkLabel(frame_cliente, text="Teléfono", **LABEL_STYLE).pack(anchor="w", padx=5)
    entry_cellphone = ctk.CTkEntry(frame_cliente, width=400, **ENTRY_STYLE)
    entry_cellphone.pack(pady=(0, 20))

    ctk.CTkButton(frame_cliente, text="Guardar Cliente", width=400, height=45, **BUTTON_STYLE,
                  command=lambda: guardar_cliente(entry_name.get(), entry_lastname.get(), entry_cellphone.get())
                  ).pack(pady=10)

    # ==========================================
    # PESTAÑA 2: REGISTRAR AUTO (2 Columnas)
    # ==========================================
    tab_auto = tabview.add("Registrar Auto")
    
    frame_auto = ctk.CTkFrame(tab_auto, fg_color="transparent")
    frame_auto.pack(pady=30, expand=True)

    # Fila 1: Marca y Modelo
    ctk.CTkLabel(frame_auto, text="Marca", **LABEL_STYLE).grid(row=0, column=0, sticky="w", padx=15)
    ctk.CTkLabel(frame_auto, text="Modelo", **LABEL_STYLE).grid(row=0, column=1, sticky="w", padx=15)
    entry_make = ctk.CTkEntry(frame_auto, width=220, **ENTRY_STYLE)
    entry_make.grid(row=1, column=0, padx=15, pady=(0, 15))
    entry_model = ctk.CTkEntry(frame_auto, width=220, **ENTRY_STYLE)
    entry_model.grid(row=1, column=1, padx=15, pady=(0, 15))

    # Fila 2: Año y Color
    ctk.CTkLabel(frame_auto, text="Año", **LABEL_STYLE).grid(row=2, column=0, sticky="w", padx=15)
    ctk.CTkLabel(frame_auto, text="Color", **LABEL_STYLE).grid(row=2, column=1, sticky="w", padx=15)
    entry_year = ctk.CTkEntry(frame_auto, width=220, **ENTRY_STYLE)
    entry_year.grid(row=3, column=0, padx=15, pady=(0, 15))
    entry_color = ctk.CTkEntry(frame_auto, width=220, **ENTRY_STYLE)
    entry_color.grid(row=3, column=1, padx=15, pady=(0, 15))

    # Fila 3: ID Cliente (Centrado ocupando 2 columnas o solo en la izquierda)
    ctk.CTkLabel(frame_auto, text="ID Cliente (Número)", **LABEL_STYLE).grid(row=4, column=0, sticky="w", padx=15)
    entry_customer = ctk.CTkEntry(frame_auto, width=220, **ENTRY_STYLE)
    entry_customer.grid(row=5, column=0, padx=15, pady=(0, 20), sticky="w")

    # Fila 4: Botón
    ctk.CTkButton(frame_auto, text="Guardar Auto", width=470, height=45, **BUTTON_STYLE,
                  command=lambda: guardar_auto(entry_make.get(), entry_model.get(), entry_year.get(),
                                               entry_color.get(), entry_customer.get())
                  ).grid(row=6, column=0, columnspan=2, pady=10)


    # ==========================================
    # PESTAÑA 3: REGISTRAR SERVICIO (2 Columnas)
    # ==========================================
    tab_servicio = tabview.add("Registrar Servicio")

    frame_servicio = ctk.CTkFrame(tab_servicio, fg_color="transparent")
    frame_servicio.pack(pady=20, expand=True)

    # Fila 1: ID Servicio y Repuesto
    ctk.CTkLabel(frame_servicio, text="ID Servicio (Número)", **LABEL_STYLE).grid(row=0, column=0, sticky="w", padx=15)
    ctk.CTkLabel(frame_servicio, text="Repuesto a cambiar", **LABEL_STYLE).grid(row=0, column=1, sticky="w", padx=15)
    entry_id_service = ctk.CTkEntry(frame_servicio, width=220, **ENTRY_STYLE)
    entry_id_service.grid(row=1, column=0, padx=15, pady=(0, 15))
    entry_part = ctk.CTkEntry(frame_servicio, width=220, **ENTRY_STYLE)
    entry_part.grid(row=1, column=1, padx=15, pady=(0, 15))

    # Fila 2: Duración y Precio
    ctk.CTkLabel(frame_servicio, text="Duración (Ej. 2 horas)", **LABEL_STYLE).grid(row=2, column=0, sticky="w", padx=15)
    ctk.CTkLabel(frame_servicio, text="Precio", **LABEL_STYLE).grid(row=2, column=1, sticky="w", padx=15)
    entry_duration = ctk.CTkEntry(frame_servicio, width=220, **ENTRY_STYLE)
    entry_duration.grid(row=3, column=0, padx=15, pady=(0, 15))
    entry_price = ctk.CTkEntry(frame_servicio, width=220, **ENTRY_STYLE)
    entry_price.grid(row=3, column=1, padx=15, pady=(0, 15))

    # Fila 3: Mecánico y VIN
    ctk.CTkLabel(frame_servicio, text="Mecánico asignado", **LABEL_STYLE).grid(row=4, column=0, sticky="w", padx=15)
    ctk.CTkLabel(frame_servicio, text="VIN del Auto (Número)", **LABEL_STYLE).grid(row=4, column=1, sticky="w", padx=15)
    entry_worker = ctk.CTkEntry(frame_servicio, width=220, **ENTRY_STYLE)
    entry_worker.grid(row=5, column=0, padx=15, pady=(0, 20))
    entry_vin_servicio = ctk.CTkEntry(frame_servicio, width=220, **ENTRY_STYLE)
    entry_vin_servicio.grid(row=5, column=1, padx=15, pady=(0, 20))

    # Fila 4: Botón
    ctk.CTkButton(frame_servicio, text="Guardar Servicio", width=470, height=45, **BUTTON_STYLE,
                  command=lambda: guardar_servicio(entry_id_service.get(), entry_part.get(), entry_duration.get(),
                                                   entry_price.get(), entry_worker.get(), entry_vin_servicio.get())
                  ).grid(row=6, column=0, columnspan=2, pady=10)

    ventana_menu.mainloop()


# --- Ventana de login ---
def login():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (usuario, contraseña))
        resultado = cursor.fetchone()
        
        if resultado:
            ventana_login.destroy()
            abrir_menu_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        conn.close()
    except Exception as e:
        messagebox.showerror("Error de Conexión o Interfaz", f"Ocurrió un problema:\n{str(e)}")

ventana_login = ctk.CTk()
ventana_login.title("Login Taller")
ventana_login.geometry("450x500")
ventana_login.configure(fg_color=COLOR_GRIS_CLARO)

frame_login = ctk.CTkFrame(ventana_login, fg_color=COLOR_BLANCO, corner_radius=15, border_width=1, border_color=COLOR_GRIS_BORDE)
frame_login.pack(pady=40, padx=40, fill="both", expand=True)

# Ícono y título en el login
ctk.CTkLabel(frame_login, text="👤 Iniciar Sesión", font=("Arial", 24, "bold"), text_color=COLOR_NEGRO).pack(pady=(40, 25))

ctk.CTkLabel(frame_login, text="Usuario", **LABEL_STYLE).pack(anchor="w", padx=65)
entry_usuario = ctk.CTkEntry(frame_login, width=250, **ENTRY_STYLE)
entry_usuario.pack(pady=(0, 15))

ctk.CTkLabel(frame_login, text="Contraseña", **LABEL_STYLE).pack(anchor="w", padx=65)
entry_contraseña = ctk.CTkEntry(frame_login, show="*", width=250, **ENTRY_STYLE)
entry_contraseña.pack(pady=(0, 20))

ctk.CTkButton(frame_login, text="Ingresar", command=login, width=250, height=45, **BUTTON_STYLE).pack(pady=(20, 40))

ventana_login.mainloop()