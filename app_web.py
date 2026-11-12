"""
Servidor Web Local para la interfaz de prueba de APIs.
Abre automáticamente el navegador en http://localhost:5000.
"""

import sys
import webbrowser
import threading
from flask import Flask, request, jsonify, render_template_string
import api_tester

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Probador de API Keys & REST APIs ⚡</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkbg: '#0f172a',
                        cardbg: '#1e293b',
                        borderbg: '#334155',
                        brand: '#38bdf8'
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0b0f19;
        }
        code, pre, .font-mono {
            font-family: 'JetBrains Mono', monospace;
        }
    </style>
</head>
<body class="text-slate-100 min-h-screen p-4 md:p-8 flex flex-col items-center">

    <!-- Contenedor Principal -->
    <div class="w-full max-w-4xl space-y-6">

        <!-- Header -->
        <header class="flex flex-col md:flex-row items-start md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
            <div>
                <div class="flex items-center gap-3">
                    <span class="text-3xl">⚡</span>
                    <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                        Probador de API Keys
                    </h1>
                </div>
                <p class="text-slate-400 text-sm mt-1">Verifica en 1 segundo si una API Key está activa, tiene saldo o si un endpoint REST responde.</p>
            </div>
            <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full text-xs text-slate-300">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Servidor Local Activo</span>
            </div>
        </header>

        <!-- Navegación por Pestañas -->
        <div class="flex border-b border-slate-800 gap-2">
            <button id="tab-btn-ai" onclick="switchTab('ai')" class="px-5 py-2.5 font-semibold text-sm border-b-2 border-sky-400 text-sky-400 flex items-center gap-2 transition">
                <span>🤖</span> Proveedores AI & Cloud
            </button>
            <button id="tab-btn-rest" onclick="switchTab('rest')" class="px-5 py-2.5 font-medium text-sm border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition">
                <span>🌐</span> REST API General
            </button>
            <button id="tab-btn-history" onclick="switchTab('history')" class="px-5 py-2.5 font-medium text-sm border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition">
                <span>📜</span> Historial (<span id="history-count">0</span>)
            </button>
        </div>

        <!-- CONTENIDO TAB 1: AI & CLOUD -->
        <div id="tab-ai" class="space-y-6">
            <!-- Card de Configuración -->
            <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-5">
                
                <!-- Selector de Proveedor -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Proveedor:</label>
                        <select id="ai-provider" onchange="onProviderChange()" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500 font-medium">
                            <option value="auto">🔍 Detección Automática (Recomendado)</option>
                            <option value="openai">🤖 OpenAI (ChatGPT, GPT-4o, etc.)</option>
                            <option value="gemini">✨ Google Gemini</option>
                            <option value="anthropic">🧠 Anthropic (Claude)</option>
                            <option value="groq">⚡ Groq</option>
                            <option value="deepseek">🐋 DeepSeek</option>
                            <option value="openrouter">🌐 OpenRouter</option>
                            <option value="mistral">🌪️ Mistral AI</option>
                            <option value="huggingface">🤗 Hugging Face</option>
                            <option value="github">🐙 GitHub Token / API</option>
                            <option value="elevenlabs">🎙️ ElevenLabs</option>
                            <option value="cohere">🔮 Cohere</option>
                            <option value="perplexity">🔍 Perplexity AI</option>
                        </select>
                    </div>

                    <div class="md:col-span-2">
                        <span class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Sugerencia de formato:</span>
                        <div id="provider-hint" class="text-xs text-sky-400/90 bg-sky-950/40 border border-sky-800/40 rounded-xl px-3 py-2.5 font-mono">
                            Pega cualquier clave: detectará OpenAI (sk-...), Gemini (AIza...), Claude (sk-ant-...), Groq (gsk_...), etc.
                        </div>
                    </div>
                </div>

                <!-- Input API Key -->
                <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">API Key a probar:</label>
                    <div class="relative flex items-center">
                        <input type="password" id="ai-key" oninput="onKeyInput()" placeholder="Pega tu clave aquí (ej: sk-proj-...)" 
                            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 pr-28 text-sm font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition">
                        
                        <div class="absolute right-2 flex items-center gap-1">
                            <button type="button" onclick="toggleKeyVisibility()" class="p-1.5 text-slate-400 hover:text-slate-200 transition text-sm" title="Ver / Ocultar">
                                <span id="eye-icon">👁️</span>
                            </button>
                            <button type="button" onclick="pasteKey()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 rounded-lg transition border border-slate-700 flex items-center gap-1">
                                📋 Pegar
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Botón de Probar -->
                <button type="button" id="btn-test-ai" onclick="runAiTest()" class="w-full py-3.5 px-6 rounded-xl font-bold text-slate-950 bg-gradient-to-r from-sky-400 to-blue-500 hover:from-sky-300 hover:to-blue-400 active:scale-[0.99] transition shadow-lg shadow-sky-500/20 flex items-center justify-center gap-2 text-base">
                    <span id="ai-btn-icon">▶</span>
                    <span id="ai-btn-text">PROBAR SI FUNCIONA LA API KEY</span>
                </button>
            </div>

            <!-- Card de Resultado -->
            <div id="ai-result-card" class="hidden rounded-2xl p-6 border shadow-2xl transition-all duration-300 space-y-4">
                <!-- Banner de Estado -->
                <div class="flex items-start md:items-center justify-between flex-col md:flex-row gap-3">
                    <div class="flex items-center gap-3">
                        <span id="res-badge-icon" class="text-3xl">🟢</span>
                        <div>
                            <h3 id="res-badge-title" class="text-xl font-bold">¡API Key VÁLIDA y ACTIVA!</h3>
                            <p id="res-badge-subtitle" class="text-xs text-slate-400 mt-0.5">Respuesta oficial del servidor</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-3 text-xs font-mono">
                        <span id="res-latency" class="bg-slate-950/70 border border-slate-800 px-3 py-1 rounded-lg text-slate-300">Latencia: 145 ms</span>
                        <span id="res-http-code" class="bg-slate-950/70 border border-slate-800 px-3 py-1 rounded-lg text-emerald-400">HTTP 200</span>
                    </div>
                </div>

                <!-- Resumen amigable -->
                <div id="res-summary-box" class="p-3.5 rounded-xl text-sm font-medium border">
                    Detalles del estado...
                </div>

                <!-- Detalles Técnicos / JSON -->
                <div>
                    <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
                        <span class="font-bold uppercase tracking-wider">Respuesta Completa del Servidor:</span>
                        <button onclick="copyToClipboard('res-json-code')" class="hover:text-slate-200 transition flex items-center gap-1">
                            📋 Copiar JSON
                        </button>
                    </div>
                    <pre class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-300 overflow-x-auto max-h-72"><code id="res-json-code">...</code></pre>
                </div>
            </div>
        </div>

        <!-- CONTENIDO TAB 2: REST API GENERAL -->
        <div id="tab-rest" class="hidden space-y-6">
            <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                
                <!-- URL y Método -->
                <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
                    <div class="md:col-span-1">
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Método:</label>
                        <select id="rest-method" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2.5 text-sm font-bold text-sky-400 focus:outline-none">
                            <option value="GET">GET</option>
                            <option value="POST">POST</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                            <option value="PATCH">PATCH</option>
                            <option value="HEAD">HEAD</option>
                        </select>
                    </div>
                    <div class="md:col-span-4">
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">URL Endpoint:</label>
                        <input type="text" id="rest-url" value="https://api.github.com/zen" placeholder="https://api.ejemplo.com/v1/ping"
                            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm font-mono text-slate-100 focus:outline-none focus:border-sky-500">
                    </div>
                </div>

                <!-- Autenticación -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Tipo de Auth:</label>
                        <select id="rest-auth-type" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none">
                            <option value="none">Sin autenticación</option>
                            <option value="bearer">Bearer Token (Authorization)</option>
                            <option value="header">Custom Header (x-api-key)</option>
                            <option value="query_param">Query Param (?api_key=...)</option>
                        </select>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Token / API Key:</label>
                        <input type="password" id="rest-token" placeholder="Token o clave..."
                            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm font-mono text-slate-100 focus:outline-none focus:border-sky-500">
                    </div>
                </div>

                <!-- Headers y Body -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Headers Adicionales (JSON):</label>
                        <textarea id="rest-headers" rows="3" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none">{\n  "Accept": "application/json"\n}</textarea>
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Request Body (JSON para POST/PUT):</label>
                        <textarea id="rest-body" rows="3" placeholder='{"mensaje": "hola"}' class="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none"></textarea>
                    </div>
                </div>

                <!-- Botón REST -->
                <button type="button" id="btn-test-rest" onclick="runRestTest()" class="w-full py-3 px-6 rounded-xl font-bold text-slate-950 bg-sky-400 hover:bg-sky-300 transition flex items-center justify-center gap-2">
                    <span>▶</span>
                    <span>ENVIAR PETICIÓN REST</span>
                </button>
            </div>

            <!-- Resultado REST -->
            <div id="rest-result-card" class="hidden rounded-2xl p-6 border border-slate-800 bg-slate-900/90 space-y-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span id="rest-status-badge" class="px-2.5 py-1 rounded-md text-xs font-bold">200 OK</span>
                        <span id="rest-latency-badge" class="text-xs text-slate-400 font-mono">120 ms</span>
                    </div>
                    <button onclick="copyToClipboard('rest-json-code')" class="text-xs text-slate-400 hover:text-slate-200 transition">📋 Copiar Respuesta</button>
                </div>
                <pre class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-300 overflow-x-auto max-h-80"><code id="rest-json-code">...</code></pre>
            </div>
        </div>

        <!-- CONTENIDO TAB 3: HISTORIAL -->
        <div id="tab-history" class="hidden space-y-4">
            <div class="flex items-center justify-between">
                <h3 class="text-sm font-bold uppercase tracking-wider text-slate-400">Historial de pruebas en esta sesión</h3>
                <button onclick="clearHistory()" class="px-3 py-1 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/50 text-rose-300 rounded-lg text-xs font-medium transition">
                    🗑️ Limpiar Historial
                </button>
            </div>
            <div id="history-list" class="space-y-2">
                <div class="p-8 text-center text-slate-500 text-sm bg-slate-900/50 rounded-2xl border border-slate-800">
                    Aún no has realizado ninguna prueba en esta sesión.
                </div>
            </div>
        </div>

    </div>

    <!-- Script de Frontend -->
    <script>
        const historyData = [];

        function switchTab(tab) {
            document.getElementById('tab-ai').classList.add('hidden');
            document.getElementById('tab-rest').classList.add('hidden');
            document.getElementById('tab-history').classList.add('hidden');

            const btnAi = document.getElementById('tab-btn-ai');
            const btnRest = document.getElementById('tab-btn-rest');
            const btnHist = document.getElementById('tab-btn-history');

            [btnAi, btnRest, btnHist].forEach(btn => {
                btn.className = "px-5 py-2.5 font-medium text-sm border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition";
            });

            if (tab === 'ai') {
                document.getElementById('tab-ai').classList.remove('hidden');
                btnAi.className = "px-5 py-2.5 font-semibold text-sm border-b-2 border-sky-400 text-sky-400 flex items-center gap-2 transition";
            } else if (tab === 'rest') {
                document.getElementById('tab-rest').classList.remove('hidden');
                btnRest.className = "px-5 py-2.5 font-semibold text-sm border-b-2 border-sky-400 text-sky-400 flex items-center gap-2 transition";
            } else if (tab === 'history') {
                document.getElementById('tab-history').classList.remove('hidden');
                btnHist.className = "px-5 py-2.5 font-semibold text-sm border-b-2 border-sky-400 text-sky-400 flex items-center gap-2 transition";
            }
        }

        function toggleKeyVisibility() {
            const input = document.getElementById('ai-key');
            const icon = document.getElementById('eye-icon');
            if (input.type === 'password') {
                input.type = 'text';
                icon.innerText = '🙈';
            } else {
                input.type = 'password';
                icon.innerText = '👁️';
            }
        }

        function cleanKey(val) {
            if (!val) return '';
            return val.trim().replace(/^["']+|["']+$/g, '').trim();
        }

        async function pasteKey() {
            try {
                const text = await navigator.clipboard.readText();
                if (text) {
                    document.getElementById('ai-key').value = cleanKey(text);
                    onKeyInput();
                }
            } catch (err) {
                alert('Por favor usa Ctrl+V para pegar en el campo.');
            }
        }

        function onProviderChange() {
            const val = document.getElementById('ai-provider').value;
            const hintBox = document.getElementById('provider-hint');
            const hints = {
                auto: "Detección Automática inteligente basada en el prefijo de tu clave.",
                openai: "Formato esperado: sk-... o sk-proj-... (OpenAI Platform)",
                gemini: "Formato esperado: AIzaSy... (Google AI Studio)",
                anthropic: "Formato esperado: sk-ant-... (Anthropic Console)",
                groq: "Formato esperado: gsk_... (Groq Console)",
                deepseek: "Formato esperado: sk-... (DeepSeek Platform)",
                openrouter: "Formato esperado: sk-or-... (OpenRouter)",
                mistral: "Formato alfanumérico estándar de Mistral AI",
                huggingface: "Formato esperado: hf_... (Hugging Face Tokens)",
                github: "Formato esperado: ghp_... o github_pat_... (GitHub PAT)",
                elevenlabs: "Formato esperado: 32 caracteres hexadecimales",
                cohere: "Formato alfanumérico estándar de Cohere",
                perplexity: "Formato esperado: pplx-... (Perplexity AI)"
            };
            hintBox.innerText = hints[val] || "Introduce tu clave para verificar.";
        }

        function onKeyInput() {
            const key = document.getElementById('ai-key').value.trim();
            const providerSelect = document.getElementById('ai-provider');
            if (providerSelect.value === 'auto' && key) {
                const hintBox = document.getElementById('provider-hint');
                if (key.startsWith('AIzaSy')) {
                    hintBox.innerText = "✨ Detectado: Google Gemini (AIzaSy...)";
                } else if (key.startsWith('sk-ant-')) {
                    hintBox.innerText = "🧠 Detectado: Anthropic Claude (sk-ant-...)";
                } else if (key.startsWith('gsk_')) {
                    hintBox.innerText = "⚡ Detectado: Groq (gsk_...)";
                } else if (key.startsWith('sk-or-')) {
                    hintBox.innerText = "🌐 Detectado: OpenRouter (sk-or-...)";
                } else if (key.startsWith('ghp_') || key.startsWith('github_pat_')) {
                    hintBox.innerText = "🐙 Detectado: GitHub Token";
                } else if (key.startsWith('hf_')) {
                    hintBox.innerText = "🤗 Detectado: Hugging Face Token";
                } else if (key.startsWith('pplx-')) {
                    hintBox.innerText = "🔍 Detectado: Perplexity AI";
                } else if (key.startsWith('sk-')) {
                    hintBox.innerText = "🤖 Detectado: OpenAI / DeepSeek (sk-...)";
                }
            }
        }

        async function runAiTest() {
            const rawInput = document.getElementById('ai-key').value;
            const key = cleanKey(rawInput);
            document.getElementById('ai-key').value = key;
            if (!key) {
                alert('Por favor ingresa una API Key para probar.');
                return;
            }

            const provider = document.getElementById('ai-provider').value;
            const btn = document.getElementById('btn-test-ai');
            const btnText = document.getElementById('ai-btn-text');
            const btnIcon = document.getElementById('ai-btn-icon');

            btn.disabled = true;
            btnText.innerText = "VERIFICANDO CON EL SERVIDOR OFICIAL...";
            btnIcon.innerText = "⏳";
            btn.classList.add('opacity-75');

            try {
                const response = await fetch('/api/test-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider, key })
                });

                const data = await response.json();
                renderAiResult(data, key);
                addHistory(data, key);
            } catch (error) {
                alert('Error al comunicar con el servidor local: ' + error.message);
            } finally {
                btn.disabled = false;
                btnText.innerText = "PROBAR SI FUNCIONA LA API KEY";
                btnIcon.innerText = "▶";
                btn.classList.remove('opacity-75');
            }
        }

        function renderAiResult(data, rawKey) {
            const card = document.getElementById('ai-result-card');
            card.classList.remove('hidden');

            const isSuccess = data.success;
            const isQuota = data.is_quota_issue;
            const icon = document.getElementById('res-badge-icon');
            const title = document.getElementById('res-badge-title');
            const subtitle = document.getElementById('res-badge-subtitle');
            const latency = document.getElementById('res-latency');
            const httpCode = document.getElementById('res-http-code');
            const summaryBox = document.getElementById('res-summary-box');
            const jsonCode = document.getElementById('res-json-code');

            latency.innerText = `Latencia: ${data.latency_ms} ms`;
            httpCode.innerText = `HTTP ${data.status_code || 'Error'}`;

            if (isSuccess) {
                card.className = "rounded-2xl p-6 border shadow-2xl space-y-4 bg-emerald-950/20 border-emerald-800/60";
                icon.innerText = "🟢";
                title.innerText = "¡API KEY VÁLIDA Y ACTIVA!";
                title.className = "text-xl font-bold text-emerald-400";
                subtitle.innerText = `${data.provider_name || 'API'} ha verificado exitosamente la clave.`;
                summaryBox.className = "p-3.5 rounded-xl text-sm font-medium border bg-emerald-900/30 border-emerald-700/50 text-emerald-200";
                httpCode.className = "bg-slate-950/70 border border-slate-800 px-3 py-1 rounded-lg text-emerald-400";
            } else if (isQuota) {
                card.className = "rounded-2xl p-6 border shadow-2xl space-y-4 bg-amber-950/20 border-amber-800/60";
                icon.innerText = "🟡";
                title.innerText = "CLAVE VÁLIDA PERO SIN CRÉDITOS / RATE LIMIT";
                title.className = "text-xl font-bold text-amber-400";
                subtitle.innerText = "La clave existe y es auténtica, pero no tiene saldo o excedió el límite de llamadas.";
                summaryBox.className = "p-3.5 rounded-xl text-sm font-medium border bg-amber-900/30 border-amber-700/50 text-amber-200";
                httpCode.className = "bg-slate-950/70 border border-slate-800 px-3 py-1 rounded-lg text-amber-400";
            } else {
                card.className = "rounded-2xl p-6 border shadow-2xl space-y-4 bg-rose-950/20 border-rose-800/60";
                icon.innerText = "🔴";
                title.innerText = "NO FUNCIONA (Inválida o Rechazada)";
                title.className = "text-xl font-bold text-rose-400";
                subtitle.innerText = data.message || "El servidor rechazó la autenticación.";
                summaryBox.className = "p-3.5 rounded-xl text-sm font-medium border bg-rose-900/30 border-rose-700/50 text-rose-200";
                httpCode.className = "bg-slate-950/70 border border-slate-800 px-3 py-1 rounded-lg text-rose-400";
            }

            summaryBox.innerText = data.summary || data.message || "Sin detalles adicionales.";
            jsonCode.innerText = JSON.stringify(data.details || data, null, 2);

            // Scroll suave al resultado
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        async function runRestTest() {
            const url = document.getElementById('rest-url').value.trim();
            const method = document.getElementById('rest-method').value;
            const auth_type = document.getElementById('rest-auth-type').value;
            const auth_token = document.getElementById('rest-token').value.trim();
            const headers_raw = document.getElementById('rest-headers').value.trim();
            const body = document.getElementById('rest-body').value.trim();

            let custom_headers = {};
            if (headers_raw) {
                try {
                    custom_headers = JSON.parse(headers_raw);
                } catch(e) {
                    alert('El campo Headers debe ser un JSON válido.');
                    return;
                }
            }

            const btn = document.getElementById('btn-test-rest');
            btn.disabled = true;
            btn.innerText = "ENVIANDO PETICIÓN...";

            try {
                const response = await fetch('/api/test-rest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, method, auth_type, auth_token, custom_headers, body })
                });
                const res = await response.json();

                const card = document.getElementById('rest-result-card');
                card.classList.remove('hidden');

                const statusBadge = document.getElementById('rest-status-badge');
                const latBadge = document.getElementById('rest-latency-badge');
                const codeBlock = document.getElementById('rest-json-code');

                statusBadge.innerText = `HTTP ${res.status_code || 'Error'}`;
                statusBadge.className = res.success ? "px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "px-2.5 py-1 rounded-md text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30";

                latBadge.innerText = `${res.latency_ms} ms`;
                codeBlock.innerText = JSON.stringify(res.details || res, null, 2);
            } catch (err) {
                alert('Error al probar REST: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = "ENVIAR PETICIÓN REST";
            }
        }

        function addHistory(data, rawKey) {
            const masked = rawKey.length > 12 ? rawKey.substring(0, 6) + "..." + rawKey.substring(rawKey.length - 4) : rawKey.substring(0, 3) + "...";
            const now = new Date().toLocaleTimeString();
            historyData.unshift({
                time: now,
                provider: data.provider_name || data.provider,
                maskedKey: masked,
                success: data.success,
                status: data.status_code || 'Error',
                latency: data.latency_ms
            });
            renderHistory();
        }

        function renderHistory() {
            document.getElementById('history-count').innerText = historyData.length;
            const container = document.getElementById('history-list');
            if (historyData.length === 0) {
                container.innerHTML = `<div class="p-8 text-center text-slate-500 text-sm bg-slate-900/50 rounded-2xl border border-slate-800">Aún no has realizado ninguna prueba en esta sesión.</div>`;
                return;
            }

            container.innerHTML = historyData.map(item => `
                <div class="flex items-center justify-between p-3.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono">
                    <div class="flex items-center gap-3">
                        <span class="text-base">${item.success ? '🟢' : '🔴'}</span>
                        <div>
                            <span class="font-bold text-slate-200">${item.provider}</span>
                            <span class="text-slate-500 ml-2">(${item.maskedKey})</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <span class="${item.success ? 'text-emerald-400' : 'text-rose-400'} font-bold">HTTP ${item.status}</span>
                        <span class="text-slate-400">${item.latency} ms</span>
                        <span class="text-slate-600">${item.time}</span>
                    </div>
                </div>
            `).join('');
        }

        function clearHistory() {
            historyData.length = 0;
            renderHistory();
        }

        function copyToClipboard(elementId) {
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text);
            alert('¡Copiado al portapapeles!');
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/test-key", methods=["POST"])
def api_test_key():
    data = request.get_json() or {}
    provider = data.get("provider", "auto")
    key = data.get("key", "").strip()
    result = api_tester.test_ai_provider(provider, key)
    return jsonify(result)

@app.route("/api/test-rest", methods=["POST"])
def api_test_rest():
    data = request.get_json() or {}
    result = api_tester.test_custom_rest_api(
        url=data.get("url", ""),
        method=data.get("method", "GET"),
        auth_type=data.get("auth_type", "none"),
        auth_token=data.get("auth_token", ""),
        custom_headers=data.get("custom_headers"),
        body=data.get("body")
    )
    return jsonify(result)

def open_browser():
    webbrowser.open_new("http://localhost:5000")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" ⚡ SERVIDOR DE PRUEBA DE API KEYS INICIADO")
    print(" Abriendo en el navegador: http://localhost:5000")
    print(" Presiona Ctrl+C en esta consola para detener el servidor")
    print("=" * 60 + "\n")
    
    # Abrir navegador en segundo plano tras 1 segundo
    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
