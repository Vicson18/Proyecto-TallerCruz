import customtkinter as ctk
from tkinter import messagebox

from conexion import conectar
from estilo import (COLOR_BG_BASE, COLOR_BG_CARD, COLOR_ACCENT, COLOR_ACCENT_DIM,
                     COLOR_TEXT_MAIN, COLOR_TEXT_DIM, COLOR_BORDER, ENTRY_STYLE,
                     animar_entrada)


class FrameLogin:
    def __init__(self, on_success):
        self.on_success = on_success
        self.build()

    def build(self):
        self.ventana = ctk.CTk()
        self.ventana.title("Cruz PRO — Acceso")
        self.ventana.geometry("1000x700")
        self.ventana.configure(fg_color=COLOR_BG_BASE)
        self.ventana.resizable(False, False)

        ctk.CTkFrame(self.ventana, fg_color=COLOR_ACCENT, width=5, corner_radius=0).place(x=0, y=0, relheight=1)

        card = ctk.CTkFrame(self.ventana, fg_color=COLOR_BG_CARD, corner_radius=6,
                            width=420, height=570, border_width=1, border_color=COLOR_BORDER)
        card.pack_propagate(False)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(card, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        logo_login = ctk.CTkFrame(card, fg_color="transparent")
        logo_login.pack(pady=(32, 0))
        ctk.CTkLabel(logo_login, text="⬡", font=("Arial", 38), text_color=COLOR_ACCENT).pack()
        ctk.CTkLabel(logo_login, text="CRUZ PRO", font=("Segoe UI", 26, "bold"), text_color=COLOR_TEXT_MAIN).pack()
        ctk.CTkLabel(logo_login, text="SISTEMA DE GESTIÓN AUTOMOTRIZ",
                     font=("Segoe UI", 9, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=(3, 0))

        ctk.CTkFrame(card, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=40, pady=24)

        ctk.CTkLabel(card, text="USUARIO", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", padx=40)
        self.entry_usuario = ctk.CTkEntry(card, placeholder_text="ID de colaborador", width=340, height=48, **ENTRY_STYLE)
        self.entry_usuario.pack(padx=40, pady=(4, 14))

        ctk.CTkLabel(card, text="CONTRASEÑA", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", padx=40)
        self.entry_contraseña = ctk.CTkEntry(card, placeholder_text="Clave de acceso", show="*", width=340, height=48, **ENTRY_STYLE)
        self.entry_contraseña.pack(padx=40, pady=(4, 0))
        self.entry_contraseña.bind("<Return>", lambda e: self.login())

        ctk.CTkFrame(card, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=40, pady=22)

        ctk.CTkButton(card, text="INICIAR SESIÓN  ▶", command=self.login, width=340, height=50,
                      fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM,
                      text_color="white", corner_radius=4,
                      font=("Segoe UI", 13, "bold")).pack(padx=40)

        ctk.CTkLabel(card, text="CRUZ PRO  //  v2.0  //  Taller Cruz",
                     font=("Segoe UI", 9), text_color="#333333").pack(pady=(16, 0))

    def login(self):
        u, c = self.entry_usuario.get(), self.entry_contraseña.get()
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (u, c))
            if cursor.fetchone():
                self.ventana.withdraw()
                self.on_success(self.ventana)
            else:
                messagebox.showerror("Acceso Denegado", "Credenciales incorrectas.")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error Crítico", str(e))

    def run(self):
        animar_entrada(self.ventana)
        self.ventana.mainloop()
