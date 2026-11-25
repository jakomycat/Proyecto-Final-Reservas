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
[n8n] Webhook → AI Agent (T = 0) + Memoria por sessionId + herramientas
          ├── Google Sheets   (fuente de verdad: Mesas, Reservas)
          ├── Google Calendar (calendario "Reservas Restaurante")
          └── OpenRouter      (modelo de lenguaje)
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

*(D5 en adelante, por completar: contrato, diseño del agente, herramientas, confirmación en dos capas, PDF en el cliente…)*

## 3. Contratos de las interfaces
Ver `SPEC.md` §4 y `skills/n8n-webhook-reservas/SKILL.md`.

## 4. Riesgos y mitigación
| Riesgo | Mitigación |
| --- | --- |
| El token OAuth de Google vence a los 7 días (app en modo *Testing*) | reconectar la credencial el día anterior a la demo |
| Se borra o recrea el Codespace del Integrante 1 (cambia la URL y se pierde `n8n_data`) | `n8n/workflow.json` siempre actualizado en el repo; registrar la nueva redirect URI |
| El modelo gratuito de OpenRouter falla o cambia | el modelo es un subnodo intercambiable; tener un segundo modelo `:free` anotado |
| *(por completar)* | *(…)* |
