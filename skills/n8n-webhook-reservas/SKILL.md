# Skill: n8n-webhook-reservas

Úsala cuando escribas o pruebes código que llama al agente de reservas (Streamlit, scripts, `curl`).

> **Contrato v2** (alineado con `n8n/workflow.json`, PR #2 del Integrante 2 + correcciones de integración).
> Si cambia, se cambia a la vez aquí, en `SPEC.md` §4, en `scripts/probar_contrato.py`
> y en `n8n/pruebas/contrato_simulado.json`.

## Idea: dos pasos, y el modelo nunca escribe

1. **Conversar** (`confirmado: false`): el agente consulta Sheets y, cuando tiene todos los datos y una mesa
   libre, devuelve una `propuesta`. No escribe nada.
2. **Confirmar** (`confirmado: true` + la `propuesta`): una rama determinista de n8n, sin LLM, vuelve a validar
   los datos y la disponibilidad, y solo entonces registra en Sheets, crea el evento en Calendar y envía el correo.

- `POST {N8N_CHAT_URL}` con `Content-Type: application/json`, timeout 120 s.
- URL interna (dentro del Codespace): `http://n8n:5678/webhook/agente-reservas`.
- La respuesta llega como objeto `{...}`. Por robustez, el cliente acepta también una lista `[{...}]` y toma el primer elemento.

## Paso 1 — Conversar

**Petición**

```json
{ "sessionId": "cliente-ana-01", "chatInput": "Mesa para 2 el viernes a las 19:00", "confirmado": false }
```

**Respuesta**

```json
{
  "output": "Tengo la mesa 1 disponible. Nombre: Ana ... ¿Confirmas la reserva?",
  "propuesta": {
    "nombre": "Ana Pérez", "correo": "ana@ejemplo.com", "personas": 2,
    "fecha": "2026-12-04", "hora": "19:00", "numero_mesa": 1
  },
  "evidencia": [
    { "herramienta": "Consultar_Mesas", "entrada": null,
      "resultado": [{ "numero_mesa": 1, "capacidad": 2, "estado_mesa": "Disponible" }] },
    { "herramienta": "Consultar_Reservas", "entrada": { "fecha": "2026-12-04" },
      "resultado": [{ "numero_mesa": 3, "fecha": "2026-12-04", "hora": "20:00", "estado": "Confirmada" }] }
  ]
}
```

| Campo | Significado |
| --- | --- |
| `output` | texto para mostrar en el chat |
| `propuesta` | `null` mientras falten datos o no haya mesa; objeto completo cuando se puede confirmar |
| `evidencia` | llamadas a herramientas con su resultado, **sin datos personales** (solo mesa, capacidad, estado, fecha, hora). Es lo que muestra el panel de grounding |

## Paso 2 — Confirmar

Solo cuando la UI tiene una `propuesta` y el usuario marcó la confirmación explícita. Se reenvía **la misma**
`propuesta` (la UI puede mostrarla, pero no debe inventarla). `chatInput` es opcional en este paso.

**Petición**

```json
{
  "sessionId": "cliente-ana-01",
  "chatInput": "Confirmo la reserva",
  "confirmado": true,
  "propuesta": {
    "nombre": "Ana Pérez", "correo": "ana@ejemplo.com", "personas": 2,
    "fecha": "2026-12-04", "hora": "19:00", "numero_mesa": 1
  }
}
```

**Respuesta exitosa**

```json
{
  "output": "Tu reserva ha sido confirmada correctamente.\n\nCodigo: RES-20261204-57 ...",
  "reserva": {
    "codigo": "RES-20261204-57", "nombre": "Ana Pérez", "correo": "ana@ejemplo.com",
    "personas": 2, "fecha": "2026-12-04", "hora": "19:00", "numero_mesa": 1,
    "estado": "Confirmada", "calendar_event_id": "abc123xyz",
    "estado_calendar": "Creado", "estado_correo": "Enviado"
  }
}
```

`reserva` trae todo lo necesario para el **comprobante PDF**, que genera Streamlit (cliente delgado).
`estado_calendar` y `estado_correo` valen `"Error"` si Calendar o Gmail fallaron: la reserva sigue registrada en Sheets.

**Respuesta de rechazo**: solo `{"output": "<motivo>"}`, sin `reserva`. Motivos posibles:
`La reserva no fue confirmada.` · `Los datos de la reserva son invalidos.` ·
`La fecha u hora de la reserva no es valida.` · `La mesa ya tiene una reserva en ese horario.` ·
`Horario fuera del servicio del restaurante.` · `La mesa no esta disponible.` · `La mesa no tiene capacidad suficiente.`

Repetir la misma confirmación devuelve `La mesa ya tiene una reserva en ese horario.`: así se evitan duplicados.

## Reglas para el cliente

- `confirmado` debe ser **booleano JSON** (`true`), no el texto `"true"`.
- Sin la casilla de confirmación marcada en la UI no se envía ninguna petición con `confirmado: true`.
- Cambiar `sessionId` = conversación nueva (memoria de n8n de 15 mensajes).
- Después de confirmar, la memoria del agente no sabe que la reserva se hizo (la rama de confirmación no pasa por el agente).

## Parseo mínimo (Python)

```python
datos = r.json()
if isinstance(datos, list):
    datos = datos[0] if datos else {}
texto = datos.get("output")
propuesta = datos.get("propuesta")      # paso 1
evidencia = datos.get("evidencia", [])  # paso 1
reserva = datos.get("reserva")          # paso 2
```

Implementación completa con diagnóstico de errores: `scripts/probar_contrato.py`.

## Errores típicos

| Síntoma | Causa | Arreglo |
| --- | --- | --- |
| `404` | workflow sin publicar, `/webhook-test/` en vez de `/webhook/`, o `path` distinto | publicar, usar `/webhook/`, revisar `path` |
| `401` con cuerpo vacío | URL `https://...app.github.dev` usada desde dentro del Codespace | usar `http://n8n:5678` |
| `Connection refused` en `localhost:5678` | con docker-outside-of-docker cada contenedor tiene su `localhost` | usar el nombre del servicio `n8n` |
| Respuesta doble o inesperada | dos workflows activos con el mismo `path` (por ejemplo el simulado y el real) | desactivar el que sobra |
| `500` | error dentro del workflow (credencial vencida, hoja no compartida) | pestaña *Executions* de n8n |
| Desde un PC fuera del Codespace no conecta | puerto 5678 en *Private* o Codespace detenido | encender el Codespace y poner 5678 en *Public*; usar la URL `https` |
