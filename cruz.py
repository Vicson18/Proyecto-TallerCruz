import tkinter as tk
from tkinter import messagebox
import pyodbc

# Conexión a SQL Server
def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=DESKTOP-PG4PTAU\\SQLEXPRESS;' 
                      # Cambia si tu servidor tiene otro nombre
        'DATABASE=taller;'         # Tu base de datos
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'    # Si usas autenticación de Windows
    )
    # Si usas usuario/contraseña:
    # 'UID=tu_usuario;PWD=tu_contraseña;'

# Función de login
def login():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Name=? AND Password=?", (usuario, contraseña))
    resultado = cursor.fetchone()
    if resultado:
        messagebox.showinfo("Login", f"Bienvenido {usuario}")
        ventana_login.destroy()
        abrir_menu_principal()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    conn.close()

# Menú principal
def abrir_menu_principal():
    ventana_menu = tk.Tk()
    ventana_menu.title("Menú Taller")

    tk.Button(ventana_menu, text="Registrar Cliente", command=registrar_customer).pack(pady=10)
    tk.Button(ventana_menu, text="Registrar Auto", command=registrar_auto).pack(pady=10)
    tk.Button(ventana_menu, text="Registrar Servicio", command=registrar_servicio).pack(pady=10)

    ventana_menu.mainloop()

# Formulario para registrar clientes
def registrar_customer():
    ventana_customer = tk.Toplevel()
    ventana_customer.title("Registrar Cliente")

    tk.Label(ventana_customer, text="Name").pack()
    name = tk.Entry(ventana_customer); name.pack()

    tk.Label(ventana_customer, text="LastName").pack()
    lastname = tk.Entry(ventana_customer); lastname.pack()

    tk.Label(ventana_customer, text="Cellphone").pack()
    cellphone = tk.Entry(ventana_customer); cellphone.pack()

    def guardar_customer():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customers (Name, LastName, Cellphone) VALUES (?,?,?)",
            (name.get(), lastname.get(), cellphone.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Cliente registrado correctamente")
        ventana_customer.destroy()

    tk.Button(ventana_customer, text="Guardar", command=guardar_customer).pack(pady=10)

# Formulario para registrar autos
def registrar_auto():
    ventana_auto = tk.Toplevel()
    ventana_auto.title("Registrar Auto")

    tk.Label(ventana_auto, text="Make").pack()
    make = tk.Entry(ventana_auto); make.pack()

    tk.Label(ventana_auto, text="Model").pack()
    model = tk.Entry(ventana_auto); model.pack()

    tk.Label(ventana_auto, text="ModelYear").pack()
    year = tk.Entry(ventana_auto); year.pack()

    tk.Label(ventana_auto, text="Color").pack()
    color = tk.Entry(ventana_auto); color.pack()

    tk.Label(ventana_auto, text="VIN").pack()
    vin = tk.Entry(ventana_auto); vin.pack()

    tk.Label(ventana_auto, text="Id_Customer").pack()
    customer = tk.Entry(ventana_auto); customer.pack()

    def guardar_auto():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Carts (Make, Model, ModelYear, Color, VIN, Id_Customer) VALUES (?,?,?,?,?,?)",
            (make.get(), model.get(), year.get(), color.get(), vin.get(), customer.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Auto registrado correctamente")
        ventana_auto.destroy()

    tk.Button(ventana_auto, text="Guardar", command=guardar_auto).pack(pady=10)

# Formulario para registrar servicios
def registrar_servicio():
    ventana_servicio = tk.Toplevel()
    ventana_servicio.title("Registrar Servicio")

    tk.Label(ventana_servicio, text="ReplacedPart").pack()
    part = tk.Entry(ventana_servicio); part.pack()

    tk.Label(ventana_servicio, text="Duration").pack()
    duration = tk.Entry(ventana_servicio); duration.pack()

    tk.Label(ventana_servicio, text="Price").pack()
    price = tk.Entry(ventana_servicio); price.pack()

    tk.Label(ventana_servicio, text="Worker").pack()
    worker = tk.Entry(ventana_servicio); worker.pack()

    tk.Label(ventana_servicio, text="Mileage").pack()
    mileage = tk.Entry(ventana_servicio); mileage.pack()

    tk.Label(ventana_servicio, text="Id_Cart").pack()
    cart = tk.Entry(ventana_servicio); cart.pack()

    def guardar_servicio():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Services (ReplacedPart, Duration, Price, Worker, Mileage, Id_Cart) VALUES (?,?,?,?,?,?)",
            (part.get(), duration.get(), price.get(), worker.get(), mileage.get(), cart.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Servicio registrado correctamente")
        ventana_servicio.destroy()

    tk.Button(ventana_servicio, text="Guardar", command=guardar_servicio).pack(pady=10)

# Ventana de login
ventana_login = tk.Tk()
ventana_login.title("Login Taller")

tk.Label(ventana_login, text="Usuario").pack()
entry_usuario = tk.Entry(ventana_login)
entry_usuario.pack()

tk.Label(ventana_login, text="Contraseña").pack()
entry_contraseña = tk.Entry(ventana_login, show="*")
entry_contraseña.pack()

tk.Button(ventana_login, text="Ingresar", command=login).pack(pady=10)

ventana_login.mainloop()