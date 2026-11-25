# Skill: google-calendar-n8n

Úsala cuando configures credenciales de Google en n8n o construyas la herramienta `crear_evento_calendar`.

## Decisiones del proyecto

- **Fuente de verdad:** Google Sheets (hoja Reservas). Calendar es el reflejo visible de cada reserva confirmada.
- **Calendario destino:** "Reservas Restaurante", zona horaria America/Bogota.
  Su ID (termina en `@group.calendar.google.com`) se pasa a n8n como variable `RESERVAS_CALENDAR_ID`
  y se usa en el nodo con la expresión `{{ $env.RESERVAS_CALENDAR_ID }}`. También se puede elegir de la lista del nodo.
- **Horario permitido:** eventos solo entre 14:00 y 23:00.
- **Duración por turno:** el evento dura 2 h desde la hora del turno (turno 20:00 → evento 20:00–22:00).
- **Orden de escritura** (solo con `confirmado = true`): `generar_codigo_reserva` → `crear_reserva` (Sheets) →
  `crear_evento_calendar` → guardar `event_id` en la fila → responder.
- **Antiduplicado:** si la fila de la reserva ya tiene `event_id`, no se crea otro evento.

## Fechas: siempre ISO 8601 con desfase de Colombia

```text
inicio: 2026-11-27T20:00:00-05:00
fin:    2026-11-27T22:00:00-05:00
```

Con el desfase explícito el evento queda bien aunque el servidor tenga otra zona horaria.
El contenedor n8n ya tiene `TZ` y `GENERIC_TIMEZONE` en America/Bogota (ver `.devcontainer/docker-compose.yml`).

## Credenciales en n8n (cada instancia de n8n crea las suyas)

1. *PORTS* → puerto 5678 → *Port Visibility* → **Public** (solo mientras se conecta OAuth).
2. *Credentials → Add Credential →* **Google Calendar OAuth2 API**. Copiar la *OAuth Redirect URL* y confirmar que
   está registrada en el cliente OAuth de Google Cloud (una URI por Codespace).
3. Pegar Client ID y Client Secret (los da el Integrante 1 por canal privado).
4. **Primero** *Sign in with Google* → aceptar → aviso verde *Account connected*. **Después** *Save*.
5. Repetir con **Google Sheets OAuth2 API**.

Proyecto de Google Cloud: APIs habilitadas Sheets, Drive y Calendar; público Externo; los tres integrantes
y la cuenta dueña como *usuarios de prueba*.

## Errores típicos

| Síntoma | Causa | Arreglo |
| --- | --- | --- |
| `redirect_uri_mismatch` | la URI de ese Codespace no está en el cliente OAuth | agregarla exacta en Google Cloud |
| `Error 403: access_denied` | el correo no es usuario de prueba | agregarlo en la pantalla de consentimiento |
| `404` al guardar la credencial | se guardó antes de iniciar sesión | iniciar sesión primero, guardar después |
| Funcionaba y dejó de funcionar | en modo *Testing* los tokens vencen a los 7 días | volver a pulsar *Sign in with Google* (hacerlo el día antes de la demo) |
| Evento 5 h corrido | fecha sin desfase o zona horaria faltante | usar `-05:00` y revisar `TZ` |
| `$env` no disponible en la expresión | acceso a variables bloqueado | `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` (ya en el compose) y recrear n8n |
| Calendar no aparece en la lista del nodo | el calendario no está compartido con la cuenta de la credencial | compartirlo con permiso "Hacer cambios en los eventos" |
