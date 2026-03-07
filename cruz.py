import customtkinter as ctk
import pyodbc
from tkinter import messagebox

# Configuración del tema
ctk.set_appearance_mode("light")  # "light" o "dark"
ctk.set_default_color_theme("blue")  # opciones: "blue", "green", "dark-blue"

# Conexión a SQL Server
def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=DESKTOP-PG4PTAU\\SQLEXPRESS;'
        'DATABASE=taller;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )

# Funciones de guardado
def guardar_cliente(name, lastname, cellphone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Customers (Name, LastName, Cellphone) VALUES (?,?,?)",
                   (name, lastname, cellphone))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Cliente registrado correctamente")

def guardar_auto(make, model, year, color, vin, customer):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Carts (Make, Model, ModelYear, Color, VIN, Id_Customer) VALUES (?,?,?,?,?,?)",
                   (make, model, year, color, vin, customer))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Auto registrado correctamente")

def guardar_servicio(part, duration, price, worker, mileage, cart):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Services (ReplacedPart, Duration, Price, Worker, Mileage, Id_Cart) VALUES (?,?,?,?,?,?)",
                   (part, duration, price, worker, mileage, cart))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Servicio registrado correctamente")

# Menú principal con pestañas modernas
def abrir_menu_principal():
    ventana_menu = ctk.CTk()
    ventana_menu.title("Menú Taller")
    ventana_menu.geometry("600x400")

    tabview = ctk.CTkTabview(ventana_menu)
    tabview.pack(expand=True, fill="both", padx=20, pady=20)

    # --- Pestaña Cliente ---
    tab_cliente = tabview.add("Registrar Cliente")
    entry_name = ctk.CTkEntry(tab_cliente, placeholder_text="Name")
    entry_name.pack(pady=10)
    entry_lastname = ctk.CTkEntry(tab_cliente, placeholder_text="LastName")
    entry_lastname.pack(pady=10)
    entry_cellphone = ctk.CTkEntry(tab_cliente, placeholder_text="Cellphone")
    entry_cellphone.pack(pady=10)
    ctk.CTkButton(tab_cliente, text="Guardar Cliente",
                  command=lambda: guardar_cliente(entry_name.get(), entry_lastname.get(), entry_cellphone.get())
                  ).pack(pady=15)

    # --- Pestaña Auto ---
    tab_auto = tabview.add("Registrar Auto")
    entry_make = ctk.CTkEntry(tab_auto, placeholder_text="Make"); entry_make.pack(pady=10)
    entry_model = ctk.CTkEntry(tab_auto, placeholder_text="Model"); entry_model.pack(pady=10)
    entry_year = ctk.CTkEntry(tab_auto, placeholder_text="ModelYear"); entry_year.pack(pady=10)
    entry_color = ctk.CTkEntry(tab_auto, placeholder_text="Color"); entry_color.pack(pady=10)
    entry_vin = ctk.CTkEntry(tab_auto, placeholder_text="VIN"); entry_vin.pack(pady=10)
    entry_customer = ctk.CTkEntry(tab_auto, placeholder_text="Id_Customer"); entry_customer.pack(pady=10)
    ctk.CTkButton(tab_auto, text="Guardar Auto",
                  command=lambda: guardar_auto(entry_make.get(), entry_model.get(), entry_year.get(),
                                               entry_color.get(), entry_vin.get(), entry_customer.get())
                  ).pack(pady=15)

    # --- Pestaña Servicio ---
    tab_servicio = tabview.add("Registrar Servicio")
    entry_part = ctk.CTkEntry(tab_servicio, placeholder_text="ReplacedPart"); entry_part.pack(pady=10)
    entry_duration = ctk.CTkEntry(tab_servicio, placeholder_text="Duration"); entry_duration.pack(pady=10)
    entry_price = ctk.CTkEntry(tab_servicio, placeholder_text="Price"); entry_price.pack(pady=10)
    entry_worker = ctk.CTkEntry(tab_servicio, placeholder_text="Worker"); entry_worker.pack(pady=10)
    entry_mileage = ctk.CTkEntry(tab_servicio, placeholder_text="Mileage"); entry_mileage.pack(pady=10)
    entry_cart = ctk.CTkEntry(tab_servicio, placeholder_text="Id_Cart"); entry_cart.pack(pady=10)
    ctk.CTkButton(tab_servicio, text="Guardar Servicio",
                  command=lambda: guardar_servicio(entry_part.get(), entry_duration.get(), entry_price.get(),
                                                   entry_worker.get(), entry_mileage.get(), entry_cart.get())
                  ).pack(pady=15)

    ventana_menu.mainloop()

# Ventana de login con CustomTkinter
def login():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (usuario, contraseña))
    resultado = cursor.fetchone()
    if resultado:
        messagebox.showinfo("Login", f"Bienvenido {usuario}")
        ventana_login.destroy()
        abrir_menu_principal()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    conn.close()

ventana_login = ctk.CTk()
ventana_login.title("Login Taller")
ventana_login.geometry("300x200")

entry_usuario = ctk.CTkEntry(ventana_login, placeholder_text="Usuario")
entry_usuario.pack(pady=10)

entry_contraseña = ctk.CTkEntry(ventana_login, placeholder_text="Contraseña", show="*")
entry_contraseña.pack(pady=10)

ctk.CTkButton(ventana_login, text="Ingresar", command=login).pack(pady=20)

ventana_login.mainloop()