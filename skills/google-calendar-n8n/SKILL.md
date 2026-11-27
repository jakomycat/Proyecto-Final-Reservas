# Skill: google-calendar-n8n

Úsala cuando configures credenciales de Google en n8n o toques los nodos de Sheets, Calendar o Gmail del workflow.

## Decisiones del proyecto

- **Fuente de verdad:** Google Sheets, documento `Reservas_Restaurante_Plantilla_Automatizacion`.
  Calendar y Gmail son el reflejo visible de cada reserva confirmada.
- **Calendario destino:** "Reservas Restaurante", zona horaria America/Bogota. El nodo `Crear_Evento` lo toma de
  `{{ $env.RESERVAS_CALENDAR_ID }}` (el ID termina en `@group.calendar.google.com`), nunca de un calendario personal.
- **Horario:** una reserva puede empezar entre 14:00 y 21:00 (dura 2 h y el servicio termina a las 23:00).
- **Código de reserva:** `RES-<AAAAMMDD>-<id de ejecución de n8n>`, por ejemplo `RES-20261204-57`.
- **Orden de escritura** (solo en la rama `confirmado = true`, sin LLM):
  `Registrar_Reserva` (fila nueva) → `Crear_Evento` → `Enviar_Correo` → `Actualizar_Reserva`
  (guarda `calendar_event_id`, `estado_calendar`, `estado_correo` buscando la fila por `codigo`).
- **Tolerancia a fallos:** `Crear_Evento`, `Enviar_Correo` y `Actualizar_Reserva` siguen aunque fallen
  (*On Error → Continue*). La reserva ya quedó en Sheets y la fila registra `Error` en el estado correspondiente.
- **Antiduplicado:** antes de registrar, `Comprobar_Disponibilidad` relee las reservas del día; una segunda
  confirmación de lo mismo choca con la primera y se rechaza.

## Estructura de la hoja

| Pestaña | Columnas |
| --- | --- |
| `Mesas` | `numero_mesa`, `capacidad`, `estado_mesa` (`Disponible` u otro) |
| `Reservas` | `codigo`, `nombre`, `correo`, `personas`, `fecha`, `hora`, `numero_mesa`, `estado`, `calendar_event_id`, `estado_calendar`, `estado_correo`, `session_id` |

**Importante:** las columnas `fecha` y `hora` de `Reservas` deben tener formato **Texto sin formato**
(*Formato → Número → Texto sin formato*). Si Sheets las convierte a fecha u hora:
- el filtro por `fecha` no encuentra las reservas del día y una mesa ocupada parece libre;
- `hora` llega como `7:00 p. m.` y la verificación rechaza todo.

## Fechas: siempre ISO 8601 con desfase de Colombia

```text
inicio: 2026-12-04T19:00:00-05:00
fin:    2026-12-04T21:00:00-05:00
```

Con el desfase explícito el evento queda bien aunque el servidor tenga otra zona horaria.
El contenedor n8n ya tiene `TZ` y `GENERIC_TIMEZONE` en America/Bogota (`.devcontainer/docker-compose.yml`).

## Credenciales en n8n (cada instancia crea las suyas)

| Credencial | Nodos |
| --- | --- |
| OpenRouter | `OpenRouter Chat Model` (modelo `:free`, temperatura 0) |
| Google Sheets OAuth2 API | `Consultar_Mesas`, `Consultar_Reservas`, `Verificar_Mesa`, `Verificar_Reservas`, `Registrar_Reserva`, `Actualizar_Reserva` |
| Google Calendar OAuth2 API | `Crear_Evento` |
| Gmail OAuth2 | `Enviar_Correo` |

Pasos para cada credencial de Google:

1. *PORTS* → puerto 5678 → *Port Visibility* → **Public** (solo mientras se conecta OAuth).
2. *Credentials → Add Credential →* el tipo correspondiente. Copiar la *OAuth Redirect URL* y confirmar que
   está registrada en el cliente OAuth de Google Cloud (una URI por Codespace).
3. Pegar Client ID y Client Secret (los da el Integrante 1 por canal privado).
4. **Primero** *Sign in with Google* → aceptar → aviso verde *Account connected*. **Después** *Save*.

Proyecto de Google Cloud: APIs habilitadas **Sheets, Drive, Calendar y Gmail**; público Externo; los tres
integrantes y la cuenta dueña como *usuarios de prueba*. La cuenta con la que se conecta n8n debe tener
**acceso de edición a la hoja** y permiso *Hacer cambios en los eventos* en el calendario.

## Errores típicos

| Síntoma | Causa | Arreglo |
| --- | --- | --- |
| `redirect_uri_mismatch` | la URI de ese Codespace no está en el cliente OAuth | agregarla exacta en Google Cloud |
| `Error 403: access_denied` | el correo no es usuario de prueba | agregarlo en la pantalla de consentimiento |
| `404` al guardar la credencial | se guardó antes de iniciar sesión | iniciar sesión primero, guardar después |
| Funcionaba y dejó de funcionar | en modo *Testing* los tokens vencen a los 7 días | volver a pulsar *Sign in with Google* (hacerlo el día antes de la demo) |
| Los nodos de Sheets no encuentran el documento | la hoja no está compartida con la cuenta de la credencial | compartirla como editor |
| Evento 5 h corrido | fecha sin desfase o zona horaria faltante | usar `-05:00` y revisar `TZ` |
| `Crear_Evento` falla con "calendar not found" | `RESERVAS_CALENDAR_ID` vacío o sin permiso | definir la variable y recrear n8n; compartir el calendario |
| `$env` no disponible en la expresión | acceso a variables bloqueado | `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` (ya en el compose) y recrear n8n |
| Gmail: `insufficient permissions` | falta la Gmail API o el alcance de envío | habilitar Gmail API y reconectar la credencial |
