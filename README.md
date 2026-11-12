# ⚡ Probador de API Keys & REST APIs

Una aplicación mini GUI rápida, moderna y ligera para **probar si tus API Keys sirven o no en un solo clic**, verificar si tienen saldo o permisos activos, y probar cualquier endpoint REST.

---

## 🚀 Inicio Rápido (1 Clic)

Puedes iniciar la aplicación directamente haciendo **doble clic** en cualquiera de estos archivos:

- **`Ejecutar_Desktop.bat`**: Abre la ventana de escritorio nativa de Windows (sin necesidad de abrir navegador).
- **`Ejecutar_Web.bat`**: Abre la interfaz web moderna en tu navegador predeterminado (`http://localhost:5000`).
- **`iniciar.bat`**: Menú interactivo para elegir entre Escritorio o Web.

O desde la terminal:
```bash
# Iniciar modo Escritorio (Ventana nativa)
python main.py

# Iniciar modo Web (Navegador)
python main.py --web
```

---

## ✨ Características Principales

### 1. 🤖 Probador de API Keys de IA & Servicios Cloud
- **Detección Automática Inteligente**: Pega cualquier clave y el sistema detecta de inmediato qué proveedor es según su prefijo.
- **Proveedores Soportados de Fábrica**:
  - 🤖 **OpenAI** (ChatGPT, GPT-4o, etc. - Prefijo `sk-...`)
  - ✨ **Google Gemini** (Google AI Studio - Prefijo `AIzaSy...`)
  - 🧠 **Anthropic Claude** (Consola Anthropic - Prefijo `sk-ant-...`)
  - ⚡ **Groq** (GroqCloud - Prefijo `gsk_...`)
  - 🐋 **DeepSeek** (DeepSeek Platform)
  - 🌐 **OpenRouter** (Prefijo `sk-or-...`)
  - 🌪️ **Mistral AI**
  - 🤗 **Hugging Face** (Prefijo `hf_...`)
  - 🐙 **GitHub Token / PAT** (Prefijos `ghp_...`, `github_pat_...`)
  - 🎙️ **ElevenLabs**
  - 🔮 **Cohere**
  - 🔍 **Perplexity AI** (Prefijo `pplx-...`)
- **Diagnóstico Claro y Visual**:
  - 🟢 **¡VÁLIDA Y ACTIVA!**: Clave auténtica con acceso verificado y listado de modelos disponibles.
  - 🟡 **CUOTA AGOTADA / RATE LIMIT**: Clave auténtica pero sin saldo de crédito (HTTP 429).
  - 🔴 **INVÁLIDA O RECHAZADA**: Clave revocada, incorrecta o sin permisos (HTTP 401 / 403).
  - **Medición de Latencia en Tiempo Real**: Te muestra cuántos milisegundos tarda en responder el servidor oficial.
- **Seguridad y Privacidad**:
  - Botón de ojo `👁️` para ocultar o mostrar la clave.
  - Botón de pegar `📋` desde el portapapeles.
  - Tus claves solo se envían directamente a los servidores oficiales de cada proveedor, nunca a terceros.

### 2. 🌐 Probador REST API General (Mini-Postman)
- Prueba cualquier API o endpoint URL (`https://api.tu-servicio.com/...`).
- Métodos HTTP soportados: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`.
- Autenticación flexible:
  - Bearer Token (`Authorization: Bearer <token>`)
  - Header personalizado (ej: `x-api-key: ...`)
  - Query Parameter (ej: `?api_key=...`)
  - Sin autenticación
- Headers y Request Body personalizables en formato JSON.
- Visualización del código HTTP, tiempo de respuesta y cuerpo de la respuesta formateado.

### 3. 📜 Historial de Pruebas
- Registro de todas las pruebas realizadas en la sesión.
- Las claves se muestran enmascaradas (ej. `sk-proj-ab...9z1x`) para proteger tus credenciales.

---

## 📁 Estructura del Proyecto

```
ProvadorDeApi_KEY/
├── api_tester.py         # Motor de peticiones y validación de proveedores
├── gui.py                # Aplicación GUI de escritorio (Tkinter / Dark Theme)
├── app_web.py            # Servidor web local e interfaz web moderna
├── main.py               # Selector y ejecutor universal de Python
├── Ejecutar_Desktop.bat   # Acceso directo para escritorio
├── Ejecutar_Web.bat       # Acceso directo para web
├── iniciar.bat           # Menú interactivo de inicio
└── README.md             # Esta guía
```
