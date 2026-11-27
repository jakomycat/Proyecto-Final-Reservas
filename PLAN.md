# PLAN — Grupo04_Reservas

> §1 y las decisiones D1–D4 las escribió el Integrante 1 (infraestructura).
> El resto lo completa el Integrante 3 con el Integrante 2.

## 1. Arquitectura

```text
Navegador (PC)
  ├── https://<codespace>-8501.app.github.dev ──► [dev]  Streamlit (app/app.py)
  └── https://<codespace>-5678.app.github.dev ──► [n8n]  editor
                                                     ▲
[dev] Streamlit ── POST http://n8n:5678/webhook/agente-reservas ──┘
                                                     │
[n8n] Webhook → ¿confirmado?
        ├── no → AI Agent (T = 0, memoria por sessionId)
        │         herramientas de solo lectura: Consultar_Mesas, Consultar_Reservas (Google Sheets)
        │         → Estructurar_Propuesta → {output, propuesta, evidencia}
        └── sí → validar → reverificar en Sheets → Registrar (Sheets) → Evento (Google Calendar)
                 → Correo (Gmail) → Actualizar fila → {output, reserva}
      Modelo: OpenRouter (modelo :free)
```

Ambos contenedores están definidos en `.devcontainer/docker-compose.yml` y comparten la red de Compose.

## 2. Decisiones y justificación

**D1. Streamlit y n8n en el mismo Codespace, comunicados por `http://n8n:5678`.**
El enunciado exige que la interfaz invoque a n8n por la dirección interna. Con `docker-outside-of-docker` cada
contenedor tiene su propio `localhost`, así que se usa el nombre del servicio (DNS interno de Compose).
La URL `https://...app.github.dev` pasa por el proxy de Codespaces y desde el código devuelve 401.
*Descartado:* `localhost:5678` (no llega al contenedor n8n) y la URL pública (401, depende del nombre del Codespace).

**D2. n8n self-hosted con versión fijada, no `latest` ni n8n Cloud.**
Igual que en las Clases 10–11; fijar la versión evita que un `pull` antes de la demo cambie los nodos.
*Descartado:* n8n Cloud (cuenta y límites externos al curso).

**D3. Un n8n de producción: el del Codespace del Integrante 1.**
Cada Codespace tiene su propio volumen `n8n_data`; workflows y credenciales no se sincronizan.
El Integrante 2 desarrolla en su Codespace y entrega `n8n/workflow.json` por pull request;
el Integrante 1 lo importa, reasigna credenciales y publica.

**D4. Secretos solo en Credentials de n8n; URLs solo en variables de entorno o barra lateral.**
El repo lleva `app/.env.example` con nombres y valores internos. `scripts/revisar_secretos.sh` y el
workflow de GitHub Actions `revisar-secretos.yml` lo verifican en cada push.

**D5. El agente solo lee; la escritura es una rama determinista sin LLM.**
El agente conversa, consulta Sheets y devuelve una `propuesta`. Solo con `confirmado = true` (casilla explícita
en la UI) se ejecuta la rama de confirmación, que vuelve a validar los datos y la disponibilidad antes de escribir.
Así el modelo no puede registrar reservas por error ni inventar datos en la escritura, y la segunda verificación
evita duplicados (una confirmación repetida choca con la primera).
*Descartado:* herramientas de escritura dentro del agente (`crear_reserva` como `ai_tool`), como en la planeación
inicial: dependería de que el modelo respete la descripción para no escribir sin confirmación.

**D6. Evidencia de grounding saneada.**
Se activan los pasos intermedios del agente y `Estructurar_Propuesta` los devuelve como `evidencia`, pero solo con
columnas sin datos personales (mesa, capacidad, estado, fecha, hora). El panel de evidencia muestra el grounding
real sin exponer nombres ni correos de otros clientes.

**D7. Calendar y Gmail no bloquean la reserva.**
Sheets es la fuente de verdad: si Calendar o Gmail fallan, la reserva ya quedó registrada, el workflow continúa,
la fila guarda `Error` en `estado_calendar` o `estado_correo` y la respuesta lo dice con honestidad.

*(D8 en adelante, por completar: interfaz, PDF en el cliente…)*

## 3. Contratos de las interfaces
Ver `SPEC.md` §4 y `skills/n8n-webhook-reservas/SKILL.md`.

## 4. Riesgos y mitigación
| Riesgo | Mitigación |
| --- | --- |
| El token OAuth de Google vence a los 7 días (app en modo *Testing*) | reconectar la credencial el día anterior a la demo |
| Se borra o recrea el Codespace del Integrante 1 (cambia la URL y se pierde `n8n_data`) | `n8n/workflow.json` siempre actualizado en el repo; registrar la nueva redirect URI |
| El modelo gratuito de OpenRouter falla, cambia o no responde en JSON | el modelo es un subnodo intercambiable; tener un segundo modelo `:free` anotado; si no responde en JSON se muestra su texto sin propuesta (nunca se puede confirmar algo no validado) |
| Sheets convierte `fecha`/`hora` a formato fecha y el filtro no encuentra reservas | columnas en *Texto sin formato*; con hora mal formateada la verificación falla cerrada (rechaza) |
| Tras confirmar, la memoria del agente no sabe que la reserva se hizo | limitación conocida; la UI muestra la reserva confirmada. Trabajo futuro: escribir un resumen en la memoria |
| Dos workflows activos en `agente-reservas` (simulado y real) | desactivar `contrato_simulado` al importar el real (`n8n/README.md`) |
| *(por completar)* | *(…)* |
