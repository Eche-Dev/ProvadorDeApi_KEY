"""
Aplicación GUI de escritorio para probar API Keys y endpoints REST.
Desarrollada en Python con Tkinter y ttk, con soporte para hilos asíncronos
(no congela la ventana durante la prueba).
"""

import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import api_tester


class ApiKeyTesterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Probador de API Keys & REST APIs ⚡")
        self.geometry("860x720")
        self.minsize(780, 640)

        # Configuración de colores (Tema Oscuro Moderno / Catppuccin Mocha)
        self.colors = {
            "bg": "#181825",
            "card_bg": "#1e1e2e",
            "card_border": "#313244",
            "surface": "#313244",
            "text": "#cdd6f4",
            "subtext": "#a6adc8",
            "accent": "#89b4fa",
            "accent_hover": "#b4befe",
            "btn_text": "#11111b",
            "success": "#a6e3a1",
            "success_bg": "#19392b",
            "error": "#f38ba8",
            "error_bg": "#431f2f",
            "warning": "#f9e2af",
            "warning_bg": "#3e371f",
            "info": "#89dceb",
            "entry_bg": "#11111b"
        }

        self.configure(bg=self.colors["bg"])

        # Estado interno
        self.is_key_visible = False
        self.testing_in_progress = False
        self.history = []

        # Estilo ttk
        self.setup_styles()

        # Construir Interfaz
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Configuración general de ttk
        self.style.configure(".", background=self.colors["bg"], foreground=self.colors["text"])
        
        # Notebook (Pestañas)
        self.style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            padding=[16, 8],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["accent"]), ("active", self.colors["surface"])],
            foreground=[("selected", self.colors["btn_text"]), ("active", self.colors["text"])]
        )

        # Combobox
        self.style.configure(
            "TCombobox",
            fieldbackground=self.colors["entry_bg"],
            background=self.colors["surface"],
            foreground=self.colors["text"],
            arrowcolor=self.colors["accent"],
            padding=6,
            font=("Segoe UI", 10)
        )

        # Scrollbars
        self.style.configure(
            "Vertical.TScrollbar",
            background=self.colors["surface"],
            troughcolor=self.colors["bg"],
            arrowcolor=self.colors["subtext"]
        )

    def create_widgets(self):
        # 1. Cabecera (Header)
        header_frame = tk.Frame(self, bg=self.colors["bg"], pady=14, padx=20)
        header_frame.pack(fill="x")

        title_lbl = tk.Label(
            header_frame,
            text="⚡ Verificador de API Keys",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_frame,
            text="Comprueba al instante si una API Key está activa, válida y con saldo, o prueba cualquier endpoint REST.",
            font=("Segoe UI", 9),
            bg=self.colors["bg"],
            fg=self.colors["subtext"]
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Contenedor de Pestañas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Pestaña 1: Proveedores de IA y Servicios
        self.tab_ai = tk.Frame(self.notebook, bg=self.colors["bg"], padx=15, pady=15)
        self.notebook.add(self.tab_ai, text="  🤖 Proveedores AI & Cloud  ")
        self.build_ai_tab(self.tab_ai)

        # Pestaña 2: REST API General
        self.tab_rest = tk.Frame(self.notebook, bg=self.colors["bg"], padx=15, pady=15)
        self.notebook.add(self.tab_rest, text="  🌐 REST API General  ")
        self.build_rest_tab(self.tab_rest)

        # Pestaña 3: Historial
        self.tab_hist = tk.Frame(self.notebook, bg=self.colors["bg"], padx=15, pady=15)
        self.notebook.add(self.tab_hist, text="  📜 Historial  ")
        self.build_history_tab(self.tab_hist)

    # -------------------------------------------------------------
    # PESTAÑA 1: PROVEEDORES AI & CLOUD
    # -------------------------------------------------------------
    def build_ai_tab(self, parent):
        # Tarjeta superior: Selector y campo de API Key
        card_input = tk.Frame(parent, bg=self.colors["card_bg"], padx=16, pady=16, highlightthickness=1, highlightbackground=self.colors["card_border"])
        card_input.pack(fill="x", pady=(0, 15))

        # Fila 1: Selector de proveedor
        row1 = tk.Frame(card_input, bg=self.colors["card_bg"])
        row1.pack(fill="x", pady=(0, 10))

        lbl_prov = tk.Label(row1, text="Proveedor:", font=("Segoe UI", 10, "bold"), bg=self.colors["card_bg"], fg=self.colors["text"])
        lbl_prov.pack(side="left")

        # Lista de opciones de proveedores
        self.provider_options = [
            ("🔍 Detección Automática (según la clave)", "auto"),
            ("🤖 OpenAI (ChatGPT, GPT-4o, etc.)", "openai"),
            ("✨ Google Gemini", "gemini"),
            ("🧠 Anthropic (Claude)", "anthropic"),
            ("⚡ Groq", "groq"),
            ("🐋 DeepSeek", "deepseek"),
            ("🌐 OpenRouter", "openrouter"),
            ("🌪️ Mistral AI", "mistral"),
            ("🤗 Hugging Face", "huggingface"),
            ("🐙 GitHub Token / API", "github"),
            ("🎙️ ElevenLabs", "elevenlabs"),
            ("🔮 Cohere", "cohere"),
            ("🔍 Perplexity AI", "perplexity"),
        ]

        self.provider_var = tk.StringVar(value=self.provider_options[0][0])
        self.cb_provider = ttk.Combobox(
            row1,
            textvariable=self.provider_var,
            values=[opt[0] for opt in self.provider_options],
            state="readonly",
            width=38
        )
        self.cb_provider.pack(side="left", padx=(10, 15))

        self.lbl_hint = tk.Label(
            row1,
            text="Prefijo esperado: sk-..., AIzaSy..., gsk_...",
            font=("Segoe UI", 9, "italic"),
            bg=self.colors["card_bg"],
            fg=self.colors["subtext"]
        )
        self.lbl_hint.pack(side="left")

        # Fila 2: Entrada de API Key
        row2 = tk.Frame(card_input, bg=self.colors["card_bg"])
        row2.pack(fill="x", pady=(0, 10))

        lbl_key = tk.Label(row2, text="API Key:", font=("Segoe UI", 10, "bold"), bg=self.colors["card_bg"], fg=self.colors["text"])
        lbl_key.pack(side="left")

        entry_container = tk.Frame(row2, bg=self.colors["entry_bg"], highlightthickness=1, highlightbackground=self.colors["surface"])
        entry_container.pack(side="left", fill="x", expand=True, padx=(22, 10))

        self.key_entry = tk.Entry(
            entry_container,
            show="•",
            font=("Consolas", 11),
            bg=self.colors["entry_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            relief="flat",
            bd=6
        )
        self.key_entry.pack(side="left", fill="x", expand=True)
        self.key_entry.bind("<KeyRelease>", self.on_key_typed)
        self.key_entry.bind("<Return>", lambda e: self.start_test_ai())

        # Botón Ver / Ocultar
        self.btn_toggle_eye = tk.Button(
            row2,
            text="👁",
            font=("Segoe UI", 10),
            bg=self.colors["surface"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground=self.colors["btn_text"],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.toggle_key_visibility
        )
        self.btn_toggle_eye.pack(side="left", padx=(0, 6))

        # Botón Pegar Portapapeles
        self.btn_paste = tk.Button(
            row2,
            text="📋 Pegar",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["surface"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground=self.colors["btn_text"],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.paste_ai_key
        )
        self.btn_paste.pack(side="left")

        # Fila 3: Botón de probar
        self.btn_test_ai = tk.Button(
            card_input,
            text="▶  PROBAR SI FUNCIONA LA API KEY",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["accent"],
            fg=self.colors["btn_text"],
            activebackground=self.colors["accent_hover"],
            activeforeground=self.colors["btn_text"],
            relief="flat",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.start_test_ai
        )
        self.btn_test_ai.pack(fill="x", pady=(5, 0))

        # 3. Tarjeta de Resultado / Estado Visual
        self.card_result = tk.Frame(parent, bg=self.colors["card_bg"], padx=16, pady=16, highlightthickness=1, highlightbackground=self.colors["card_border"])
        self.card_result.pack(fill="both", expand=True)

        # Banner de Estado
        self.status_banner = tk.Frame(self.card_result, bg=self.colors["surface"], padx=14, pady=12)
        self.status_banner.pack(fill="x", pady=(0, 12))

        self.lbl_status_icon = tk.Label(self.status_banner, text="⚪", font=("Segoe UI", 24), bg=self.colors["surface"])
        self.lbl_status_icon.pack(side="left", padx=(0, 12))

        status_text_frame = tk.Frame(self.status_banner, bg=self.colors["surface"])
        status_text_frame.pack(side="left", fill="x", expand=True)

        self.lbl_status_title = tk.Label(
            status_text_frame,
            text="Listo para probar",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors["surface"],
            fg=self.colors["text"]
        )
        self.lbl_status_title.pack(anchor="w")

        self.lbl_status_meta = tk.Label(
            status_text_frame,
            text="Ingresa una clave arriba y haz clic en el botón para verificarla.",
            font=("Segoe UI", 9),
            bg=self.colors["surface"],
            fg=self.colors["subtext"]
        )
        self.lbl_status_meta.pack(anchor="w")

        # Área de detalles / Diagnóstico
        lbl_diag = tk.Label(self.card_result, text="Diagnóstico y Detalles de la Respuesta:", font=("Segoe UI", 10, "bold"), bg=self.colors["card_bg"], fg=self.colors["text"])
        lbl_diag.pack(anchor="w", pady=(0, 6))

        text_container = tk.Frame(self.card_result, bg=self.colors["entry_bg"])
        text_container.pack(fill="both", expand=True)

        self.txt_details = tk.Text(
            text_container,
            bg=self.colors["entry_bg"],
            fg=self.colors["text"],
            font=("Consolas", 10),
            wrap="word",
            relief="flat",
            bd=8,
            insertbackground=self.colors["accent"]
        )
        self.txt_details.pack(side="left", fill="both", expand=True)

        scroll_txt = ttk.Scrollbar(text_container, orient="vertical", command=self.txt_details.yview)
        scroll_txt.pack(side="right", fill="y")
        self.txt_details.config(yscrollcommand=scroll_txt.set)

        # Botón para copiar respuesta
        btn_copy_resp = tk.Button(
            self.card_result,
            text="📋 Copiar Detalles al Portapapeles",
            font=("Segoe UI", 9),
            bg=self.colors["surface"],
            fg=self.colors["text"],
            relief="flat",
            bd=0,
            pady=4,
            padx=10,
            cursor="hand2",
            command=self.copy_details_clipboard
        )
        btn_copy_resp.pack(anchor="e", pady=(8, 0))

    # -------------------------------------------------------------
    # PESTAÑA 2: REST API GENERAL
    # -------------------------------------------------------------
    def build_rest_tab(self, parent):
        card_rest = tk.Frame(parent, bg=self.colors["card_bg"], padx=16, pady=16, highlightthickness=1, highlightbackground=self.colors["card_border"])
        card_rest.pack(fill="both", expand=True)

        # Fila URL y Método
        row_url = tk.Frame(card_rest, bg=self.colors["card_bg"])
        row_url.pack(fill="x", pady=(0, 10))

        self.rest_method_var = tk.StringVar(value="GET")
        cb_method = ttk.Combobox(row_url, textvariable=self.rest_method_var, values=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"], state="readonly", width=8)
        cb_method.pack(side="left")

        self.rest_url_entry = tk.Entry(
            row_url,
            font=("Consolas", 10),
            bg=self.colors["entry_bg"],
            fg=self.colors["text"],
            relief="flat",
            bd=6
        )
        self.rest_url_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.rest_url_entry.insert(0, "https://api.github.com/zen")

        # Fila Autenticación
        row_auth = tk.Frame(card_rest, bg=self.colors["card_bg"])
        row_auth.pack(fill="x", pady=(0, 10))

        tk.Label(row_auth, text="Autenticación:", font=("Segoe UI", 9, "bold"), bg=self.colors["card_bg"], fg=self.colors["text"]).pack(side="left")

        self.rest_auth_type_var = tk.StringVar(value="none")
        cb_auth = ttk.Combobox(row_auth, textvariable=self.rest_auth_type_var, values=["none", "bearer", "header", "query_param"], state="readonly", width=12)
        cb_auth.pack(side="left", padx=(8, 12))

        tk.Label(row_auth, text="Token / Key:", font=("Segoe UI", 9), bg=self.colors["card_bg"], fg=self.colors["text"]).pack(side="left")
        self.rest_token_entry = tk.Entry(
            row_auth,
            font=("Consolas", 10),
            bg=self.colors["entry_bg"],
            fg=self.colors["text"],
            relief="flat",
            bd=5
        )
        self.rest_token_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Fila Headers y Body (Notebook interno de 2 pestañas)
        rest_subnotebook = ttk.Notebook(card_rest)
        rest_subnotebook.pack(fill="both", expand=True, pady=(5, 10))

        # Pestaña Headers
        tab_sub_headers = tk.Frame(rest_subnotebook, bg=self.colors["entry_bg"], padx=8, pady=8)
        rest_subnotebook.add(tab_sub_headers, text=" Headers Adicionales (JSON) ")
        self.txt_rest_headers = tk.Text(tab_sub_headers, height=4, bg=self.colors["entry_bg"], fg=self.colors["text"], font=("Consolas", 9), relief="flat")
        self.txt_rest_headers.pack(fill="both", expand=True)
        self.txt_rest_headers.insert("1.0", '{\n  "Accept": "application/json"\n}')

        # Pestaña Body
        tab_sub_body = tk.Frame(rest_subnotebook, bg=self.colors["entry_bg"], padx=8, pady=8)
        rest_subnotebook.add(tab_sub_body, text=" Request Body (JSON) ")
        self.txt_rest_body = tk.Text(tab_sub_body, height=4, bg=self.colors["entry_bg"], fg=self.colors["text"], font=("Consolas", 9), relief="flat")
        self.txt_rest_body.pack(fill="both", expand=True)

        # Botón Enviar Petición
        self.btn_send_rest = tk.Button(
            card_rest,
            text="▶  ENVIAR PETICIÓN REST",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["accent"],
            fg=self.colors["btn_text"],
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=self.start_test_rest
        )
        self.btn_send_rest.pack(fill="x", pady=(0, 10))

        # Área de respuesta REST
        self.lbl_rest_status = tk.Label(card_rest, text="Estado: En espera", font=("Segoe UI", 10, "bold"), bg=self.colors["card_bg"], fg=self.colors["subtext"])
        self.lbl_rest_status.pack(anchor="w", pady=(0, 4))

        self.txt_rest_resp = tk.Text(card_rest, height=8, bg=self.colors["entry_bg"], fg=self.colors["text"], font=("Consolas", 9), relief="flat", bd=6)
        self.txt_rest_resp.pack(fill="both", expand=True)

    # -------------------------------------------------------------
    # PESTAÑA 3: HISTORIAL
    # -------------------------------------------------------------
    def build_history_tab(self, parent):
        top_bar = tk.Frame(parent, bg=self.colors["bg"])
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="Registro de pruebas recientes:", font=("Segoe UI", 11, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(side="left")

        btn_clear = tk.Button(
            top_bar,
            text="🗑️ Limpiar Historial",
            font=("Segoe UI", 9),
            bg=self.colors["surface"],
            fg=self.colors["text"],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.clear_history
        )
        btn_clear.pack(side="right")

        self.txt_history = tk.Text(
            parent,
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
            font=("Consolas", 10),
            relief="flat",
            bd=10
        )
        self.txt_history.pack(fill="both", expand=True)
        self.update_history_display()

    # -------------------------------------------------------------
    # LÓGICA DE EVENTOS Y PRUEBAS ASÍNCRONAS
    # -------------------------------------------------------------
    def toggle_key_visibility(self):
        self.is_key_visible = not self.is_key_visible
        if self.is_key_visible:
            self.key_entry.config(show="")
            self.btn_toggle_eye.config(text="🙈")
        else:
            self.key_entry.config(show="•")
            self.btn_toggle_eye.config(text="👁")

    def paste_ai_key(self):
        try:
            clipboard_text = self.clipboard_get().strip().strip("\"'").strip()
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, clipboard_text)
            self.on_key_typed()
        except Exception:
            pass

    def on_key_typed(self, event=None):
        key = self.key_entry.get().strip()
        if not key:
            return

        # Si el usuario tiene seleccionada la opción "auto", previsualizar la detección
        detected = api_tester.detect_provider(key)
        for text, prov_id in self.provider_options:
            if prov_id == detected:
                cfg = api_tester.PROVIDERS.get(detected, {})
                hint = cfg.get("prefix_hint", "")
                self.lbl_hint.config(text=f"Detectado automáticamente: {cfg.get('name', detected)} (hint: {hint})")
                break

    def start_test_ai(self):
        if self.testing_in_progress:
            return

        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Atención", "Por favor ingresa o pega una API Key para probar.")
            return

        # Obtener el id del proveedor seleccionado
        selected_text = self.provider_var.get()
        provider_id = "auto"
        for text, pid in self.provider_options:
            if text == selected_text:
                provider_id = pid
                break

        # Actualizar UI a modo "Cargando..."
        self.testing_in_progress = True
        self.btn_test_ai.config(text="⏳ VERIFICANDO CONEXIÓN CON EL SERVIDOR...", state="disabled", bg=self.colors["surface"])
        self.status_banner.config(bg=self.colors["surface"])
        self.lbl_status_icon.config(text="⏳", bg=self.colors["surface"])
        self.lbl_status_title.config(text="Comprobando API Key...", fg=self.colors["warning"], bg=self.colors["surface"])
        self.lbl_status_meta.config(text="Enviando petición a la API oficial...", bg=self.colors["surface"])
        self.txt_details.delete("1.0", tk.END)
        self.txt_details.insert(tk.END, "Enviando solicitud de prueba...")

        # Ejecutar en segundo plano para que la ventana nunca se bloquee
        thread = threading.Thread(target=self._run_ai_test_worker, args=(provider_id, key), daemon=True)
        thread.start()

    def _run_ai_test_worker(self, provider_id: str, key: str):
        result = api_tester.test_ai_provider(provider_id, key)
        # Regresar al hilo principal de Tkinter
        self.after(0, self._handle_ai_test_result, result, key)

    def _handle_ai_test_result(self, result: dict, raw_key: str):
        self.testing_in_progress = False
        self.btn_test_ai.config(
            text="▶  PROBAR SI FUNCIONA LA API KEY",
            state="normal",
            bg=self.colors["accent"]
        )

        success = result.get("success", False)
        status_code = result.get("status_code")
        latency = result.get("latency_ms", 0)
        provider_name = result.get("provider_name", "API")
        msg = result.get("message", "")
        summary = result.get("summary", "")
        details = result.get("details")

        # Color según estado
        if success:
            bg_color = self.colors["success_bg"]
            fg_color = self.colors["success"]
            icon = "🟢"
            title = f"¡FUNCIONA! (API Key Válida y Activa)"
        elif result.get("is_quota_issue"):
            bg_color = self.colors["warning_bg"]
            fg_color = self.colors["warning"]
            icon = "🟡"
            title = "CLAVE VÁLIDA PERO SIN SALDO / RATE LIMIT"
        else:
            bg_color = self.colors["error_bg"]
            fg_color = self.colors["error"]
            icon = "🔴"
            title = "NO FUNCIONA (Inválida o Rechazada)"

        # Actualizar Banner
        self.status_banner.config(bg=bg_color)
        self.lbl_status_icon.config(text=icon, bg=bg_color)
        self.lbl_status_title.config(text=title, fg=fg_color, bg=bg_color)
        
        meta_info = f"Proveedor: {provider_name} | Código HTTP: {status_code or 'Sin respuesta'} | Latencia: {latency} ms"
        self.lbl_status_meta.config(text=meta_info, bg=bg_color)

        # Actualizar Detalles de texto
        self.txt_details.delete("1.0", tk.END)
        output_text = f"=== RESULTADO DE LA VERIFICACIÓN ===\n"
        output_text += f"Estado: {'VÁLIDA' if success else 'INVÁLIDA / ERROR'}\n"
        output_text += f"Proveedor: {provider_name}\n"
        output_text += f"Código HTTP: {status_code}\n"
        output_text += f"Tiempo de Respuesta: {latency} ms\n"
        output_text += f"Mensaje: {msg}\n"
        if summary:
            output_text += f"Diagnóstico: {summary}\n"
        
        output_text += f"\n=== RESPUESTA COMPLETA DEL SERVIDOR ===\n"
        if details:
            try:
                output_text += json.dumps(details, indent=2, ensure_ascii=False)
            except Exception:
                output_text += str(details)
        else:
            output_text += "(No se recibió cuerpo de respuesta)"

        self.txt_details.insert(tk.END, output_text)

        # Agregar a Historial
        masked_key = raw_key[:7] + "..." + raw_key[-4:] if len(raw_key) > 12 else raw_key[:3] + "..."
        hist_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "provider": provider_name,
            "key": masked_key,
            "status": "VÁLIDA (200)" if success else f"FALLÓ ({status_code or 'Error'})",
            "latency": f"{latency}ms",
            "success": success
        }
        self.history.insert(0, hist_entry)
        self.update_history_display()

    # -------------------------------------------------------------
    # PRUEBA REST
    # -------------------------------------------------------------
    def start_test_rest(self):
        url = self.rest_url_entry.get().strip()
        method = self.rest_method_var.get()
        auth_type = self.rest_auth_type_var.get()
        token = self.rest_token_entry.get().strip()

        # Parsear headers
        headers = {}
        headers_raw = self.txt_rest_headers.get("1.0", tk.END).strip()
        if headers_raw:
            try:
                headers = json.loads(headers_raw)
            except Exception:
                pass

        body = self.txt_rest_body.get("1.0", tk.END).strip()

        self.btn_send_rest.config(text="⏳ Enviando...", state="disabled")
        self.lbl_rest_status.config(text="Enviando petición HTTP...", fg=self.colors["warning"])

        def worker():
            res = api_tester.test_custom_rest_api(
                url=url,
                method=method,
                auth_type=auth_type,
                auth_token=token,
                custom_headers=headers,
                body=body
            )
            self.after(0, self._handle_rest_result, res)

        threading.Thread(target=worker, daemon=True).start()

    def _handle_rest_result(self, res: dict):
        self.btn_send_rest.config(text="▶  ENVIAR PETICIÓN REST", state="normal")
        success = res.get("success", False)
        code = res.get("status_code")
        latency = res.get("latency_ms", 0)

        color = self.colors["success"] if success else self.colors["error"]
        self.lbl_rest_status.config(text=f"Respuesta: HTTP {code} ({latency} ms)", fg=color)

        self.txt_rest_resp.delete("1.0", tk.END)
        details = res.get("details")
        text = f"Status: {code} | Tiempo: {latency} ms\n"
        if details:
            try:
                text += json.dumps(details, indent=2, ensure_ascii=False)
            except Exception:
                text += str(details)
        else:
            text += res.get("message", "")
        self.txt_rest_resp.insert(tk.END, text)

    # -------------------------------------------------------------
    # HISTORIAL Y UTILIDADES
    # -------------------------------------------------------------
    def update_history_display(self):
        self.txt_history.delete("1.0", tk.END)
        if not self.history:
            self.txt_history.insert(tk.END, "No hay pruebas registradas en esta sesión.\n")
            return

        header = f"{'HORA':<10} | {'PROVEEDOR':<20} | {'ESTADO':<18} | {'LATENCIA':<10} | {'KEY'}\n"
        self.txt_history.insert(tk.END, header)
        self.txt_history.insert(tk.END, "-" * 75 + "\n")

        for item in self.history:
            icon = "🟢" if item["success"] else "🔴"
            line = f"{item['time']:<10} | {item['provider']:<20} | {icon} {item['status']:<15} | {item['latency']:<10} | {item['key']}\n"
            self.txt_history.insert(tk.END, line)

    def clear_history(self):
        self.history.clear()
        self.update_history_display()

    def copy_details_clipboard(self):
        details = self.txt_details.get("1.0", tk.END).strip()
        if details:
            self.clipboard_clear()
            self.clipboard_append(details)
            messagebox.showinfo("Copiado", "Detalles copiados al portapapeles correctamente.")


if __name__ == "__main__":
    app = ApiKeyTesterApp()
    app.mainloop()
