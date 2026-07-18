import customtkinter as ctk
from tkinter import messagebox, ttk

import estado
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT,
                     COLOR_TEXT_MAIN, COLOR_TEXT_DIM, ENTRY_STYLE, LABEL_STYLE,
                     hacer_boton_accion)


class FrameInventario:
    def __init__(self, parent):
        self.id_part_actual = None
        self.build(parent)
        self.cargar()

    def build(self, parent):
        inv_outer = ctk.CTkFrame(parent, fg_color="transparent")
        inv_outer.pack(expand=True, fill="both", padx=32, pady=(20, 20))

        # Header tipo tarjeta: icono + título + descripción, contador en vivo a la derecha
        inv_header = ctk.CTkFrame(inv_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                   border_width=1, border_color=COLOR_BORDER, height=60)
        inv_header.pack(fill="x", pady=(0, 16))
        inv_header.pack_propagate(False)
        ctk.CTkFrame(inv_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        inv_header_txt = ctk.CTkFrame(inv_header, fg_color="transparent")
        inv_header_txt.pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(inv_header_txt, text="📦  INVENTARIO",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(inv_header_txt, text="Refacciones registradas, stock disponible y precios",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        self.lbl_total = ctk.CTkLabel(inv_header, text="0 REFACCIONES",
                                       font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT)
        self.lbl_total.pack(side="right", padx=20)

        inv_body = ctk.CTkFrame(inv_outer, fg_color="transparent")
        inv_body.pack(expand=True, fill="both")

        f_form_inv = ctk.CTkScrollableFrame(inv_body, fg_color=COLOR_BG_CARD, width=380,
                                             corner_radius=6, border_width=1, border_color=COLOR_BORDER)
        f_form_inv.pack(side="left", fill="y", padx=(0, 20))
        ctk.CTkFrame(f_form_inv, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(f_form_inv, text="FICHA DE REFACCIÓN", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
        ctk.CTkLabel(f_form_inv, text="DATOS DE LA PIEZA", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

        self.entry_partname = self._campo(f_form_inv, "NOMBRE DE LA REFACCIÓN", "Ej: Balata delantera")
        self.entry_stock = self._campo(f_form_inv, "STOCK DISPONIBLE", "0")
        self.entry_price = self._campo(f_form_inv, "PRECIO ($)", "0.00")

        self.lbl_sel = ctk.CTkLabel(f_form_inv, text="Ninguna refacción seleccionada",
                                     font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM,
                                     wraplength=320, justify="left")
        self.lbl_sel.pack(anchor="w", padx=24, pady=(8, 0))

        ctk.CTkFrame(f_form_inv, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
        hacer_boton_accion(f_form_inv, "REGISTRAR REFACCIÓN", COLOR_ACCENT, self.guardar, "＋").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_inv, "ACTUALIZAR DATOS", "#1a3a1a", self.editar, "✎").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_inv, "ELIMINAR REFACCIÓN", "#2a1010", self.eliminar, "✕").pack(fill="x", padx=24, pady=3)

        t_frame_inv = ctk.CTkFrame(inv_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                    border_width=1, border_color=COLOR_BORDER)
        t_frame_inv.pack(side="right", expand=True, fill="both")
        ctk.CTkFrame(t_frame_inv, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        inv_tabla_toolbar = ctk.CTkFrame(t_frame_inv, fg_color="transparent")
        inv_tabla_toolbar.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(inv_tabla_toolbar, text="🔍", font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_DIM).pack(side="left", padx=(0, 8))
        self.buscar_entry = ctk.CTkEntry(inv_tabla_toolbar, placeholder_text="Buscar por nombre de refacción...",
                                          height=36, **ENTRY_STYLE)
        self.buscar_entry.pack(side="left", expand=True, fill="x")
        self.buscar_entry.bind("<KeyRelease>", lambda e: self.cargar(self.buscar_entry.get().strip()))

        self.tree = ttk.Treeview(t_frame_inv, columns=("Refacción", "Stock", "Precio"), show="headings")
        encabezados = [("Refacción", "REFACCIÓN", 260),
                       ("Stock", "STOCK", 100), ("Precio", "PRECIO", 120)]
        for c, txt, w in encabezados:
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, anchor="center" if c in ("Stock", "Precio") else "w")
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
            if filtro:
                cursor.execute(
                    "SELECT Id_Part, PartName, Stock, Price FROM Inventory WHERE PartName LIKE ? ORDER BY PartName",
                    (f"%{filtro}%",))
            else:
                cursor.execute("SELECT Id_Part, PartName, Stock, Price FROM Inventory ORDER BY PartName")
            filas = cursor.fetchall()
            for i, row in enumerate(filas):
                tag = 'even' if i % 2 == 0 else 'odd'
                precio = f"{row[3]:,.2f}"
                self.tree.insert("", "end", iid=str(row[0]), values=(row[1], row[2], precio), tags=(tag,))
            self.tree.tag_configure('even', background=COLOR_BG_CARD)
            self.tree.tag_configure('odd', background=COLOR_BG_CARD_ALT)
            etiqueta = "RESULTADO" if filtro else "REFACCIÓN"
            self.lbl_total.configure(text=f"{len(filas)} {etiqueta}{'S' if len(filas) != 1 else ''}")
            conn.close()
        except Exception as e: print(e)

    def _validar_datos(self):
        nombre = self.entry_partname.get().strip()
        if not nombre:
            return None, "El nombre de la refacción es obligatorio."
        try:
            stock = int(self.entry_stock.get().strip())
            if stock < 0: raise ValueError
        except ValueError:
            return None, "El stock debe ser un número entero (0 o mayor)."
        precio_txt = self.entry_price.get().strip().replace("$", "").replace(",", "")
        try:
            precio = float(precio_txt)
        except ValueError:
            return None, "El precio debe ser un número válido, ej: 250.00."
        return (nombre, stock, precio), None

    def guardar(self):
        datos, error = self._validar_datos()
        if error: return messagebox.showwarning("Error", error)
        nombre, stock, precio = datos
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("INSERT INTO Inventory (PartName, Stock, Price) VALUES (?,?,?)", (nombre, stock, precio))
            conn.commit(); conn.close()
            estado.actualizar_datos_precarga()
            self.cargar(); self.limpiar()
            messagebox.showinfo("Éxito", "Refacción registrada.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def editar(self):
        if not self.id_part_actual:
            return messagebox.showwarning("Advertencia", "Selecciona una refacción de la tabla.")
        datos, error = self._validar_datos()
        if error: return messagebox.showwarning("Error", error)
        nombre, stock, precio = datos
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("UPDATE Inventory SET PartName=?, Stock=?, Price=? WHERE Id_Part=?",
                           (nombre, stock, precio, self.id_part_actual))
            conn.commit(); conn.close()
            estado.actualizar_datos_precarga()
            self.cargar(); self.limpiar()
            messagebox.showinfo("Éxito", "Refacción actualizada.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar(self):
        if not self.id_part_actual:
            return messagebox.showwarning("Advertencia", "Selecciona una refacción de la tabla.")
        if messagebox.askyesno("Confirmar", "¿Eliminar esta refacción del inventario?"):
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("DELETE FROM Inventory WHERE Id_Part=?", (self.id_part_actual,))
                conn.commit(); conn.close()
                estado.actualizar_datos_precarga()
                self.cargar(); self.limpiar()
            except Exception:
                messagebox.showerror("Error", "No se puede eliminar (la refacción está usada en servicios registrados).")

    def limpiar(self):
        self.entry_partname.delete(0, 'end'); self.entry_stock.delete(0, 'end'); self.entry_price.delete(0, 'end')
        self.id_part_actual = None
        self.lbl_sel.configure(text="Ninguna refacción seleccionada")

    def seleccionar(self, event):
        seleccion = self.tree.focus()
        if seleccion:
            valores = self.tree.item(seleccion, 'values')
            self.entry_partname.delete(0, 'end'); self.entry_stock.delete(0, 'end'); self.entry_price.delete(0, 'end')
            self.id_part_actual = int(seleccion)
            self.entry_partname.insert(0, valores[0])
            self.entry_stock.insert(0, str(valores[1]))
            self.entry_price.insert(0, str(valores[2]).replace(',', ''))
            self.lbl_sel.configure(text=f"Editando refacción #{self.id_part_actual}")
