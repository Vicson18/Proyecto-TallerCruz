import threading
from datetime import datetime

import customtkinter as ctk

import bot_taller
from estilo import (COLOR_BG_CARD, COLOR_BG_CARD_ALT, COLOR_BORDER, COLOR_ACCENT,
                     COLOR_ACCENT_DIM, COLOR_TEXT_MAIN, COLOR_TEXT_DIM, COLOR_SUCCESS,
                     ENTRY_STYLE)

BIENVENIDA = (
    "Hola! Soy el asistente de Cruz PRO.\n\n"
    "Puedo consultar la base de datos por ti. Ejemplos:\n"
    "  • ultimo servicio de Juan\n"
    "  • que autos tiene Carlos\n"
    "  • cuanto hemos facturado\n"
    "  • quien es el mejor mecanico\n\n"
    "Escribe 'ayuda' para ver todos los comandos."
)

DOTS_ANIM = ["●  ∙  ∙", "∙  ●  ∙", "∙  ∙  ●"]


class FrameIA:
    def __init__(self, parent):
        self.typing_fila = None
        self.typing_label = None
        self.typing_after_id = None
        self.build(parent)

    def build(self, parent):
        bot_outer = ctk.CTkFrame(parent, fg_color="transparent")
        bot_outer.pack(expand=True, fill="both", padx=32, pady=20)

        f_chat = ctk.CTkFrame(bot_outer, fg_color=COLOR_BG_CARD, corner_radius=8,
                              border_width=1, border_color=COLOR_BORDER)
        f_chat.pack(expand=True, fill="both")

        # Barra de encabezado integrada en la propia tarjeta del chat
        chat_header = ctk.CTkFrame(f_chat, fg_color=COLOR_BG_CARD_ALT, height=56, corner_radius=0)
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)
        ctk.CTkFrame(chat_header, fg_color=COLOR_ACCENT, width=4, corner_radius=0).pack(side="left", fill="y")

        self._crear_avatar(chat_header, "⬡", COLOR_ACCENT, size=34).pack(side="left", padx=(14, 10))

        titulos = ctk.CTkFrame(chat_header, fg_color="transparent")
        titulos.pack(side="left")
        ctk.CTkLabel(titulos, text="Asistente IA — Cruz PRO", font=("Segoe UI", 14, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(10, 0))
        ctk.CTkLabel(titulos, text="Consulta la base de datos escribiendo en lenguaje natural",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w")

        estado_f = ctk.CTkFrame(chat_header, fg_color="transparent")
        estado_f.pack(side="right", padx=16)
        ctk.CTkLabel(estado_f, text="●", font=("Segoe UI", 11), text_color=COLOR_SUCCESS).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(estado_f, text="En línea", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_DIM).pack(side="left")

        ctk.CTkFrame(f_chat, fg_color=COLOR_BORDER, height=1, corner_radius=0).pack(fill="x")

        self.chat_scroll = ctk.CTkScrollableFrame(f_chat, fg_color="#0d0d0d", corner_radius=0)
        self.chat_scroll.pack(expand=True, fill="both", padx=0, pady=0)

        self.agregar_bienvenida()

        ctk.CTkFrame(f_chat, fg_color=COLOR_BORDER, height=1, corner_radius=0).pack(fill="x")
        entry_row = ctk.CTkFrame(f_chat, fg_color=COLOR_BG_CARD_ALT)
        entry_row.pack(fill="x", padx=0, pady=0)
        entry_inner = ctk.CTkFrame(entry_row, fg_color="transparent")
        entry_inner.pack(fill="x", padx=16, pady=14)

        entry_style = dict(ENTRY_STYLE)
        entry_style["corner_radius"] = 22
        self.entry_chat = ctk.CTkEntry(entry_inner, placeholder_text="Escribe tu consulta y presiona ENTER...",
                                        height=44, **entry_style)
        self.entry_chat.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entry_chat.bind("<Return>", self.enviar_mensaje_chat)
        ctk.CTkButton(entry_inner, text="ENVIAR  ▶", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DIM,
                      text_color="white", width=110, height=44, corner_radius=22,
                      font=("Segoe UI", 12, "bold"), command=self.enviar_mensaje_chat).pack(side="right")

    def _crear_avatar(self, parent, texto, color, size=30):
        avatar = ctk.CTkFrame(parent, width=size, height=size, corner_radius=size // 2, fg_color=color)
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=texto, font=("Segoe UI", 12, "bold"), text_color="#ffffff").pack(expand=True)
        return avatar

    def _hora_actual(self):
        return datetime.now().strftime("%H:%M")

    def agregar_bienvenida(self):
        fila = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(16, 4))
        self._crear_avatar(fila, "⬡", COLOR_ACCENT).pack(side="left", anchor="nw")
        msg_col = ctk.CTkFrame(fila, fg_color="transparent")
        msg_col.pack(side="left", anchor="w", padx=(8, 0))
        ctk.CTkLabel(msg_col, text=f"Cruz PRO · {self._hora_actual()}", font=("Segoe UI", 9, "bold"),
                     text_color=COLOR_ACCENT).pack(anchor="w", pady=(2, 4))
        burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                               corner_radius=14, border_width=1, border_color=COLOR_BORDER)
        burbuja.pack(anchor="w")
        ctk.CTkLabel(burbuja, text=BIENVENIDA, font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_MAIN, wraplength=500,
                     justify="left", padx=14, pady=10).pack()

    def agregar_burbuja(self, texto, tipo):
        fila = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=6)
        if tipo == "user":
            msg_col = ctk.CTkFrame(fila, fg_color="transparent")
            msg_col.pack(side="right", anchor="e", padx=(0, 8))
            ctk.CTkLabel(msg_col, text=f"Tú · {self._hora_actual()}", font=("Segoe UI", 9, "bold"),
                         text_color=COLOR_TEXT_DIM).pack(anchor="e", pady=(2, 4))
            burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_ACCENT, corner_radius=14)
            burbuja.pack(anchor="e")
            ctk.CTkLabel(burbuja, text=texto, font=("Segoe UI", 13),
                         text_color="#ffffff", wraplength=480,
                         justify="right", padx=14, pady=10).pack()
            self._crear_avatar(fila, "Tú", COLOR_TEXT_DIM).pack(side="right", anchor="nw")
        else:
            self._crear_avatar(fila, "⬡", COLOR_ACCENT).pack(side="left", anchor="nw")
            msg_col = ctk.CTkFrame(fila, fg_color="transparent")
            msg_col.pack(side="left", anchor="w", padx=(8, 0))
            ctk.CTkLabel(msg_col, text=f"Cruz PRO · {self._hora_actual()}", font=("Segoe UI", 9, "bold"),
                         text_color=COLOR_ACCENT).pack(anchor="w", pady=(2, 4))
            burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                                   corner_radius=14, border_width=1, border_color=COLOR_BORDER)
            burbuja.pack(anchor="w")
            ctk.CTkLabel(burbuja, text=texto, font=("Segoe UI", 13),
                         text_color=COLOR_TEXT_MAIN, wraplength=500,
                         justify="left", padx=14, pady=10).pack()
        self._scroll_abajo()

    def _scroll_abajo(self):
        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def _mostrar_typing(self):
        self.typing_fila = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        self.typing_fila.pack(fill="x", padx=16, pady=6)
        self._crear_avatar(self.typing_fila, "⬡", COLOR_ACCENT).pack(side="left", anchor="nw")
        msg_col = ctk.CTkFrame(self.typing_fila, fg_color="transparent")
        msg_col.pack(side="left", anchor="w", padx=(8, 0))
        burbuja = ctk.CTkFrame(msg_col, fg_color=COLOR_BG_CARD_ALT,
                               corner_radius=14, border_width=1, border_color=COLOR_BORDER)
        burbuja.pack(anchor="w")
        self.typing_label = ctk.CTkLabel(burbuja, text=DOTS_ANIM[0], font=("Segoe UI", 13),
                                          text_color=COLOR_TEXT_DIM, padx=14, pady=10)
        self.typing_label.pack()
        self._animar_typing(0)
        self._scroll_abajo()

    def _animar_typing(self, paso):
        if not (self.typing_label and self.typing_label.winfo_exists()):
            return
        self.typing_label.configure(text=DOTS_ANIM[paso % len(DOTS_ANIM)])
        self.typing_after_id = self.chat_scroll.after(350, self._animar_typing, paso + 1)

    def _quitar_typing(self):
        if self.typing_after_id:
            self.chat_scroll.after_cancel(self.typing_after_id)
            self.typing_after_id = None
        if self.typing_fila and self.typing_fila.winfo_exists():
            self.typing_fila.destroy()
        self.typing_fila = None
        self.typing_label = None

    def enviar_mensaje_chat(self, event=None):
        if self.entry_chat.cget("state") == "disabled": return
        m = self.entry_chat.get().strip()
        if not m: return
        self.entry_chat.configure(state="disabled")
        self.entry_chat.delete(0, "end")
        self.agregar_burbuja(m, "user")
        self._mostrar_typing()
        def obtener_respuesta():
            r = bot_taller.procesar_lenguaje_natural(m)
            self.chat_scroll.after(0, lambda: self._mostrar_bot(r))
        threading.Thread(target=obtener_respuesta, daemon=True).start()

    def _mostrar_bot(self, r):
        self._quitar_typing()
        self.agregar_burbuja(r, "bot")
        self.entry_chat.configure(state="normal")
        self.entry_chat.focus()
