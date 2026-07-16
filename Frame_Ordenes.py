import customtkinter as ctk
from tkinter import messagebox, ttk

import reportes
from conexion import conectar
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT,
                     COLOR_ACCENT2, COLOR_TEXT_MAIN, COLOR_TEXT_DIM, ENTRY_STYLE, LABEL_STYLE,
                     hacer_boton_accion, mostrar_autocomplete)


class FrameOrdenes:
    def __init__(self, parent):
        self.build(parent)
        self.cargar()

    def build(self, parent):
        ser_outer = ctk.CTkFrame(parent, fg_color="transparent")
        ser_outer.pack(expand=True, fill="both", padx=32, pady=(20, 20))

        # Header tipo tarjeta: icono + título + descripción, contador en vivo a la derecha
        ser_header = ctk.CTkFrame(ser_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                                   border_width=1, border_color=COLOR_BORDER, height=60)
        ser_header.pack(fill="x", pady=(0, 16))
        ser_header.pack_propagate(False)
        ctk.CTkFrame(ser_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        ser_header_txt = ctk.CTkFrame(ser_header, fg_color="transparent")
        ser_header_txt.pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(ser_header_txt, text="🔧  ÓRDENES DE SERVICIO",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(ser_header_txt, text="Registro, edición y seguimiento de órdenes de trabajo",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        self.lbl_total = ctk.CTkLabel(ser_header, text="0 ÓRDENES",
                                       font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT)
        self.lbl_total.pack(side="right", padx=20)

        ser_body = ctk.CTkFrame(ser_outer, fg_color="transparent")
        ser_body.pack(expand=True, fill="both")

        f_form_ser = ctk.CTkScrollableFrame(ser_body, fg_color=COLOR_BG_CARD, width=380,
                                             corner_radius=6, border_width=1, border_color=COLOR_BORDER)
        f_form_ser.pack(side="left", fill="y", padx=(0, 20))
        ctk.CTkFrame(f_form_ser, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(f_form_ser, text="ORDEN DE TRABAJO", font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=(12, 0))
        ctk.CTkLabel(f_form_ser, text="DETALLE DEL SERVICIO", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(2, 8))

        self.entry_part = self._campo(f_form_ser, "TRABAJO / REPUESTOS", "Descripción del servicio")
        self.entry_duration = self._campo(f_form_ser, "TIEMPO ESTIMADO", "Ej: 3 Horas")
        self.entry_price = self._campo(f_form_ser, "COSTO TOTAL ($)", "0.00")
        self.entry_worker = self._campo(f_form_ser, "MECÁNICO ASIGNADO", "Nombre del mecánico")

        ctk.CTkLabel(f_form_ser, text="VIN DEL VEHÍCULO", **LABEL_STYLE).pack(anchor="w", padx=24, pady=(10, 0))
        self.search_vin = ctk.CTkEntry(f_form_ser, placeholder_text="Escribir o buscar VIN...", width=320, height=42, **ENTRY_STYLE)
        self.search_vin.pack(padx=24, pady=(2, 0))
        self.search_vin.bind("<KeyRelease>", lambda e: mostrar_autocomplete(self.search_vin, "auto"))

        ctk.CTkFrame(f_form_ser, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=24, pady=14)
        hacer_boton_accion(f_form_ser, "CREAR ORDEN", COLOR_ACCENT, self.guardar, "＋").pack(fill="x", padx=24, pady=3)
        hacer_boton_accion(f_form_ser, "ACTUALIZAR ORDEN", "#1a3a1a", self.editar, "✎").pack(fill="x", padx=24, pady=3)
        ctk.CTkButton(f_form_ser, text="⬇  EXPORTAR PDF", fg_color="transparent",
                      border_width=1, border_color=COLOR_ACCENT2, text_color=COLOR_ACCENT2,
                      height=42, corner_radius=4, font=("Segoe UI", 12, "bold"),
                      command=self.pedir_ticket_pdf).pack(fill="x", padx=24, pady=3)

        t_frame_ser = ctk.CTkFrame(ser_body, fg_color=COLOR_BG_CARD, corner_radius=6,
                                    border_width=1, border_color=COLOR_BORDER)
        t_frame_ser.pack(side="right", expand=True, fill="both")
        ctk.CTkFrame(t_frame_ser, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        ser_tabla_toolbar = ctk.CTkFrame(t_frame_ser, fg_color="transparent")
        ser_tabla_toolbar.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(ser_tabla_toolbar, text="🔍", font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_DIM).pack(side="left", padx=(0, 8))
        self.buscar_entry = ctk.CTkEntry(ser_tabla_toolbar, placeholder_text="Buscar por descripción, mecánico o VIN...",
                                          height=36, **ENTRY_STYLE)
        self.buscar_entry.pack(side="left", expand=True, fill="x")
        self.buscar_entry.bind("<KeyRelease>", lambda e: self.cargar(self.buscar_entry.get().strip()))

        self.tree = ttk.Treeview(t_frame_ser,
                                  columns=("ID","Descripción","Hrs","Costo","Mecánico","VIN"),
                                  show="headings")
        encabezados = [("ID","ID",50),("Descripción","DESCRIPCIÓN",230),("Hrs","HRS",80),
                        ("Costo","COSTO",100),("Mecánico","MECÁNICO",140),("VIN","VIN",180)]
        for c, txt, w in encabezados:
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, anchor="center" if c in ("ID","Hrs","Costo") else "w")
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
                like = f"%{filtro}%"
                cursor.execute(
                    "SELECT Id_Service, ReplacedPart, Duration, Price, Worker, VIN FROM Services "
                    "WHERE ReplacedPart LIKE ? OR Worker LIKE ? OR VIN LIKE ?", (like, like, like))
            else:
                cursor.execute("SELECT Id_Service, ReplacedPart, Duration, Price, Worker, VIN FROM Services")
            filas = cursor.fetchall()
            for i, row in enumerate(filas):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=[str(v) for v in row], tags=(tag,))
            self.tree.tag_configure('even', background=COLOR_BG_CARD)
            self.tree.tag_configure('odd', background=COLOR_BG_CARD_ALT)
            if filtro:
                etiqueta = "RESULTADO" if len(filas) == 1 else "RESULTADOS"
            else:
                etiqueta = "ORDEN" if len(filas) == 1 else "ÓRDENES"
            self.lbl_total.configure(text=f"{len(filas)} {etiqueta}")
            conn.close()
        except Exception as e: print(e)

    def guardar(self):
        vin = self.search_vin.get()
        if not vin: return messagebox.showwarning("Error", "Escribe o selecciona un VIN.")
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("INSERT INTO Services (ReplacedPart, Duration, Price, Worker, VIN) VALUES (?,?,?,?,?)",
                           (self.entry_part.get(), self.entry_duration.get(), self.entry_price.get(), self.entry_worker.get(), vin))
            conn.commit(); conn.close(); self.cargar(); self.limpiar()
            messagebox.showinfo("Éxito", "Orden de servicio creada.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def editar(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un servicio.")
        id_servicio = int(str(self.tree.item(seleccion, 'values')[0]).replace(',', ''))
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("UPDATE Services SET ReplacedPart=?, Duration=?, Price=?, Worker=?, VIN=? WHERE Id_Service=?",
                           (self.entry_part.get(), self.entry_duration.get(), self.entry_price.get(), self.entry_worker.get(), self.search_vin.get(), id_servicio))
            conn.commit(); conn.close(); self.cargar(); self.limpiar()
            messagebox.showinfo("Éxito", "Servicio modificado.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Advertencia", "Seleccione un servicio.")
        id_servicio = int(str(self.tree.item(seleccion, 'values')[0]).replace(',', ''))
        if messagebox.askyesno("Confirmar", "¿Borrar esta orden?"):
            try:
                conn = conectar(); cursor = conn.cursor()
                cursor.execute("DELETE FROM Services WHERE Id_Service=?", (id_servicio,))
                conn.commit(); conn.close(); self.cargar(); self.limpiar()
            except Exception as e: messagebox.showerror("Error", str(e))

    def limpiar(self):
        self.entry_part.delete(0, 'end'); self.entry_duration.delete(0, 'end')
        self.entry_price.delete(0, 'end'); self.entry_worker.delete(0, 'end'); self.search_vin.delete(0, 'end')

    def seleccionar(self, event):
        seleccion = self.tree.focus()
        if seleccion:
            valores = self.tree.item(seleccion, 'values')
            self.limpiar()
            self.entry_part.insert(0, valores[1]); self.entry_duration.insert(0, valores[2])
            self.entry_price.insert(0, valores[3]); self.entry_worker.insert(0, valores[4])
            self.search_vin.insert(0, valores[5])

    def pedir_ticket_pdf(self):
        seleccion = self.tree.focus()
        if not seleccion: return messagebox.showwarning("Error", "Selecciona un servicio.")
        valores = self.tree.item(seleccion, 'values')
        exito, mensaje = reportes.crear_pdf_profesional(valores[0], valores[1], valores[3], valores[5])
        if exito: messagebox.showinfo("Éxito", mensaje)
        else: messagebox.showerror("Error PDF", mensaje)
