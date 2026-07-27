import customtkinter as ctk
from tkinter import messagebox, ttk

import estado
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT,
                     COLOR_TEXT_MAIN, COLOR_TEXT_DIM, ENTRY_STYLE, LABEL_STYLE,
                     hacer_boton_accion, mostrar_autocomplete)


class FrameFlota:
    def __init__(self, parent):
        self.build(parent)
        self.cargar()

    def build(self, parent):
        au_outer = ctk.CTkFrame(parent, fg_color="transparent")
        au_outer.pack(expand=True, fill="both", padx=32, pady=(20, 20))

        # Header tipo tarjeta: icono + título + descripción, contador en vivo a la derecha
        au_header = ctk.CTkFrame(au_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                  border_width=1, border_color=COLOR_BORDER, height=60)
        au_header.pack(fill="x", pady=(0, 16))
        au_header.pack_propagate(False)
        ctk.CTkFrame(au_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        au_header_txt = ctk.CTkFrame(au_header, fg_color="transparent")
        au_header_txt.pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(au_header_txt, text="🚗  FLOTA VEHICULAR",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(au_header_txt, text="Registro, edición y consulta de vehículos y propietarios",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        self.lbl_total = ctk.CTkLabel(au_header, text="0 VEHÍCULOS",
                                       font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT)
        self.lbl_total.pack(side="right", padx=20)

        au_body = ctk.CTkFrame(au_outer, fg_color="transparent")
        au_body.pack(expand=True, fill="both")

        f_form_au = ctk.CTkScrollableFrame(au_body, fg_color=COLOR_BG_CARD, width=380,
                                            corner_radius=6, border_width=1, border_color=COLOR_BORDER)
        f_form_au.pack(side="left", fill="y", padx=(0, 20))
        ctk.CTkFrame(f_form_au, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(f_form_au, text="FICHA TÉCNICA", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
        ctk.CTkLabel(f_form_au, text="DATOS DEL VEHÍCULO", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

        self.entry_vin = self._campo(f_form_au, "VIN — NÚMERO DE SERIE", "1HGBH41JXMN109186")
        self.entry_make = self._campo(f_form_au, "MARCA", "Nissan, Toyota, Ford...")
        self.entry_model = self._campo(f_form_au, "MODELO", "Sentra, Corolla...")
        self.entry_year = self._campo(f_form_au, "AÑO", "2024")
        self.entry_color = self._campo(f_form_au, "COLOR", "Color del vehículo")

        ctk.CTkLabel(f_form_au, text="PROPIETARIO", **LABEL_STYLE).pack(anchor="w", padx=24, pady=(10, 0))
        self.search_customer = ctk.CTkEntry(f_form_au, placeholder_text="Buscar cliente...", width=320, height=42, **ENTRY_STYLE)
        self.search_customer.pack(padx=24, pady=(2, 0))
        self.search_customer.bind("<KeyRelease>", lambda e: mostrar_autocomplete(self.search_customer, "cliente"))

        ctk.CTkFrame(f_form_au, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
        hacer_boton_accion(f_form_au, "REGISTRAR VEHÍCULO", COLOR_ACCENT, self.guardar, "＋").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_au, "ACTUALIZAR DATOS", "#1a3a1a", self.editar, "✎").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_au, "DAR DE BAJA", "#2a1010", self.eliminar, "✕").pack(fill="x", padx=24, pady=3)
        ctk.CTkButton(f_form_au, text="LIMPIAR", fg_color="transparent", border_width=1,
                      border_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM, height=36,
                      corner_radius=4, font=("Segoe UI", 11),
                      command=self.limpiar).pack(fill="x", padx=24, pady=(10, 16))

        t_frame_au = ctk.CTkFrame(au_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                   border_width=1, border_color=COLOR_BORDER)
        t_frame_au.pack(side="right", expand=True, fill="both")
        ctk.CTkFrame(t_frame_au, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        au_tabla_toolbar = ctk.CTkFrame(t_frame_au, fg_color="transparent")
        au_tabla_toolbar.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(au_tabla_toolbar, text="🔍", font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_DIM).pack(side="left", padx=(0, 8))
        self.buscar_entry = ctk.CTkEntry(au_tabla_toolbar, placeholder_text="Buscar por VIN, marca, modelo o color...",
                                          height=36, **ENTRY_STYLE)
        self.buscar_entry.pack(side="left", expand=True, fill="x")
        self.buscar_entry.bind("<KeyRelease>", lambda e: self.cargar(self.buscar_entry.get().strip()))

        self.tree = ttk.Treeview(t_frame_au, columns=("VIN","Marca","Modelo","Año","Color","Propietario","Fecha"), show="headings")
        encabezados = [("VIN","VIN",190),("Marca","MARCA",110),("Modelo","MODELO",120),
                        ("Año","AÑO",70),("Color","COLOR",100),("Propietario","PROPIETARIO",160),
                        ("Fecha","REGISTRADO",100)]
        for c, txt, w in encabezados:
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, anchor="center" if c in ("Año","Fecha") else "w")
        self.tree.pack(expand=True, fill="both", padx=2, pady=(0, 2))
        self.tree.bind("<ButtonRelease-1>", self.seleccionar)

    def _campo(self, parent, lbl, ph):
        ctk.CTkLabel(parent, text=lbl, **LABEL_STYLE).pack(anchor="w", padx=24, pady=(6, 0))
        e = ctk.CTkEntry(parent, placeholder_text=ph, width=320, height=42, **ENTRY_STYLE)
        e.pack(padx=24, pady=(2, 0))
        return e

    def cargar(self, filtro=""):
        for row in self.tree.get_children(): self.tree.delete(row)
        try:
            conn = conectar(); cursor = conn.cursor()
            base = ("SELECT Ca.VIN, Ca.Make, Ca.Model, Ca.ModelYear, Ca.Color, Ca.Id_Customer, Ca.InsertedDate, "
                    "Cu.Name, Cu.LastName FROM Carts Ca LEFT JOIN Customers Cu ON Ca.Id_Customer = Cu.Id_Customer")
            if filtro:
                like = f"%{filtro}%"
                cursor.execute(
                    base + " WHERE Ca.VIN LIKE ? OR Ca.Make LIKE ? OR Ca.Model LIKE ? OR Ca.Color LIKE ?",
                    (like, like, like, like))
            else:
                cursor.execute(base)
            filas = cursor.fetchall()
            for i, row in enumerate(filas):
                tag = 'even' if i % 2 == 0 else 'odd'
                fecha = row[6].strftime("%d/%m/%Y") if row[6] else "—"
                propietario = f"{row[7]} {row[8]}" if row[7] else "—"
                valores = [str(v) for v in row[:5]] + [propietario, fecha, str(row[5]) if row[5] is not None else ""]
                self.tree.insert("", "end", iid=row[0], values=valores, tags=(tag,))
            self.tree.tag_configure('even', background=COLOR_BG_CARD)
            self.tree.tag_configure('odd', background=COLOR_BG_CARD_ALT)
            etiqueta = "RESULTADO" if filtro else "VEHÍCULO"
            self.lbl_total.configure(text=f"{len(filas)} {etiqueta}{'S' if len(filas) != 1 else ''}")
            conn.close()
        except Exception as e: print(e)

    def guardar(self):
        texto = self.search_customer.get()
        vin_valor = self.entry_vin.get().strip()
        if not vin_valor: return messagebox.showwarning("Error", "El VIN es obligatorio.")
        if "(ID:" not in texto: return messagebox.showwarning("Error", "Selecciona un cliente de la lista.")
        try:
            id_cli = int(texto.split("(ID:")[1].replace(")", ""))
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("INSERT INTO Carts (VIN, Make, Model, ModelYear, Color, Id_Customer, InsertedDate) VALUES (?,?,?,?,?,?, GETDATE())",
                           (vin_valor, self.entry_make.get(), self.entry_model.get(), self.entry_year.get(), self.entry_color.get(), id_cli))
            conn.commit(); conn.close(); self.cargar(); estado.actualizar_datos_precarga(); self.limpiar()
            messagebox.showinfo("Éxito", "Vehículo registrado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def editar(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto.")
        vin_original = seleccion
        texto = self.search_customer.get()
        if "(ID:" not in texto: return messagebox.showwarning("Error", "Seleccione un propietario válido.")
        try:
            id_cli = int(texto.split("(ID:")[1].replace(")", ""))
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("UPDATE Carts SET VIN=?, Make=?, Model=?, ModelYear=?, Color=?, Id_Customer=? WHERE VIN=?",
                           (self.entry_vin.get().strip(), self.entry_make.get(), self.entry_model.get(), self.entry_year.get(), self.entry_color.get(), id_cli, vin_original))
            conn.commit(); conn.close(); self.cargar(); estado.actualizar_datos_precarga(); self.limpiar()
            messagebox.showinfo("Éxito", "Vehículo actualizado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un auto.")
        vin = seleccion
        if messagebox.askyesno("Confirmar", "¿Eliminar vehículo del sistema?"):
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("DELETE FROM Carts WHERE VIN=?", (vin,))
                conn.commit(); conn.close(); self.cargar(); estado.actualizar_datos_precarga(); self.limpiar()
            except Exception: messagebox.showerror("Error", "No se puede eliminar (tiene servicios vinculados).")

    def limpiar(self):
        self.entry_vin.delete(0, 'end'); self.entry_make.delete(0, 'end'); self.entry_model.delete(0, 'end')
        self.entry_year.delete(0, 'end'); self.entry_color.delete(0, 'end'); self.search_customer.delete(0, 'end')

    def seleccionar(self, event):
        seleccion = self.tree.focus()
        if seleccion:
            valores = self.tree.item(seleccion, 'values')
            self.limpiar()
            self.entry_vin.insert(0, valores[0]); self.entry_make.insert(0, valores[1])
            self.entry_model.insert(0, valores[2]); self.entry_year.insert(0, valores[3])
            self.entry_color.insert(0, valores[4])
            id_buscado = str(valores[7]) if len(valores) > 7 else ""
            for cli_id, cli_nombre in estado.lista_clientes_data:
                if str(cli_id) == id_buscado:
                    self.search_customer.insert(0, cli_nombre); break
