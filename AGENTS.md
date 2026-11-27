# AGENTS — Grupo04_Reservas

Reglas que cualquier persona o agente de código lee antes de tocar el repo.

## Cómo ejecutar (dentro del Codespace)

```bash
# 1. Contenedores (Codespaces ya los levanta al crearse; esto es por si n8n está detenido)
cd .devcontainer && docker compose up -d n8n && docker compose ps && cd ..

# 2. n8n: abrir SIEMPRE por la URL https del puerto 5678 en la pestaña PORTS.
#    Importar n8n/workflow.json -> reasignar credenciales -> Publish.

# 3. Verificar entorno y contrato
bash scripts/verificar_entorno.sh
python scripts/probar_contrato.py --mensaje "¿Hay mesa para 2 hoy a las 19:00?" --guardar-propuesta /tmp/propuesta.json

# 4. Interfaz (abrir por la URL https del puerto 8501 en PORTS)
pip install -r app/requirements.txt
streamlit run app/app.py
```

## Contrato (no romper)

- `POST http://n8n:5678/webhook/agente-reservas`, contrato v2 en dos pasos:
  - Conversar: `{"sessionId", "chatInput", "confirmado": false}` → `{"output", "propuesta", "evidencia"}`
  - Confirmar: `{"sessionId", "chatInput", "confirmado": true, "propuesta"}` → `{"output", "reserva"}`
- Detalle y errores: `skills/n8n-webhook-reservas/SKILL.md`.

## Reglas

1. `SPEC.md` manda. Si el código contradice al SPEC, se cambia el código.
2. Nada de secretos en el repo: claves de OpenRouter y Google solo en *Credentials* de n8n.
   URLs solo por variables de entorno (`app/.env.example`) o la barra lateral. `bash scripts/revisar_secretos.sh` debe decir OK.
3. El código dentro del Codespace usa `http://n8n:5678`, nunca `localhost:5678` ni la URL `https://...app.github.dev`.
4. Cliente delgado: validación, extracción y generación de archivos (PDF) en `app/`; n8n razona y persiste.
5. El agente solo lee. La escritura (Sheets, Calendar, Gmail) ocurre únicamente en la rama determinista de n8n,
   con confirmación explícita en la UI (`confirmado = true` + la `propuesta` recibida). Sin la casilla marcada
   no se envía ninguna petición con `confirmado = true`.
6. Una tarea de `TASKS.md` = un cambio. Se marca `[x]` solo con su evidencia en `evidencias/`.
7. Nadie hace commit directo a `main`: rama + pull request; el Integrante 1 fusiona. El check de secretos debe estar en verde.
8. Antes de exportar `n8n/workflow.json`: quitar *pinned data*.
9. Skills en `skills/*/SKILL.md` son el contexto reutilizable: citarlas, no duplicarlas.
