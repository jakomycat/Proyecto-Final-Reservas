# SPEC — Agente de reservas para restaurante (Grupo04_Reservas)

> Responsable: Integrante 3. El SPEC manda: si el código lo contradice, se cambia el código.
> Las secciones marcadas *(por completar)* las redacta el Integrante 3.

## 1. Objetivo
*(por completar: problema de negocio, usuarios afectados, qué decisión apoya el agente)*

## 2. Alcance

### 2.1 Qué hace el agente
*(por completar)*
- Consulta disponibilidad de mesas por fecha, turno y número de personas (lectura con grounding desde Google Sheets).
- Crea reservas en Sheets y su evento en Google Calendar, solo con confirmación explícita.
- *(…)*

### 2.2 Qué NO hace
*(por completar: ej. cancelar o modificar reservas, cobrar, reservar fuera de 14:00–23:00)*

## 3. Historias de usuario
*(por completar, formato: Como <rol> quiero <acción> para <beneficio>)*

## 4. Contratos

### 4.1 Contrato HTTP Streamlit → n8n (v2, en dos pasos)
Detalle, ejemplos y errores en `skills/n8n-webhook-reservas/SKILL.md`.

- `POST http://n8n:5678/webhook/agente-reservas`
- **Paso 1, conversar:** `{"sessionId": str, "chatInput": str, "confirmado": false}`
  → `{"output": str, "propuesta": obj|null, "evidencia": list}`
- **Paso 2, confirmar:** `{"sessionId": str, "chatInput": str, "confirmado": true, "propuesta": obj}`
  → `{"output": str, "reserva": obj}`, o solo `{"output": motivo}` si se rechaza
- `propuesta` = `{nombre, correo, personas, fecha "YYYY-MM-DD", hora "HH:mm", numero_mesa 1–5}`
- `reserva` = propuesta + `{codigo, estado, calendar_event_id, estado_calendar, estado_correo}`

### 4.2 Capacidades del agente y del workflow
| Capacidad | Nodo(s) | Tipo | Cuándo | Prohibido |
| --- | --- | --- | --- | --- |
| Consultar mesas | `Consultar_Mesas` (herramienta del agente) | lectura con grounding (Sheets) | siempre antes de ofrecer una mesa | concluir disponibilidad horaria solo con el estado; inventar mesas |
| Consultar reservas del día | `Consultar_Reservas` (herramienta del agente) | lectura con grounding (Sheets) | siempre antes de ofrecer una mesa; exige `fecha` | revelar datos de otros clientes; escribir |
| Validar y verificar disponibilidad | `Validar_Datos_Reserva`, `Verificar_Mesa`, `Verificar_Reservas`, `Comprobar_Disponibilidad` | utilidad determinista | solo con `confirmado = true` | aceptar fechas pasadas, fuera de 14:00–21:00 de inicio, o con choque de 2 h |
| Generar código | `Comprobar_Disponibilidad` | utilidad | al aprobar la verificación | — |
| Registrar reserva | `Registrar_Reserva`, `Actualizar_Reserva` | escritura controlada (Sheets) | solo tras verificación con `confirmado = true` | ejecutarse desde el agente |
| Crear evento | `Crear_Evento` | escritura controlada (Calendar) | tras registrar | usar un calendario distinto de `RESERVAS_CALENDAR_ID` |
| Enviar confirmación | `Enviar_Correo` | escritura controlada (Gmail) | tras crear el evento | enviar sin reserva registrada |

El agente **solo lee**; toda escritura ocurre en la rama determinista de confirmación.

### 4.3 Estructura de la hoja
Documento `Reservas_Restaurante_Plantilla_Automatizacion` (ver `skills/google-calendar-n8n/SKILL.md`):

- `Mesas`: `numero_mesa`, `capacidad`, `estado_mesa`
- `Reservas`: `codigo`, `nombre`, `correo`, `personas`, `fecha`, `hora`, `numero_mesa`, `estado`,
  `calendar_event_id`, `estado_calendar`, `estado_correo`, `session_id`
  (`fecha` y `hora` en formato *Texto sin formato*)

## 5. Criterios de aceptación (medibles: pasan o no pasan)
*(por completar)*
- [ ] Mismo `sessionId` en dos mensajes: el segundo usa información del primero; `sessionId` nuevo: no.
- [ ] Una petición con `propuesta` pero `confirmado = false` no crea fila, evento ni correo.
- [ ] Una confirmación válida crea 1 fila con código `RES-AAAAMMDD-n`, 1 evento a la hora correcta, envía 1 correo
      y guarda `calendar_event_id` en la fila; la respuesta trae `reserva`.
- [ ] Repetir la misma confirmación se rechaza ("La mesa ya tiene una reserva en ese horario.").
- [ ] La `evidencia` de la respuesta no contiene nombres ni correos de otros clientes.
- [ ] `bash scripts/revisar_secretos.sh` imprime OK.
- [ ] *(…)*
