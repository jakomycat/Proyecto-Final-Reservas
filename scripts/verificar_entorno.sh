#!/usr/bin/env bash
# Verificación rápida del entorno del Codespace (Integrante 1).
# Corre desde la raíz del repo, dentro del Codespace:
#   bash scripts/verificar_entorno.sh
# Guardar como evidencia:
#   bash scripts/verificar_entorno.sh > evidencias/I1-T3_verificar_entorno.txt 2>&1
set -uo pipefail

cd "$(git rev-parse --show-toplevel)" || exit 1

N8N_BASE="${N8N_BASE:-http://n8n:5678}"
PASA=0
FALLA=0

ok()    { echo "  [PASA]  $1"; PASA=$((PASA + 1)); }
falla() { echo "  [FALLA] $1"; echo "          -> $2"; FALLA=$((FALLA + 1)); }

echo "== Verificación del entorno ($(date '+%Y-%m-%d %H:%M:%S %Z')) =="

# 1. Docker disponible dentro del contenedor dev
if command -v docker >/dev/null 2>&1; then
  ok "comando docker disponible"
else
  falla "comando docker disponible" "Rebuild Container (feature docker-outside-of-docker)"
fi

# 2. Contenedor n8n arriba
if docker compose -f .devcontainer/docker-compose.yml ps --status running --services 2>/dev/null | grep -qx n8n; then
  ok "contenedor n8n en ejecución"
else
  falla "contenedor n8n en ejecución" "cd .devcontainer && docker compose up -d n8n"
fi

# 3. n8n responde por la red interna
if curl -s -o /dev/null --max-time 10 "$N8N_BASE/healthz"; then
  ok "n8n alcanzable en $N8N_BASE (red interna)"
else
  falla "n8n alcanzable en $N8N_BASE" "usa el nombre del servicio (n8n), no localhost; revisa docker compose ps"
fi

# 4. Webhook de prueba publicado (workflow n8n/pruebas/ping.json)
CODIGO=$(curl -s -o /tmp/ping_resp.txt -w '%{http_code}' --max-time 10 \
  -X POST "$N8N_BASE/webhook/ping" -H 'Content-Type: application/json' -d '{"prueba": true}')
if [ "$CODIGO" = "200" ]; then
  ok "webhook /webhook/ping responde 200: $(cat /tmp/ping_resp.txt)"
else
  falla "webhook /webhook/ping (HTTP $CODIGO)" "importa n8n/pruebas/ping.json en n8n y publícalo (404 = no publicado)"
fi

# 5. Dependencias de la app instaladas
if python -c "import streamlit, requests, fpdf" 2>/dev/null; then
  ok "dependencias de app/requirements.txt instaladas"
else
  falla "dependencias de la app" "pip install -r app/requirements.txt"
fi

# 6. app.py compila (si ya existe)
if [ -f app/app.py ]; then
  if python -m py_compile app/app.py; then
    ok "app/app.py compila"
  else
    falla "app/app.py compila" "error de sintaxis arriba"
  fi
else
  echo "  [--]    app/app.py aún no existe (lo entrega el Integrante 3)"
fi

# 7. Sin secretos en el repo
if bash scripts/revisar_secretos.sh >/tmp/secretos.txt 2>&1; then
  ok "sin secretos en archivos versionados"
else
  falla "sin secretos en archivos versionados" "ver: bash scripts/revisar_secretos.sh"
fi

echo "== Resultado: $PASA pasan, $FALLA fallan =="
[ "$FALLA" -eq 0 ]
