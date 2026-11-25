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

### 4.1 Contrato HTTP Streamlit → n8n
Definido en `skills/n8n-webhook-reservas/SKILL.md` (estado: PROPUESTA hasta que el equipo lo apruebe).

- `POST http://n8n:5678/webhook/agente-reservas`
- Petición: `{"sessionId": str, "chatInput": str, "confirmado": bool}`
- Respuesta 200: `[{"output": str}]` o `{"output": str}`

### 4.2 Herramientas del agente
| Herramienta | Tipo | Cuándo se usa | Prohibido |
| --- | --- | --- | --- |
| `consultar_disponibilidad` | lectura (Sheets) | *(por completar)* | *(…)* |
| `crear_reserva` | escritura controlada (Sheets) | *(…)* | ejecutarse sin `confirmado = true` |
| `crear_evento_calendar` | escritura controlada (Calendar) | *(…)* | sin `confirmado = true`; fuera de 14:00–23:00; duplicar si ya hay `event_id` |
| `generar_codigo_reserva` | utilidad | *(…)* | *(…)* |
| `validar_fecha_turno` (opcional) | utilidad | *(…)* | *(…)* |

### 4.3 Estructura de la hoja
*(por completar con el Integrante 2: pestañas Mesas y Reservas, columnas)*

## 5. Criterios de aceptación (medibles: pasan o no pasan)
*(por completar)*
- [ ] Mismo `sessionId` en dos mensajes: el segundo usa información del primero; `sessionId` nuevo: no.
- [ ] Una petición de reserva con `confirmado = false` no crea fila ni evento.
- [ ] Una reserva con `confirmado = true` crea 1 fila con código `RES-XXXX`, 1 evento a la hora correcta y guarda su `event_id`.
- [ ] `bash scripts/revisar_secretos.sh` imprime OK.
- [ ] *(…)*
