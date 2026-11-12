"""
Motor de verificación de APIs y API Keys.
Soporta proveedores populares de IA / Cloud y APIs REST genéricas.
"""

import time
import json
import requests
from typing import Dict, Any, Tuple, Optional


PROVIDERS = {
    "openai": {
        "name": "OpenAI (ChatGPT)",
        "url": "https://api.openai.com/v1/models",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "sk-...",
        "icon": "🤖"
    },
    "gemini": {
        "name": "Google Gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "method": "GET",
        "auth_type": "query_param",
        "query_param_name": "key",
        "prefix_hint": "AIzaSy...",
        "icon": "✨"
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "url": "https://api.anthropic.com/v1/models",
        "method": "GET",
        "auth_type": "header",
        "header_name": "x-api-key",
        "extra_headers": {"anthropic-version": "2023-06-01"},
        "prefix_hint": "sk-ant-...",
        "icon": "🧠"
    },
    "groq": {
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1/models",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "gsk_...",
        "icon": "⚡"
    },
    "deepseek": {
        "name": "DeepSeek",
        "url": "https://api.deepseek.com/models",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "sk-...",
        "icon": "🐋"
    },
    "openrouter": {
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/auth/key",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "sk-or-...",
        "icon": "🌐"
    },
    "mistral": {
        "name": "Mistral AI",
        "url": "https://api.mistral.ai/v1/models",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "...",
        "icon": "🌪️"
    },
    "huggingface": {
        "name": "Hugging Face",
        "url": "https://huggingface.co/api/whoami-v2",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "hf_...",
        "icon": "🤗"
    },
    "github": {
        "name": "GitHub Token / API",
        "url": "https://api.github.com/user",
        "method": "GET",
        "auth_type": "bearer",
        "extra_headers": {"User-Agent": "API-Key-Checker"},
        "prefix_hint": "ghp_... o github_pat_...",
        "icon": "🐙"
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "url": "https://api.elevenlabs.io/v1/user",
        "method": "GET",
        "auth_type": "header",
        "header_name": "xi-api-key",
        "prefix_hint": "32 caracteres hex",
        "icon": "🎙️"
    },
    "cohere": {
        "name": "Cohere",
        "url": "https://api.cohere.com/v1/models",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "...",
        "icon": "🔮"
    },
    "perplexity": {
        "name": "Perplexity AI",
        "url": "https://api.perplexity.ai/models",
        "method": "GET",
        "auth_type": "bearer",
        "prefix_hint": "pplx-...",
        "icon": "🔍"
    }
}


def clean_api_key(key: str) -> str:
    """Limpia la clave quitando espacios y comillas accidentales."""
    if not key:
        return ""
    return key.strip().strip("\"'").strip()


def detect_provider(key: str) -> str:
    """Detecta automáticamente el proveedor más probable a partir del formato de la clave."""
    key = clean_api_key(key)
    if not key:
        return "auto"
    
    if key.startswith("AIzaSy"):
        return "gemini"
    elif key.startswith("sk-ant-"):
        return "anthropic"
    elif key.startswith("gsk_"):
        return "groq"
    elif key.startswith("sk-or-"):
        return "openrouter"
    elif key.startswith("ghp_") or key.startswith("github_pat_"):
        return "github"
    elif key.startswith("hf_"):
        return "huggingface"
    elif key.startswith("pplx-"):
        return "perplexity"
    elif key.startswith("sk-"):
        # Podría ser OpenAI, DeepSeek o Mistral
        return "openai"
    elif len(key) == 32 and all(c in "0123456789abcdefABCDEF" for c in key):
        return "elevenlabs"
    
    return "openai"


