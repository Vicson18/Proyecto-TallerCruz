import threading
import customtkinter as ctk

import bot_taller
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT,
                     COLOR_ACCENT_DIM, COLOR_TEXT_MAIN, COLOR_TEXT_DIM, ENTRY_STYLE)

BIENVENIDA = (
    "Hola! Soy el asistente de Cruz PRO.\n\n"
    "Puedo consultar la base de datos por ti. Ejemplos:\n"
    "  • ultimo servicio de Juan\n"
    "  • que autos tiene Carlos\n"
    "  • cuanto hemos facturado\n"
    "  • quien es el mejor mecanico\n\n"
    "Escribe 'ayuda' para ver todos los comandos."
)


class FrameIA:
    def __init__(self, parent):
        self.build(parent)

    def build(self, parent):
        bot_outer = ctk.CTkFrame(parent, fg_color="transparent")
        bot_outer.pack(expand=True, fill="both", padx=32, pady=24)

        bot_header = ctk.CTkFrame(bot_outer, fg_color="transparent")
        bot_header.pack(fill="x", pady=(0, 12))
        ctk.CTkFrame(bot_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y", padx=(0,12))
        ctk.CTkLabel(bot_header, text="ASISTENTE IA", font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(bot_header, text="  //  Escribe tu consulta abajo",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(side="left")

        f_chat = ctk.CTkFrame(bot_outer, fg_color=COLOR_BG_CARD, corner_radius=6,
                              border_width=1, border_color=COLOR_BORDER)
        f_chat.pack(expand=True, fill="both")
        ctk.CTkFrame(f_chat, fg_color=COLOR_ACCENT, height=4, corner_radius=0).pack(fill="x")

        self.chat_scroll = ctk.CTkScrollableFrame(f_chat, fg_color="#0d0d0d", corner_radius=0)
        self.chat_scroll.pack(expand=True, fill="both", padx=0, pady=0)

        self.agregar_bienvenida()

        ctk.CTkFrame(f_chat, fg_color=COLOR_BORDER, height=1, corner_radius=0).pack(fill="x")
        entry_row = ctk.CTkFrame(f_chat, fg_color="transparent")
        entry_row.pack(fill="x", padx=20, pady=12)
        self.entry_chat = ctk.CTkEntry(entry_row, placeholder_text="Escribe tu consulta y presiona ENTER...",
                                        height=44, **ENTRY_STYLE)
        self.entry_chat.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entry_chat.bind("<Return>", self.enviar_mensaje_chat)
        ctk.CTkButton(entry_row, text="ENVIAR  ▶", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM,
                      text_color="white", width=110, height=44, corner_radius=4,
                      font=("Segoe UI", 12, "bold"), command=self.enviar_mensaje_chat).pack(side="right")

    def agregar_bienvenida(self):
        fila = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(16, 4))
        icono_col = ctk.CTkFrame(fila, fg_color="transparent")
        icono_col.pack(side="left", anchor="nw")
        ctk.CTkLabel(icono_col, text="Cruz PRO", font=("Segoe UI", 9, "bold"),
                     text_color=COLOR_ACCENT, width=30).pack(pady=(4, 0))
        msg_col = ctk.CTkFrame(fila, fg_color="transparent")
        msg_col.pack(side="left", anchor="w", padx=(6, 0))
        burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                               corner_radius=14, border_width=1, border_color=COLOR_BORDER)
        burbuja.pack(anchor="w")
        ctk.CTkLabel(burbuja, text=BIENVENIDA, font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_MAIN, wraplength=500,
                     justify="left", padx=14, pady=10).pack()

    def agregar_burbuja(self, texto, tipo):
        fila = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=4)
        if tipo == "user":
            burbuja = ctk.CTkFrame(fila, fg_color=COLOR_ACCENT, corner_radius=14)
            burbuja.pack(side="right", anchor="e")
            ctk.CTkLabel(burbuja, text=texto, font=("Segoe UI", 13),
                         text_color="#ffffff", wraplength=500,
                         justify="right", padx=14, pady=10).pack()
            ctk.CTkLabel(fila, text="Tu", font=("Segoe UI", 9),
                         text_color=COLOR_TEXT_DIM).pack(side="right", anchor="se", padx=(0,4))
        else:
            icono_col = ctk.CTkFrame(fila, fg_color="transparent")
            icono_col.pack(side="left", anchor="nw")
            ctk.CTkLabel(icono_col, text="Cruz PRO", font=("Segoe UI", 9, "bold"),
                         text_color=COLOR_ACCENT, width=30).pack(pady=(4, 0))
            msg_col = ctk.CTkFrame(fila, fg_color="transparent")
            msg_col.pack(side="left", anchor="w", padx=(6, 0))
            burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                                   corner_radius=14, border_width=1, border_color=COLOR_BORDER)
            burbuja.pack(anchor="w")
            ctk.CTkLabel(burbuja, text=texto, font=("Segoe UI", 13),
                         text_color=COLOR_TEXT_MAIN, wraplength=500,
                         justify="left", padx=14, pady=10).pack()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def enviar_mensaje_chat(self, event=None):
        if self.entry_chat.cget("state") == "disabled": return
        m = self.entry_chat.get().strip()
        if not m: return
        self.entry_chat.configure(state="disabled")
        self.entry_chat.delete(0, "end")
        self.agregar_burbuja(m, "user")
        def obtener_respuesta():
            r = bot_taller.procesar_lenguaje_natural(m)
            self.chat_scroll.after(0, lambda: self._mostrar_bot(r))
        threading.Thread(target=obtener_respuesta, daemon=True).start()

    def _mostrar_bot(self, r):
        self.agregar_burbuja(r, "bot")
        self.entry_chat.configure(state="normal")
        self.entry_chat.focus()
