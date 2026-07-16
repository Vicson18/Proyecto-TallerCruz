import customtkinter as ctk
from tkinter import messagebox, ttk

import estado
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT,
                     COLOR_TEXT_MAIN, COLOR_TEXT_DIM, ENTRY_STYLE, LABEL_STYLE,
                     hacer_boton_accion)


class FrameClientes:
    def __init__(self, parent):
        self.build(parent)
        self.cargar()

    def build(self, parent):
        cli_outer = ctk.CTkFrame(parent, fg_color="transparent")
        cli_outer.pack(expand=True, fill="both", padx=32, pady=(20, 20))

        # Header tipo tarjeta: icono + título + descripción, contador en vivo a la derecha
        cli_header = ctk.CTkFrame(cli_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                   border_width=1, border_color=COLOR_BORDER, height=60)
        cli_header.pack(fill="x", pady=(0, 16))
        cli_header.pack_propagate(False)
        ctk.CTkFrame(cli_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        cli_header_txt = ctk.CTkFrame(cli_header, fg_color="transparent")
        cli_header_txt.pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(cli_header_txt, text="👤  GESTIÓN DE CLIENTES",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(cli_header_txt, text="Registro, edición y consulta del expediente de clientes",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        self.lbl_total = ctk.CTkLabel(cli_header, text="0 CLIENTES",
                                       font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT)
        self.lbl_total.pack(side="right", padx=20)

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

        self.entry_name = self._campo(f_form_cli, "NOMBRE", "Nombre")
        self.entry_lastname = self._campo(f_form_cli, "APELLIDO", "Apellido")
        self.entry_cellphone = self._campo(f_form_cli, "TELÉFONO", "Teléfono")

        ctk.CTkFrame(f_form_cli, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
        hacer_boton_accion(f_form_cli, "REGISTRAR", COLOR_ACCENT, self.guardar, "＋").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_cli, "ACTUALIZAR", "#1a3a1a", self.editar, "✎").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_cli, "DAR DE BAJA", "#2a1010", self.eliminar, "✕").pack(fill="x", padx=24, pady=3)
        ctk.CTkButton(f_form_cli, text="LIMPIAR", fg_color="transparent", border_width=1,
                      border_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM, height=36,
                      corner_radius=4, font=("Segoe UI", 11),
                      command=self.limpiar).pack(fill="x", padx=24, pady=(10, 16))

        t_frame_cli = ctk.CTkFrame(cli_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                    border_width=1, border_color=COLOR_BORDER)
        t_frame_cli.pack(side="right", expand=True, fill="both")
        ctk.CTkFrame(t_frame_cli, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        cli_tabla_toolbar = ctk.CTkFrame(t_frame_cli, fg_color="transparent")
        cli_tabla_toolbar.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(cli_tabla_toolbar, text="🔍", font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_DIM).pack(side="left", padx=(0, 8))
        self.buscar_entry = ctk.CTkEntry(cli_tabla_toolbar, placeholder_text="Buscar por nombre, apellido o teléfono...",
                                          height=36, **ENTRY_STYLE)
        self.buscar_entry.pack(side="left", expand=True, fill="x")
        self.buscar_entry.bind("<KeyRelease>", lambda e: self.cargar(self.buscar_entry.get().strip()))

        self.tree = ttk.Treeview(t_frame_cli, columns=("ID","Nombre","Apellido","Tel"), show="headings")
        for c, w in [("ID",70),("Nombre",220),("Apellido",220),("Tel",160)]:
            self.tree.heading(c, text=c); self.tree.column(c, width=w)
        self.tree.pack(expand=True, fill="both", padx=2, pady=(0, 2))
        self.tree.bind("<ButtonRelease-1>", self.seleccionar)

    def _campo(self, parent, lbl, ph):
        ctk.CTkLabel(parent, text=lbl, **LABEL_STYLE).pack(anchor="w", padx=24, pady=(6, 0))
        e = ctk.CTkEntry(parent, placeholder_text=ph, width=310, height=42, **ENTRY_STYLE)
        e.pack(padx=24, pady=(2, 0))
        return e

    def cargar(self, filtro=""):
        for row in self.tree.get_children(): self.tree.delete(row)
        try:
            conn = conectar(); cursor = conn.cursor()
            if filtro:
                like = f"%{filtro}%"
                cursor.execute(
                    "SELECT Id_Customer, Name, LastName, Cellphone FROM Customers "
                    "WHERE Name LIKE ? OR LastName LIKE ? OR Cellphone LIKE ?", (like, like, like))
            else:
                cursor.execute("SELECT Id_Customer, Name, LastName, Cellphone FROM Customers")
            filas = cursor.fetchall()
            for i, row in enumerate(filas):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=[str(v) if v is not None else "" for v in row], tags=(tag,))
            self.tree.tag_configure('even', background=COLOR_BG_CARD)
            self.tree.tag_configure('odd', background=COLOR_BG_CARD_ALT)
            etiqueta = "RESULTADO" if filtro else "CLIENTE"
            self.lbl_total.configure(text=f"{len(filas)} {etiqueta}{'S' if len(filas) != 1 else ''}")
            conn.close()
        except Exception as e: print(e)

    def guardar(self):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("INSERT INTO Customers (Name, LastName, Cellphone, InsertedDate) VALUES (?,?,?, GETDATE())",
                           (self.entry_name.get(), self.entry_lastname.get(), self.entry_cellphone.get()))
            conn.commit(); conn.close()
            self.cargar(); estado.actualizar_datos_precarga(); self.limpiar()
            messagebox.showinfo("Éxito", "Cliente registrado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def editar(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente.")
        id_cliente = int(str(self.tree.item(seleccion, 'values')[0]).replace(',', ''))
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("UPDATE Customers SET Name=?, LastName=?, Cellphone=? WHERE Id_Customer=?",
                           (self.entry_name.get(), self.entry_lastname.get(), self.entry_cellphone.get(), id_cliente))
            conn.commit(); conn.close()
            messagebox.showinfo("Éxito", "Datos actualizados.")
            self.limpiar(); self.cargar(); estado.actualizar_datos_precarga()
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un cliente.")
        id_cliente = int(str(self.tree.item(seleccion, 'values')[0]).replace(',', ''))
        if messagebox.askyesno("Confirmar", "¿Eliminar cliente permanentemente?"):
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("DELETE FROM Customers WHERE Id_Customer=?", (id_cliente,))
                conn.commit(); conn.close()
                self.limpiar(); self.cargar(); estado.actualizar_datos_precarga()
            except Exception: messagebox.showerror("Error", "No se puede eliminar (tiene autos registrados).")

    def limpiar(self):
        self.entry_name.delete(0, 'end'); self.entry_lastname.delete(0, 'end'); self.entry_cellphone.delete(0, 'end')

    def seleccionar(self, event):
        item = self.tree.focus()
        if item:
            v = self.tree.item(item, 'values')
            self.limpiar()
            self.entry_name.insert(0, v[1]); self.entry_lastname.insert(0, v[2]); self.entry_cellphone.insert(0, v[3])
