import customtkinter as ctk
from tkinter import messagebox, ttk

import estado
import reportes
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT, COLOR_ACCENT_DIM,
                     COLOR_ACCENT2, COLOR_SUCCESS, COLOR_TEXT_MAIN, COLOR_TEXT_DIM, ENTRY_STYLE, LABEL_STYLE,
                     hacer_boton_accion, mostrar_autocomplete)


class FrameOrdenes:
    def __init__(self, parent):
        self.orden_actual = None
        self.id_part_seleccionado = None
        self.inventario_map = {}
        self.servicios_pendientes = []
        self.cantidad_servicio = 1
        self.precio_unitario_actual = None
        self.servicio_editando = None
        self.build(parent)
        self.cargar_ordenes()
        self._cargar_inventario_combo()

    def build(self, parent):
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(expand=True, fill="both", padx=32, pady=(20, 20))

        # Header tipo tarjeta: icono + título + descripción, contador en vivo a la derecha
        header = ctk.CTkFrame(outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                               border_width=1, border_color=COLOR_BORDER, height=60)
        header.pack(fill="x", pady=(0, 16))
        header.pack_propagate(False)
        ctk.CTkFrame(header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        header_txt = ctk.CTkFrame(header, fg_color="transparent")
        header_txt.pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(header_txt, text="🔧  ÓRDENES DE SERVICIO",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(header_txt, text="Crea una orden por cliente y agrégale los servicios que necesite",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        self.lbl_total = ctk.CTkLabel(header, text="0 ÓRDENES",
                                       font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT)
        self.lbl_total.pack(side="right", padx=20)

        self.tabs = ctk.CTkTabview(outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                    border_width=1, border_color=COLOR_BORDER,
                                    segmented_button_selected_color=COLOR_ACCENT,
                                    segmented_button_selected_hover_color=COLOR_ACCENT_DIM,
                                    segmented_button_unselected_color=COLOR_BG_CARD_ALT,
                                    text_color=COLOR_TEXT_MAIN)
        self.tabs.pack(expand=True, fill="both")
        tab_ordenes = self.tabs.add("📋  ÓRDENES")
        tab_servicios = self.tabs.add("🔧  SERVICIOS DE LA ORDEN")

        self._build_tab_ordenes(tab_ordenes)
        self._build_tab_servicios(tab_servicios)

    # ── PESTAÑA 1: ÓRDENES ───────────────────────────────────────
    def _build_tab_ordenes(self, tab):
        body = ctk.CTkFrame(tab, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=4, pady=4)

        f_form = ctk.CTkScrollableFrame(body, fg_color=COLOR_BG_CARD_ALT, width=340,
                                         corner_radius=6, border_width=1, border_color=COLOR_BORDER)
        f_form.pack(side="left", fill="y", padx=(0, 16))
        ctk.CTkFrame(f_form, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(f_form, text="NUEVA ORDEN", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
        ctk.CTkLabel(f_form, text="ORDEN GENERAL", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

        ctk.CTkLabel(f_form, text="CLIENTE", **LABEL_STYLE).pack(anchor="w", padx=20, pady=(6, 0))
        self.search_customer = ctk.CTkEntry(f_form, placeholder_text="Buscar cliente...", width=280, height=42, **ENTRY_STYLE)
        self.search_customer.pack(padx=20, pady=(2, 0))
        self.search_customer.bind("<KeyRelease>", lambda e: mostrar_autocomplete(self.search_customer, "cliente"))

        ctk.CTkLabel(f_form, text="VIN DEL VEHÍCULO (OPCIONAL)", **LABEL_STYLE).pack(anchor="w", padx=20, pady=(10, 0))
        self.search_vin = ctk.CTkEntry(f_form, placeholder_text="Escribir o buscar VIN...", width=280, height=42, **ENTRY_STYLE)
        self.search_vin.pack(padx=20, pady=(2, 0))
        self.search_vin.bind("<KeyRelease>", lambda e: mostrar_autocomplete(self.search_vin, "auto"))

        ctk.CTkFrame(f_form, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=20, pady=14)
        hacer_boton_accion(f_form, "CREAR ORDEN", COLOR_ACCENT, self.crear_orden, "＋").pack(fill="x", padx=20, pady=3)
        hacer_boton_accion(f_form, "ELIMINAR ORDEN", "#2a1010", self.eliminar_orden, "✕").pack(fill="x", padx=20, pady=3)
        ctk.CTkButton(f_form, text="⬇  EXPORTAR PDF", fg_color="transparent",
                      border_width=1, border_color=COLOR_ACCENT2, text_color=COLOR_ACCENT2,
                      height=42, corner_radius=4, font=("Segoe UI", 12, "bold"),
                      command=self.pedir_ticket_pdf).pack(fill="x", padx=20, pady=3)
        ctk.CTkButton(f_form, text="LIMPIAR", fg_color="transparent", border_width=1,
                      border_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM, height=36,
                      corner_radius=4, font=("Segoe UI", 11),
                      command=self.limpiar_form_orden).pack(fill="x", padx=20, pady=(10, 3))

        ctk.CTkFrame(f_form, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=20, pady=14)
        ctk.CTkLabel(f_form, text="ORDEN ACTIVA", **LABEL_STYLE).pack(anchor="w", padx=20)
        self.lbl_orden_activa = ctk.CTkLabel(f_form, text="Ninguna orden seleccionada",
                                              font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN,
                                              wraplength=280, justify="left")
        self.lbl_orden_activa.pack(anchor="w", padx=20, pady=(2, 12))

        t_frame = ctk.CTkFrame(body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                border_width=1, border_color=COLOR_BORDER)
        t_frame.pack(side="right", expand=True, fill="both")
        ctk.CTkFrame(t_frame, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        toolbar = ctk.CTkFrame(t_frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(toolbar, text="🔍", font=("Segoe UI", 13), text_color=COLOR_TEXT_DIM).pack(side="left", padx=(0, 8))
        self.buscar_orden_entry = ctk.CTkEntry(toolbar, placeholder_text="Buscar por cliente o VIN...",
                                                height=36, **ENTRY_STYLE)
        self.buscar_orden_entry.pack(side="left", expand=True, fill="x")
        self.buscar_orden_entry.bind("<KeyRelease>", lambda e: self.cargar_ordenes(self.buscar_orden_entry.get().strip()))

        self.tree_ordenes = ttk.Treeview(t_frame, columns=("Cliente", "VIN", "Fecha", "Total"), show="headings")
        encabezados = [("Cliente", "CLIENTE", 200), ("VIN", "VIN", 170),
                       ("Fecha", "FECHA", 100), ("Total", "TOTAL", 110)]
        for c, txt, w in encabezados:
            self.tree_ordenes.heading(c, text=txt)
            self.tree_ordenes.column(c, width=w, anchor="center" if c in ("Fecha", "Total") else "w")
        self.tree_ordenes.pack(expand=True, fill="both", padx=2, pady=(0, 2))
        self.tree_ordenes.bind("<ButtonRelease-1>", self.seleccionar_orden)

    # ── PESTAÑA 2: SERVICIOS DE LA ORDEN ─────────────────────────
    def _build_tab_servicios(self, tab):
        body = ctk.CTkFrame(tab, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=4, pady=4)

        f_form = ctk.CTkScrollableFrame(body, fg_color=COLOR_BG_CARD_ALT, width=340,
                                         corner_radius=6, border_width=1, border_color=COLOR_BORDER)
        f_form.pack(side="left", fill="y", padx=(0, 16))
        ctk.CTkFrame(f_form, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(f_form, text="AGREGAR SERVICIO", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
        self.lbl_orden_activa_2 = ctk.CTkLabel(f_form, text="Selecciona una orden en la pestaña ÓRDENES",
                                                font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN,
                                                wraplength=280, justify="left")
        self.lbl_orden_activa_2.pack(pady=(2, 10), padx=20)

        ctk.CTkLabel(f_form, text="REFACCIÓN", **LABEL_STYLE).pack(anchor="w", padx=20, pady=(6, 0))
        self.entry_parte = ctk.CTkEntry(f_form, placeholder_text="Escribe el nombre de la refacción...",
                                         width=280, height=42, **ENTRY_STYLE)
        self.entry_parte.pack(padx=20, pady=(2, 0))
        self.entry_parte.bind("<KeyRelease>", self.al_escribir_parte)

        f_cantidad = ctk.CTkFrame(f_form, fg_color="transparent")
        f_cantidad.pack(padx=20, pady=(6, 0), fill="x")
        ctk.CTkLabel(f_cantidad, text="CANTIDAD", **LABEL_STYLE).pack(anchor="w")
        f_cantidad_ctrl = ctk.CTkFrame(f_cantidad, fg_color="transparent")
        f_cantidad_ctrl.pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(f_cantidad_ctrl, text="－", width=36, height=36, corner_radius=4,
                      fg_color=COLOR_BG_CARD_ALT, hover_color=COLOR_ACCENT_DIM,
                      text_color=COLOR_TEXT_MAIN, font=("Segoe UI", 14, "bold"),
                      command=self.decrementar_cantidad).pack(side="left")
        self.lbl_cantidad = ctk.CTkLabel(f_cantidad_ctrl, text="1", width=50, height=36,
                                          font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN)
        self.lbl_cantidad.pack(side="left", padx=4)
        ctk.CTkButton(f_cantidad_ctrl, text="＋", width=36, height=36, corner_radius=4,
                      fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM,
                      text_color=COLOR_TEXT_MAIN, font=("Segoe UI", 14, "bold"),
                      command=self.incrementar_cantidad).pack(side="left")

        self.entry_duration = self._campo(f_form, "TIEMPO ESTIMADO", "Ej: 3 Horas")
        self.entry_price = self._campo(f_form, "COSTO ($)", "0.00")
        self.entry_worker = self._campo(f_form, "MECÁNICO ASIGNADO", "Nombre del mecánico")

        self.lbl_editando_servicio = ctk.CTkLabel(f_form, text="", font=("Segoe UI", 10, "bold"),
                                                   text_color=COLOR_ACCENT2, wraplength=280, justify="left")
        self.lbl_editando_servicio.pack(anchor="w", padx=20, pady=(4, 0))

        ctk.CTkFrame(f_form, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=20, pady=14)
        hacer_boton_accion(f_form, "AGREGAR A LA LISTA", COLOR_ACCENT, self.agregar_servicio, "＋").pack(fill="x", padx=20, pady=3)
        hacer_boton_accion(f_form, "GUARDAR CAMBIOS", "#1a3a1a", self.guardar_cambios_servicio, "✎").pack(fill="x", padx=20, pady=3)
        hacer_boton_accion(f_form, "QUITAR SELECCIONADO", "#2a1010", self.eliminar_servicio, "✕").pack(fill="x", padx=20, pady=3)
        ctk.CTkButton(f_form, text="LIMPIAR", fg_color="transparent", border_width=1,
                      border_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM, height=36,
                      corner_radius=4, font=("Segoe UI", 11),
                      command=self._limpiar_form_servicio).pack(fill="x", padx=20, pady=(3, 0))

        ctk.CTkFrame(f_form, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=20, pady=14)
        self.lbl_pendientes = ctk.CTkLabel(f_form, text="Sin servicios pendientes por guardar",
                                            font=("Segoe UI", 11, "bold"), text_color=COLOR_ACCENT2,
                                            wraplength=280, justify="left")
        self.lbl_pendientes.pack(padx=20, pady=(0, 8))
        hacer_boton_accion(f_form, "CONFIRMAR Y GUARDAR EN LA ORDEN", COLOR_SUCCESS,
                            self.confirmar_servicios, "✓").pack(fill="x", padx=20, pady=3)

        t_frame = ctk.CTkFrame(body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                border_width=1, border_color=COLOR_BORDER)
        t_frame.pack(side="right", expand=True, fill="both")
        ctk.CTkFrame(t_frame, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(t_frame, text="SERVICIOS DE LA ORDEN", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=16, pady=(12, 6))

        self.tree_servicios = ttk.Treeview(t_frame, columns=("Refacción", "Duración", "Precio", "Mecánico", "Fecha"),
                                            show="headings")
        encabezados = [("Refacción", "REFACCIÓN", 180), ("Duración", "DURACIÓN", 110),
                       ("Precio", "PRECIO", 100), ("Mecánico", "MECÁNICO", 150), ("Fecha", "FECHA", 100)]
        for c, txt, w in encabezados:
            self.tree_servicios.heading(c, text=txt)
            self.tree_servicios.column(c, width=w, anchor="center" if c in ("Duración", "Precio", "Fecha") else "w")
        self.tree_servicios.pack(expand=True, fill="both", padx=2, pady=(0, 2))
        self.tree_servicios.bind("<ButtonRelease-1>", self.seleccionar_servicio)

    def _campo(self, parent, lbl, ph):
        ctk.CTkLabel(parent, text=lbl, **LABEL_STYLE).pack(anchor="w", padx=20, pady=(6, 0))
        e = ctk.CTkEntry(parent, placeholder_text=ph, width=280, height=42, **ENTRY_STYLE)
        e.pack(padx=20, pady=(2, 0))
        return e

    # ── ÓRDENES: datos ───────────────────────────────────────────
    def cargar_ordenes(self, filtro=""):
        for row in self.tree_ordenes.get_children(): self.tree_ordenes.delete(row)
        try:
            conn = conectar(); cursor = conn.cursor()
            base = ("SELECT O.Id_Order, Cu.Name, Cu.LastName, O.VIN, O.OrderDate, O.TotalAmount "
                     "FROM Orders O JOIN Customers Cu ON O.Id_Customer = Cu.Id_Customer")
            if filtro:
                like = f"%{filtro}%"
                cursor.execute(base + " WHERE Cu.Name LIKE ? OR Cu.LastName LIKE ? OR O.VIN LIKE ?",
                               (like, like, like))
            else:
                cursor.execute(base)
            filas = cursor.fetchall()
            for i, row in enumerate(filas):
                tag = 'even' if i % 2 == 0 else 'odd'
                fecha = row[4].strftime("%d/%m/%Y") if row[4] else "—"
                cliente = f"{row[1]} {row[2]}"
                vin = row[3] or "—"
                total = f"{row[5]:,.2f}" if row[5] is not None else "0.00"
                self.tree_ordenes.insert("", "end", iid=str(row[0]), values=(cliente, vin, fecha, total), tags=(tag,))
            self.tree_ordenes.tag_configure('even', background=COLOR_BG_CARD)
            self.tree_ordenes.tag_configure('odd', background=COLOR_BG_CARD_ALT)
            etiqueta = "RESULTADO" if filtro else "ORDEN"
            self.lbl_total.configure(text=f"{len(filas)} {etiqueta}{'S' if len(filas) != 1 else ''}")
            conn.close()
        except Exception as e: print(e)

    def limpiar_form_orden(self):
        self.search_customer.delete(0, 'end')
        self.search_vin.delete(0, 'end')

    def _vin_existe(self, vin):
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Carts WHERE VIN = ?", (vin,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe

    def _confirmar_descarte_pendientes(self):
        """Si hay servicios agregados a la lista pero aún no guardados,
        pide confirmación antes de cambiar de orden (se perderían)."""
        if not self.servicios_pendientes:
            return True
        return messagebox.askyesno(
            "Servicios sin guardar",
            f"Tienes {len(self.servicios_pendientes)} servicio(s) agregados a la lista que "
            "todavía no se han guardado en la orden actual.\n"
            "Si cambias de orden se perderán. ¿Deseas continuar?")

    def crear_orden(self):
        texto = self.search_customer.get()
        if "(ID:" not in texto: return messagebox.showwarning("Error", "Selecciona un cliente de la lista.")
        if not self._confirmar_descarte_pendientes(): return
        vin = self.search_vin.get().strip() or None
        if vin and not self._vin_existe(vin):
            return messagebox.showwarning(
                "VIN no encontrado",
                f"El VIN '{vin}' no está registrado en la flota.\n"
                "Regístralo primero en la pestaña FLOTA o deja el campo vacío.")
        try:
            id_cli = int(texto.split("(ID:")[1].replace(")", ""))
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("INSERT INTO Orders (Id_Customer, VIN) OUTPUT INSERTED.Id_Order VALUES (?,?)",
                           (id_cli, vin))
            nuevo_id = int(cursor.fetchone()[0])
            conn.commit(); conn.close()
            self.cargar_ordenes()
            self._activar_orden(nuevo_id)
            self.search_customer.delete(0, 'end'); self.search_vin.delete(0, 'end')
            messagebox.showinfo("Éxito", f"Orden #{nuevo_id} creada. Ve a la pestaña SERVICIOS para agregarle servicios.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar_orden(self):
        if not self.orden_actual:
            return messagebox.showwarning("Advertencia", "Selecciona una orden de la tabla.")
        respuesta = messagebox.askyesnocancel(
            "Confirmar eliminación",
            f"¿Eliminar la orden #{self.orden_actual} y todos sus servicios?\n\n"
            "¿Quieres que las refacciones usadas regresen al inventario?\n\n"
            "Sí = eliminar y devolver refacciones al stock.\n"
            "No = eliminar sin devolver refacciones.\n"
            "Cancelar = no eliminar la orden.")
        if respuesta is None:
            return
        try:
            conn = conectar(); cursor = conn.cursor()
            if respuesta:
                cursor.execute("SELECT Id_Part FROM Services WHERE Id_Order = ? AND Id_Part IS NOT NULL", (self.orden_actual,))
                partes = [r[0] for r in cursor.fetchall()]
                for id_part in partes:
                    cursor.execute("UPDATE Inventory SET Stock = Stock + 1 WHERE Id_Part = ?", (id_part,))
            cursor.execute("DELETE FROM Services WHERE Id_Order = ?", (self.orden_actual,))
            cursor.execute("DELETE FROM Orders WHERE Id_Order = ?", (self.orden_actual,))
            conn.commit(); conn.close()
            estado.actualizar_datos_precarga()
            self.orden_actual = None
            self.servicios_pendientes = []
            self.lbl_orden_activa.configure(text="Ninguna orden seleccionada")
            self.lbl_orden_activa_2.configure(text="Selecciona una orden en la pestaña ÓRDENES")
            for row in self.tree_servicios.get_children(): self.tree_servicios.delete(row)
            self.cargar_ordenes()
            messagebox.showinfo("Éxito", "Orden eliminada.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def seleccionar_orden(self, event):
        seleccion = self.tree_ordenes.focus()
        if seleccion:
            id_order = int(seleccion)
            if id_order == self.orden_actual: return
            if not self._confirmar_descarte_pendientes(): return
            self._activar_orden(id_order)

    def _activar_orden(self, id_order):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("""SELECT O.Id_Order, Cu.Name, Cu.LastName, O.VIN, O.TotalAmount
                              FROM Orders O JOIN Customers Cu ON O.Id_Customer = Cu.Id_Customer
                              WHERE O.Id_Order = ?""", (id_order,))
            row = cursor.fetchone(); conn.close()
        except Exception as e:
            return messagebox.showerror("Error", str(e))
        if not row:
            return messagebox.showwarning("Error", "La orden ya no existe.")
        self.servicios_pendientes = []
        self.orden_actual = row[0]
        vin_txt = row[3] or "sin vehículo asociado"
        total = row[4] if row[4] is not None else 0
        texto = f"Orden #{row[0]}\n{row[1]} {row[2]}\nVIN: {vin_txt}\nTotal: ${total:,.2f}"
        self.lbl_orden_activa.configure(text=texto)
        self.lbl_orden_activa_2.configure(text=texto)
        self._cargar_inventario_combo()
        self.cargar_servicios()

    # ── SERVICIOS: datos ─────────────────────────────────────────
    def _cargar_inventario_combo(self):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("SELECT Id_Part, PartName, Stock, Price, Duration FROM Inventory "
                            "WHERE IsDeleted = 0 ORDER BY PartName")
            filas = cursor.fetchall(); conn.close()
        except Exception as e:
            print(e); filas = []
        self.inventario_map = {r[1].strip().lower(): (r[0], float(r[3]), r[4]) for r in filas}
        self.entry_parte.delete(0, 'end')
        self.id_part_seleccionado = None

    def al_escribir_parte(self, event):
        mostrar_autocomplete(self.entry_parte, "parte")
        self._set_cantidad(1)
        self._sincronizar_parte(autofill_precio=True)

    def _set_cantidad(self, valor):
        self.cantidad_servicio = valor
        self.lbl_cantidad.configure(text=str(valor))

    def _actualizar_costo_mostrado(self):
        """Refleja en el campo COSTO el precio unitario de inventario
        multiplicado por la cantidad seleccionada."""
        if self.precio_unitario_actual is None:
            return
        total = self.precio_unitario_actual * self.cantidad_servicio
        self.entry_price.delete(0, 'end')
        self.entry_price.insert(0, f"{total:.2f}")

    def _stock_disponible_restante(self):
        """Stock disponible de la refacción seleccionada, descontando lo que
        ya está en la lista de pendientes (sin contar la cantidad que se está
        por agregar)."""
        if not self.id_part_seleccionado:
            return 0
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("SELECT Stock FROM Inventory WHERE Id_Part = ?", (self.id_part_seleccionado,))
            fila = cursor.fetchone(); conn.close()
        except Exception:
            fila = None
        stock_actual = fila[0] if fila else 0
        usado_pendiente = sum(1 for s in self.servicios_pendientes if s["id_part"] == self.id_part_seleccionado)
        return stock_actual - usado_pendiente

    def incrementar_cantidad(self):
        self._sincronizar_parte(autofill_precio=False)
        if not self.id_part_seleccionado:
            return messagebox.showwarning(
                "Error", "Escribe primero el nombre de una refacción registrada en INVENTARIO.")
        disponible = self._stock_disponible_restante()
        if self.cantidad_servicio >= disponible:
            return messagebox.showwarning(
                "Sin stock",
                f"No hay más stock disponible (disponible: {disponible}).")
        self._set_cantidad(self.cantidad_servicio + 1)
        self._actualizar_costo_mostrado()

    def decrementar_cantidad(self):
        if self.cantidad_servicio > 1:
            self._set_cantidad(self.cantidad_servicio - 1)
            self._actualizar_costo_mostrado()

    def _sincronizar_parte(self, autofill_precio=False):
        """Busca coincidencia exacta (sin importar mayúsculas) entre lo tecleado
        y una refacción registrada en Inventory. Por ahora es texto libre —
        cuando haya muchas refacciones registradas se puede volver a un combo."""
        texto = self.entry_parte.get().strip().lower()
        datos = self.inventario_map.get(texto)
        if datos:
            id_part, precio, duracion = datos
            self.id_part_seleccionado = id_part
            self.precio_unitario_actual = precio
            if autofill_precio:
                self._actualizar_costo_mostrado()
                # La duración es el tiempo estándar del trabajo completo (p.ej.
                # "cambiar el juego de bujías"), no depende de la cantidad de
                # unidades, así que no se multiplica por self.cantidad_servicio.
                self.entry_duration.delete(0, 'end')
                if duracion:
                    self.entry_duration.insert(0, duracion)
        else:
            self.id_part_seleccionado = None
            self.precio_unitario_actual = None

    def cargar_servicios(self):
        for row in self.tree_servicios.get_children(): self.tree_servicios.delete(row)
        if self.orden_actual:
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("""SELECT S.Id_Service, COALESCE(I.PartName, 'Sin refacción'), S.Duration,
                                         S.Price, S.Worker, S.InsertedDate
                                  FROM Services S
                                  LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                                  WHERE S.Id_Order = ?
                                  ORDER BY S.Id_Service""", (self.orden_actual,))
                filas = cursor.fetchall(); conn.close()
                for i, row in enumerate(filas):
                    tag = 'even' if i % 2 == 0 else 'odd'
                    fecha = row[5].strftime("%d/%m/%Y") if row[5] else "—"
                    precio = f"{row[3]:,.2f}" if row[3] is not None else "0.00"
                    self.tree_servicios.insert("", "end", iid=f"db-{row[0]}",
                                                values=(row[1], row[2], precio, row[4], fecha), tags=(tag,))
                self.tree_servicios.tag_configure('even', background=COLOR_BG_CARD)
                self.tree_servicios.tag_configure('odd', background=COLOR_BG_CARD_ALT)
            except Exception as e: print(e)

        for i, s in enumerate(self.servicios_pendientes):
            precio = f"{s['price']:,.2f}" if s['price'] is not None else "0.00"
            self.tree_servicios.insert("", "end", iid=f"pend-{i}",
                                        values=(s["part_name"], s["duration"], precio, s["worker"], "Sin guardar"),
                                        tags=('pending',))
        self.tree_servicios.tag_configure('pending', background="#3a2a00", foreground=COLOR_ACCENT2)

        if self.servicios_pendientes:
            total_pend = sum((s['price'] or 0) for s in self.servicios_pendientes)
            self.lbl_pendientes.configure(
                text=f"{len(self.servicios_pendientes)} servicio(s) sin guardar — subtotal ${total_pend:,.2f}")
        else:
            self.lbl_pendientes.configure(text="Sin servicios pendientes por guardar")

    def _limpiar_precio(self, texto):
        """Acepta '' (sin costo aún) y formatos con coma de miles y/o punto
        decimal en cualquier combinación. Devuelve (precio, error)."""
        texto = texto.strip().replace("$", "").replace(" ", "")
        if not texto:
            return None, None
        limpio = texto
        if "," in limpio and "." in limpio:
            if limpio.rfind(",") > limpio.rfind("."):
                limpio = limpio.replace(".", "").replace(",", ".")
            else:
                limpio = limpio.replace(",", "")
        elif "," in limpio:
            partes = limpio.split(",")
            if len(partes[-1]) == 3 and all(len(p) <= 3 for p in partes[1:]):
                limpio = limpio.replace(",", "")
            else:
                limpio = limpio.replace(",", ".")
        try:
            return float(limpio), None
        except ValueError:
            return None, "El costo debe ser un número válido, ej: 12,000.00 o 12000.50."

    def agregar_servicio(self):
        """Agrega el servicio a una lista local en memoria (no se guarda en la
        BD todavía). El usuario puede seguir agregando más y solo hasta que
        presione CONFIRMAR Y GUARDAR se insertan todos de una vez."""
        if not self.orden_actual:
            return messagebox.showwarning("Advertencia", "Primero crea o selecciona una orden en la pestaña ÓRDENES.")
        self._sincronizar_parte(autofill_precio=False)
        if not self.id_part_seleccionado:
            return messagebox.showwarning(
                "Error", "Esa refacción no está registrada en INVENTARIO.\n"
                "Escribe el nombre exacto de una refacción existente o regístrala primero en la pestaña INVENTARIO.")
        precio_total, error_precio = self._limpiar_precio(self.entry_price.get())
        if error_precio: return messagebox.showwarning("Error", error_precio)
        worker = self.entry_worker.get().strip()
        if not worker: return messagebox.showwarning("Error", "El mecánico asignado es obligatorio.")
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("SELECT PartName, Stock FROM Inventory WHERE Id_Part = ?", (self.id_part_seleccionado,))
            fila = cursor.fetchone()
            conn.close()
        except Exception as e:
            return messagebox.showerror("Error", str(e))
        if not fila:
            return messagebox.showwarning("Error", "La refacción ya no existe en inventario.")
        part_name, stock_actual = fila
        cantidad = max(1, self.cantidad_servicio)
        usado_pendiente = sum(1 for s in self.servicios_pendientes if s["id_part"] == self.id_part_seleccionado)
        if usado_pendiente + cantidad > stock_actual:
            return messagebox.showwarning(
                "Sin stock",
                f"No hay suficiente stock de '{part_name}' para agregar {cantidad} unidad(es) "
                f"(disponible: {stock_actual}, ya tienes {usado_pendiente} en la lista sin guardar).")
        # El campo COSTO muestra el total (precio unitario x cantidad); cada
        # fila guardada en Services representa 1 unidad, así que se reparte
        # el total entre la cantidad para guardar el costo por unidad.
        precio_unitario_guardar = round(precio_total / cantidad, 2) if precio_total is not None else None
        for _ in range(cantidad):
            self.servicios_pendientes.append({
                "id_part": self.id_part_seleccionado, "part_name": part_name,
                "duration": self.entry_duration.get(), "price": precio_unitario_guardar, "worker": worker,
            })
        self.cargar_servicios()
        self._limpiar_form_servicio()

    def confirmar_servicios(self):
        """Inserta en la BD todos los servicios agregados a la lista pendiente
        de la orden activa, descontando el stock de cada refacción."""
        if not self.orden_actual:
            return messagebox.showwarning("Advertencia", "No hay una orden activa.")
        if not self.servicios_pendientes:
            return messagebox.showwarning("Advertencia", "No hay servicios pendientes por guardar. Agrega al menos uno a la lista.")
        try:
            conn = conectar(); cursor = conn.cursor()
            total_agregado = 0
            for s in self.servicios_pendientes:
                cursor.execute("SELECT Stock FROM Inventory WHERE Id_Part = ?", (s["id_part"],))
                fila = cursor.fetchone()
                if not fila or fila[0] <= 0:
                    conn.rollback(); conn.close()
                    return messagebox.showerror(
                        "Sin stock",
                        f"'{s['part_name']}' se quedó sin stock antes de guardar la orden.\n"
                        "Quítalo de la lista y vuelve a intentarlo.")
                cursor.execute("""INSERT INTO Services (Duration, Price, Worker, Id_Order, Id_Part)
                                  VALUES (?,?,?,?,?)""",
                               (s["duration"], s["price"], s["worker"], self.orden_actual, s["id_part"]))
                cursor.execute("UPDATE Inventory SET Stock = Stock - 1 WHERE Id_Part = ? AND Stock > 0",
                               (s["id_part"],))
                total_agregado += s["price"] or 0
            cursor.execute("UPDATE Orders SET TotalAmount = TotalAmount + ? WHERE Id_Order = ?",
                           (total_agregado, self.orden_actual))
            conn.commit(); conn.close()
            n = len(self.servicios_pendientes)
            self.servicios_pendientes = []
            estado.actualizar_datos_precarga()
            self._activar_orden(self.orden_actual)
            self.cargar_ordenes()
            messagebox.showinfo("Éxito", f"{n} servicio(s) guardado(s) en la orden.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar_servicio(self):
        seleccion = self.tree_servicios.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Selecciona un servicio de la tabla.")
        if seleccion.startswith("pend-"):
            idx = int(seleccion.split("-", 1)[1])
            if 0 <= idx < len(self.servicios_pendientes):
                del self.servicios_pendientes[idx]
                self.cargar_servicios()
            return
        if not messagebox.askyesno(
                "Confirmar", "¿Eliminar este servicio ya guardado de la orden?\nSe devolverá 1 unidad al stock de la refacción."):
            return
        id_service = int(seleccion.split("-", 1)[1])
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("SELECT Id_Part, Price FROM Services WHERE Id_Service = ?", (id_service,))
            fila = cursor.fetchone()
            if fila:
                id_part, precio = fila
                if id_part:
                    cursor.execute("UPDATE Inventory SET Stock = Stock + 1 WHERE Id_Part = ?", (id_part,))
                cursor.execute("UPDATE Orders SET TotalAmount = TotalAmount - ? WHERE Id_Order = ?",
                               (precio or 0, self.orden_actual))
            cursor.execute("DELETE FROM Services WHERE Id_Service = ?", (id_service,))
            conn.commit(); conn.close()
            estado.actualizar_datos_precarga()
            self._refrescar_orden_activa()
            self.cargar_ordenes()
            self._limpiar_form_servicio()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _limpiar_form_servicio(self):
        self.entry_parte.delete(0, 'end')
        self.entry_duration.delete(0, 'end')
        self.entry_price.delete(0, 'end')
        self.entry_worker.delete(0, 'end')
        self.id_part_seleccionado = None
        self.precio_unitario_actual = None
        self.servicio_editando = None
        self.lbl_editando_servicio.configure(text="")
        self._set_cantidad(1)

    def _refrescar_orden_activa(self):
        """Actualiza el total mostrado de la orden activa y la tabla de
        servicios sin tocar self.servicios_pendientes (a diferencia de
        _activar_orden, que los descarta)."""
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("""SELECT O.Id_Order, Cu.Name, Cu.LastName, O.VIN, O.TotalAmount
                              FROM Orders O JOIN Customers Cu ON O.Id_Customer = Cu.Id_Customer
                              WHERE O.Id_Order = ?""", (self.orden_actual,))
            row = cursor.fetchone(); conn.close()
        except Exception:
            row = None
        if row:
            vin_txt = row[3] or "sin vehículo asociado"
            total = row[4] if row[4] is not None else 0
            texto = f"Orden #{row[0]}\n{row[1]} {row[2]}\nVIN: {vin_txt}\nTotal: ${total:,.2f}"
            self.lbl_orden_activa.configure(text=texto)
            self.lbl_orden_activa_2.configure(text=texto)
        self.cargar_servicios()

    def seleccionar_servicio(self, event):
        """Al seleccionar un servicio (pendiente o ya guardado) en la tabla,
        carga sus datos en el formulario para poder editarlo con
        GUARDAR CAMBIOS."""
        seleccion = self.tree_servicios.focus()
        if not seleccion:
            return
        if seleccion.startswith("pend-"):
            idx = int(seleccion.split("-", 1)[1])
            if not (0 <= idx < len(self.servicios_pendientes)): return
            s = self.servicios_pendientes[idx]
            self._limpiar_form_servicio()
            self.servicio_editando = ("pend", idx)
            self.entry_parte.insert(0, s["part_name"])
            self.entry_duration.insert(0, s["duration"] or "")
            if s["price"] is not None: self.entry_price.insert(0, f"{s['price']:.2f}")
            self.entry_worker.insert(0, s["worker"] or "")
            self.id_part_seleccionado = s["id_part"]
            self.precio_unitario_actual = s["price"]
            self.lbl_editando_servicio.configure(text=f"✎ Editando servicio pendiente (fila {idx + 1})")
        elif seleccion.startswith("db-"):
            id_service = int(seleccion.split("-", 1)[1])
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("""SELECT S.Id_Part, COALESCE(I.PartName, 'Sin refacción'), S.Duration,
                                         S.Price, S.Worker
                                  FROM Services S
                                  LEFT JOIN Inventory I ON S.Id_Part = I.Id_Part
                                  WHERE S.Id_Service = ?""", (id_service,))
                fila = cursor.fetchone(); conn.close()
            except Exception as e:
                return messagebox.showerror("Error", str(e))
            if not fila:
                return
            id_part, part_name, duration, price, worker = fila
            self._limpiar_form_servicio()
            self.servicio_editando = ("db", id_service, id_part, price)
            self.entry_parte.insert(0, part_name)
            self.entry_duration.insert(0, duration or "")
            if price is not None: self.entry_price.insert(0, f"{price:.2f}")
            self.entry_worker.insert(0, worker or "")
            self.id_part_seleccionado = id_part
            self.precio_unitario_actual = price
            self.lbl_editando_servicio.configure(text=f"✎ Editando servicio guardado #{id_service}")

    def guardar_cambios_servicio(self):
        """Aplica los cambios hechos en el formulario al servicio seleccionado
        con seleccionar_servicio (pendiente o ya guardado en la BD)."""
        if not self.servicio_editando:
            return messagebox.showwarning(
                "Advertencia", "Selecciona un servicio de la tabla (haciendo clic en él) para editarlo.")
        self._sincronizar_parte(autofill_precio=False)
        if not self.id_part_seleccionado:
            return messagebox.showwarning(
                "Error", "Esa refacción no está registrada en INVENTARIO.\n"
                "Escribe el nombre exacto de una refacción existente o regístrala primero en la pestaña INVENTARIO.")
        precio_total, error_precio = self._limpiar_precio(self.entry_price.get())
        if error_precio: return messagebox.showwarning("Error", error_precio)
        worker = self.entry_worker.get().strip()
        if not worker: return messagebox.showwarning("Error", "El mecánico asignado es obligatorio.")
        duration = self.entry_duration.get().strip()
        cantidad = max(1, self.cantidad_servicio)
        precio_unitario_guardar = round(precio_total / cantidad, 2) if precio_total is not None else None

        tipo = self.servicio_editando[0]
        if tipo == "pend":
            idx = self.servicio_editando[1]
            if not (0 <= idx < len(self.servicios_pendientes)):
                self.servicio_editando = None
                return messagebox.showwarning("Error", "Ese servicio pendiente ya no existe.")
            id_part_original = self.servicios_pendientes[idx]["id_part"]
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("SELECT PartName, Stock FROM Inventory WHERE Id_Part = ?", (self.id_part_seleccionado,))
                fila = cursor.fetchone(); conn.close()
            except Exception as e:
                return messagebox.showerror("Error", str(e))
            if not fila:
                return messagebox.showwarning("Error", "La refacción ya no existe en inventario.")
            part_name, stock_actual = fila
            if self.id_part_seleccionado != id_part_original:
                usado_pendiente = sum(1 for i, s in enumerate(self.servicios_pendientes)
                                       if i != idx and s["id_part"] == self.id_part_seleccionado)
                if usado_pendiente + 1 > stock_actual:
                    return messagebox.showwarning(
                        "Sin stock", f"No hay stock disponible de '{part_name}' para hacer este cambio.")
            self.servicios_pendientes[idx] = {
                "id_part": self.id_part_seleccionado, "part_name": part_name,
                "duration": duration, "price": precio_unitario_guardar, "worker": worker,
            }
            self.cargar_servicios()
            self._limpiar_form_servicio()
            messagebox.showinfo("Éxito", "Servicio pendiente actualizado.")
        else:
            _, id_service, id_part_original, precio_original = self.servicio_editando
            try:
                conn = conectar(); cursor = conn.cursor()
                if self.id_part_seleccionado != id_part_original:
                    cursor.execute("SELECT PartName, Stock FROM Inventory WHERE Id_Part = ?",
                                   (self.id_part_seleccionado,))
                    fila = cursor.fetchone()
                    if not fila:
                        conn.close()
                        return messagebox.showwarning("Error", "La refacción ya no existe en inventario.")
                    part_name, stock_actual = fila
                    if stock_actual <= 0:
                        conn.close()
                        return messagebox.showwarning(
                            "Sin stock", f"No hay stock disponible de '{part_name}' para hacer este cambio.")
                    if id_part_original:
                        cursor.execute("UPDATE Inventory SET Stock = Stock + 1 WHERE Id_Part = ?", (id_part_original,))
                    cursor.execute("UPDATE Inventory SET Stock = Stock - 1 WHERE Id_Part = ? AND Stock > 0",
                                   (self.id_part_seleccionado,))
                cursor.execute("UPDATE Services SET Duration=?, Price=?, Worker=?, Id_Part=? WHERE Id_Service=?",
                               (duration, precio_unitario_guardar, worker, self.id_part_seleccionado, id_service))
                diferencia = (precio_unitario_guardar or 0) - (precio_original or 0)
                cursor.execute("UPDATE Orders SET TotalAmount = TotalAmount + ? WHERE Id_Order = ?",
                               (diferencia, self.orden_actual))
                conn.commit(); conn.close()
                estado.actualizar_datos_precarga()
                self._refrescar_orden_activa()
                self.cargar_ordenes()
                self._limpiar_form_servicio()
                messagebox.showinfo("Éxito", "Servicio actualizado.")
            except Exception as e: messagebox.showerror("Error", str(e))

    def pedir_ticket_pdf(self):
        if not self.orden_actual:
            return messagebox.showwarning("Error", "Selecciona una orden en la tabla de ÓRDENES.")
        exito, mensaje = reportes.crear_pdf_profesional(self.orden_actual)
        if exito: messagebox.showinfo("Éxito", mensaje)
        else: messagebox.showerror("Error PDF", mensaje)
