import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

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

# Guardar Cliente
def guardar_cliente(name, lastname, cellphone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Customers (Name, LastName, Cellphone) VALUES (?,?,?)",
        (name, lastname, cellphone)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Cliente registrado correctamente")

# Guardar Auto
def guardar_auto(make, model, year, color, vin, customer):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Carts (Make, Model, ModelYear, Color, VIN, Id_Customer) VALUES (?,?,?,?,?,?)",
        (make, model, year, color, vin, customer)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Auto registrado correctamente")

# Guardar Servicio
def guardar_servicio(part, duration, price, worker, mileage, cart):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Services (ReplacedPart, Duration, Price, Worker, Mileage, Id_Cart) VALUES (?,?,?,?,?,?)",
        (part, duration, price, worker, mileage, cart)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Servicio registrado correctamente")

# Menú principal con pestañas y estilo
def abrir_menu_principal():
    ventana_menu = tk.Tk()
    ventana_menu.title("Menú Taller")
    ventana_menu.geometry("500x400")

    # --- Estilo moderno ---
    style = ttk.Style()
    style.theme_use("clam")  # Puedes probar "alt", "default", "clam"
    style.configure("TNotebook", background="#f0f0f0")
    style.configure("TNotebook.Tab", padding=[10, 5], font=("Arial", 10, "bold"))
    style.configure("TButton", font=("Arial", 10), padding=6)
    style.configure("TLabel", font=("Arial", 10))

    notebook = ttk.Notebook(ventana_menu)
    notebook.pack(expand=True, fill="both")

    # --- Pestaña Cliente ---
    frame_cliente = ttk.Frame(notebook)
    notebook.add(frame_cliente, text="Registrar Cliente")

    ttk.Label(frame_cliente, text="Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_name = ttk.Entry(frame_cliente); entry_name.grid(row=0, column=1)

    ttk.Label(frame_cliente, text="LastName").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_lastname = ttk.Entry(frame_cliente); entry_lastname.grid(row=1, column=1)

    ttk.Label(frame_cliente, text="Cellphone").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_cellphone = ttk.Entry(frame_cliente); entry_cellphone.grid(row=2, column=1)

    ttk.Button(frame_cliente, text="Guardar Cliente",
               command=lambda: guardar_cliente(entry_name.get(), entry_lastname.get(), entry_cellphone.get())
               ).grid(row=3, columnspan=2, pady=10)

    # --- Pestaña Auto ---
    frame_auto = ttk.Frame(notebook)
    notebook.add(frame_auto, text="Registrar Auto")

    ttk.Label(frame_auto, text="Make").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_make = ttk.Entry(frame_auto); entry_make.grid(row=0, column=1)

    ttk.Label(frame_auto, text="Model").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_model = ttk.Entry(frame_auto); entry_model.grid(row=1, column=1)

    ttk.Label(frame_auto, text="ModelYear").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_year = ttk.Entry(frame_auto); entry_year.grid(row=2, column=1)

    ttk.Label(frame_auto, text="Color").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_color = ttk.Entry(frame_auto); entry_color.grid(row=3, column=1)

    ttk.Label(frame_auto, text="VIN").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_vin = ttk.Entry(frame_auto); entry_vin.grid(row=4, column=1)

    ttk.Label(frame_auto, text="Id_Customer").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    entry_customer = ttk.Entry(frame_auto); entry_customer.grid(row=5, column=1)

    ttk.Button(frame_auto, text="Guardar Auto",
               command=lambda: guardar_auto(entry_make.get(), entry_model.get(), entry_year.get(),
                                            entry_color.get(), entry_vin.get(), entry_customer.get())
               ).grid(row=6, columnspan=2, pady=10)

    # --- Pestaña Servicio ---
    frame_servicio = ttk.Frame(notebook)
    notebook.add(frame_servicio, text="Registrar Servicio")

    ttk.Label(frame_servicio, text="ReplacedPart").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_part = ttk.Entry(frame_servicio); entry_part.grid(row=0, column=1)

    ttk.Label(frame_servicio, text="Duration").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_duration = ttk.Entry(frame_servicio); entry_duration.grid(row=1, column=1)

    ttk.Label(frame_servicio, text="Price").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_price = ttk.Entry(frame_servicio); entry_price.grid(row=2, column=1)

    ttk.Label(frame_servicio, text="Worker").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_worker = ttk.Entry(frame_servicio); entry_worker.grid(row=3, column=1)

    ttk.Label(frame_servicio, text="Mileage").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_mileage = ttk.Entry(frame_servicio); entry_mileage.grid(row=4, column=1)

    ttk.Label(frame_servicio, text="Id_Cart").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    entry_cart = ttk.Entry(frame_servicio); entry_cart.grid(row=5, column=1)

    ttk.Button(frame_servicio, text="Guardar Servicio",
               command=lambda: guardar_servicio(entry_part.get(), entry_duration.get(), entry_price.get(),
                                                entry_worker.get(), entry_mileage.get(), entry_cart.get())
               ).grid(row=6, columnspan=2, pady=10)

    ventana_menu.mainloop()

# Ventana de login
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

ventana_login = tk.Tk()
ventana_login.title("Login Taller")
ventana_login.geometry("300x150")

ttk.Label(ventana_login, text="Usuario").pack(pady=5)
entry_usuario = ttk.Entry(ventana_login)
entry_usuario.pack()

ttk.Label(ventana_login, text="Contraseña").pack(pady=5)
entry_contraseña = ttk.Entry(ventana_login, show="*")
entry_contraseña.pack()

ttk.Button(ventana_login, text="Ingresar", command=login).pack(pady=10)

ventana_login.mainloop()