def test_ai_provider(provider_id: str, api_key: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Prueba una API Key contra un proveedor específico.
    Devuelve un diccionario con el resultado detallado.
    """
    api_key = clean_api_key(api_key)
    if not api_key:
        return {
            "success": False,
            "status_code": None,
            "latency_ms": 0,
            "message": "Debes ingresar una API Key.",
            "details": None,
            "provider": provider_id
        }

    # Si se pasó auto, detectar
    if provider_id == "auto" or provider_id not in PROVIDERS:
        provider_id = detect_provider(api_key)

    cfg = PROVIDERS.get(provider_id)
    if not cfg:
        return {
            "success": False,
            "status_code": None,
            "latency_ms": 0,
            "message": f"Proveedor '{provider_id}' no reconocido.",
            "details": None,
            "provider": provider_id
        }

    url = cfg["url"]
    headers = {"Accept": "application/json"}
    if "extra_headers" in cfg:
        headers.update(cfg["extra_headers"])

    params = {}
    auth_type = cfg.get("auth_type", "bearer")

    if auth_type == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_type == "header":
        header_name = cfg.get("header_name", "x-api-key")
        headers[header_name] = api_key
    elif auth_type == "query_param":
        param_name = cfg.get("query_param_name", "key")
        params[param_name] = api_key

    start_time = time.time()
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout
        )
        latency_ms = int((time.time() - start_time) * 1000)
        status_code = response.status_code

        # Intentar parsear respuesta JSON
        try:
            body_json = response.json()
        except Exception:
            body_json = {"raw_text": response.text[:1000]}

        # Analizar según código HTTP
        if status_code in (200, 201):
            summary = _extract_provider_success_details(provider_id, body_json, response.headers)
            return {
                "success": True,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "message": f"¡API Key VÁLIDA y ACTIVA! ({cfg['name']})",
                "summary": summary,
                "details": body_json,
                "provider": provider_id,
                "provider_name": cfg["name"]
            }
        elif status_code == 401:
            err_msg = _extract_error_message(body_json) or "Clave no autorizada (401 Unauthorized). La clave es incorrecta o fue revocada."
            return {
                "success": False,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "message": "NO FUNCIONA: API Key inválida o revocada.",
                "summary": err_msg,
                "details": body_json,
                "provider": provider_id,
                "provider_name": cfg["name"]
            }
        elif status_code == 403:
            err_msg = _extract_error_message(body_json) or "Acceso prohibido (403 Forbidden). La clave puede ser válida pero carece de permisos o la API no está habilitada en tu consola."
            return {
                "success": False,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "message": "ACCESO DENEGADO (403): Permisos insuficientes o API no habilitada.",
                "summary": err_msg,
                "details": body_json,
                "provider": provider_id,
                "provider_name": cfg["name"]
            }
        elif status_code == 429:
            err_msg = _extract_error_message(body_json) or "Límite de tasa o cuota excedida (429 Too Many Requests)."
            return {
                "success": False,
                "is_quota_issue": True,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "message": "CUOTA AGOTADA / RATE LIMIT (429): La API Key es auténtica pero no tiene saldo o excedió el límite de peticiones.",
                "summary": err_msg,
                "details": body_json,
                "provider": provider_id,
                "provider_name": cfg["name"]
            }
        else:
            err_msg = _extract_error_message(body_json) or f"Código HTTP {status_code}"
            return {
                "success": False,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "message": f"Respuesta inesperada: Código HTTP {status_code}",
                "summary": err_msg,
                "details": body_json,
                "provider": provider_id,
                "provider_name": cfg["name"]
            }

    except requests.exceptions.Timeout:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "message": f"Tiempo de espera agotado ({timeout}s). Verifica tu conexión a Internet.",
            "summary": "Timeout al conectar con el servidor.",
            "details": None,
            "provider": provider_id,
            "provider_name": cfg["name"]
        }
    except requests.exceptions.ConnectionError as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "message": "Error de conexión de red. Comprueba tu acceso a internet.",
            "summary": str(e),
            "details": None,
            "provider": provider_id,
            "provider_name": cfg["name"]
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "message": f"Error inesperado: {str(e)}",
            "summary": str(e),
            "details": None,
            "provider": provider_id,
            "provider_name": cfg["name"]
        }


def _extract_error_message(data: Any) -> Optional[str]:
    """Extrae el mensaje de error legible de respuestas de APIs comunes."""
    if isinstance(data, dict):
        if "error" in data:
            err = data["error"]
            if isinstance(err, dict):
                return err.get("message") or err.get("code")
            elif isinstance(err, str):
                return err
        if "message" in data:
            return str(data["message"])
        if "detail" in data:
            return str(data["detail"])
    return None


def _extract_provider_success_details(provider_id: str, data: Any, headers: Any) -> str:
    """Extrae un resumen amigable con datos de la cuenta o modelos."""
    try:
        if provider_id == "openai":
            models = [m.get("id", "") for m in data.get("data", []) if isinstance(m, dict)]
            total = len(models)
            sample = ", ".join(models[:5])
            return f"✅ Acceso concedido a {total} modelos. Ejemplos disponibles: {sample}..."

        elif provider_id == "gemini":
            models = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
            total = len(models)
            sample = ", ".join(models[:4])
            return f"✅ Acceso concedido a {total} modelos Gemini. Disponibles: {sample}..."

        elif provider_id == "anthropic":
            models = [m.get("id", "") for m in data.get("data", []) if isinstance(m, dict)]
            total = len(models)
            sample = ", ".join(models[:4]) if models else "Modelos activos"
            return f"✅ Cuenta Anthropic Claude activa. {total} modelos disponibles ({sample})."

        elif provider_id == "groq":
            models = [m.get("id", "") for m in data.get("data", [])]
            total = len(models)
            sample = ", ".join(models[:4])
            return f"✅ Conexión Groq exitosa. {total} modelos disponibles ({sample})."

        elif provider_id == "deepseek":
            models = [m.get("id", "") for m in data.get("data", [])]
            return f"✅ Cuenta DeepSeek autenticada. Modelos: {', '.join(models) if models else 'Activo'}."

        elif provider_id == "openrouter":
            key_data = data.get("data", {})
            label = key_data.get("label", "Sin etiqueta")
            limit = key_data.get("limit")
            usage = key_data.get("usage", 0)
            is_free = key_data.get("is_free_tier", False)
            limit_str = f"${limit}" if limit is not None else "Ilimitado"
            return f"✅ OpenRouter Key válida | Nombre: '{label}' | Uso: ${usage:.2f} | Límite: {limit_str} | Tier gratuito: {is_free}"

        elif provider_id == "huggingface":
            user = data.get("name") or data.get("fullname") or "Usuario"
            email = data.get("email", "")
            auth_type = data.get("auth", {}).get("type", "Token")
            return f"✅ HuggingFace Token válido | Usuario: {user} ({email}) | Tipo: {auth_type}"

        elif provider_id == "github":
            user = data.get("login", "")
            name = data.get("name", "")
            scopes = headers.get("X-OAuth-Scopes", "Default scopes")
            plan = data.get("plan", {}).get("name", "Free")
            return f"✅ GitHub Token válido | Usuario: @{user} ({name}) | Plan: {plan} | Permisos: {scopes}"

        elif provider_id == "elevenlabs":
            tier = data.get("subscription", {}).get("tier", "Free")
            chars = data.get("subscription", {}).get("character_count", 0)
            max_chars = data.get("subscription", {}).get("character_limit", 0)
            return f"✅ ElevenLabs Key válida | Plan: {tier} | Caracteres usados: {chars}/{max_chars}"

        elif provider_id == "mistral":
            models = [m.get("id", "") for m in data.get("data", [])]
            return f"✅ Mistral Key válida. {len(models)} modelos disponibles."

        elif provider_id == "cohere":
            models = [m.get("name", "") for m in data.get("models", [])]
            return f"✅ Cohere Key válida. {len(models)} modelos disponibles."

        elif provider_id == "perplexity":
            return "✅ Perplexity API Key autenticada correctamente."

    except Exception:
        pass
    
    return "✅ Autenticación exitosa y respuesta 200 OK del servidor."


def test_custom_rest_api(
    url: str,
    method: str = "GET",
    auth_type: str = "none",
    auth_token: str = "",
    custom_header_name: str = "x-api-key",
    custom_param_name: str = "api_key",
    custom_headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Prueba cualquier endpoint REST API genérico.
    """
    url = url.strip()
    if not url:
        return {
            "success": False,
            "status_code": None,
            "latency_ms": 0,
            "message": "Debes especificar una URL válida (ej. https://api.ejemplo.com/v1/ping)",
            "details": None
        }

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    headers = {}
    if custom_headers:
        headers.update(custom_headers)

    params = {}
    auth_token = clean_api_key(auth_token)

    if auth_type == "bearer" and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    elif auth_type == "header" and auth_token:
        headers[custom_header_name or "x-api-key"] = auth_token
    elif auth_type == "query_param" and auth_token:
        params[custom_param_name or "api_key"] = auth_token

    # Procesar body si aplica
    data_payload = None
    json_payload = None
    if body and method.upper() in ("POST", "PUT", "PATCH"):
        body_trimmed = body.strip()
        if body_trimmed.startswith("{") or body_trimmed.startswith("["):
            try:
                json_payload = json.loads(body_trimmed)
                headers.setdefault("Content-Type", "application/json")
            except Exception:
                data_payload = body_trimmed
        else:
            data_payload = body_trimmed

    start_time = time.time()
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json_payload,
            data=data_payload,
            timeout=timeout
        )
        latency_ms = int((time.time() - start_time) * 1000)
        status_code = response.status_code

        try:
            body_json = response.json()
        except Exception:
            body_json = {"raw_text": response.text[:2000]}

        is_success = 200 <= status_code < 300

        return {
            "success": is_success,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "message": f"Respuesta HTTP {status_code} ({'ÉXITO' if is_success else 'FALLO'})",
            "summary": f"Estado: {status_code} {response.reason} | Tiempo: {latency_ms} ms",
            "response_headers": dict(response.headers),
            "details": body_json
        }

    except requests.exceptions.Timeout:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "message": f"Tiempo de espera agotado ({timeout}s).",
            "summary": "No se recibió respuesta en el tiempo límite.",
            "details": None
        }
    except requests.exceptions.ConnectionError as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "message": "Error de conexión (Host no encontrado o servidor caído).",
            "summary": str(e),
            "details": None
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "message": f"Error: {str(e)}",
            "summary": str(e),
            "details": None
        }
