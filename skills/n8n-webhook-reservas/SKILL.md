# Skill: n8n-webhook-reservas

Úsala cuando escribas o pruebes código que llama al agente de reservas (Streamlit, scripts, `curl`).

> **Estado del contrato:** PROPUESTA del Integrante 1. Cuando el equipo la apruebe,
> copiarla a `SPEC.md` (§ Contratos) y cambiar esta línea a "APROBADO <fecha>".
> Si el contrato cambia, se cambia aquí, en `SPEC.md` y en `scripts/probar_contrato.py` a la vez.

## Contrato

- `POST {N8N_CHAT_URL}` con `Content-Type: application/json`, timeout 120 s.
- URL interna (dentro del Codespace): `http://n8n:5678/webhook/agente-reservas`.

**Petición**

```json
{
  "sessionId": "cliente-ana-01",
  "chatInput": "¿Tienen mesa para 4 el viernes a las 20:00?",
  "confirmado": false
}
```

| Campo | Tipo | Regla |
| --- | --- | --- |
| `sessionId` | texto | estable por conversación; cambiarlo = conversación nueva (memoria de n8n) |
| `chatInput` | texto | mensaje del usuario, no vacío |
| `confirmado` | booleano | `true` solo cuando el usuario marcó la confirmación explícita en la UI; sin él nunca se escribe en Sheets ni en Calendar |

**Respuesta 200**: `[{"output": "..."}]` o `{"output": "..."}`. El cliente acepta las dos formas.
Si el Integrante 2 activa *Return Intermediate Steps* en el AI Agent, llega además
`intermediateSteps` (llamadas a herramientas y sus resultados): eso es lo que muestra el panel de evidencia.

## Ejemplos de respuesta (para maquetar la UI sin n8n)

Consulta (lectura con grounding):

```json
[{"output": "Para el viernes 27 a las 20:00 hay 2 mesas libres para 4 personas: Mesa 2 (interior) y Mesa 5 (terraza). ¿Desea reservar alguna?"}]
```

Escritura pedida sin confirmación (no debe escribir nada):

```json
[{"output": "Puedo reservar la Mesa 2 el viernes 27 a las 20:00 para 4 personas a nombre de Ana. Para registrarla necesito su confirmación explícita."}]
```

Escritura confirmada:

```json
[{"output": "Reserva RES-A7X9 confirmada: Mesa 2, viernes 27 a las 20:00, 4 personas, a nombre de Ana. Evento creado en el calendario."}]
```

## Parseo mínimo (Python)

```python
datos = r.json()
texto = datos[0]["output"] if isinstance(datos, list) else datos.get("output")
```

Implementación completa con diagnóstico de errores: `scripts/probar_contrato.py`.

## Errores típicos

| Síntoma | Causa | Arreglo |
| --- | --- | --- |
| `404` | workflow sin publicar, `/webhook-test/` en vez de `/webhook/`, o `path` distinto | publicar, usar `/webhook/`, revisar `path` |
| `401` con cuerpo vacío | URL `https://...app.github.dev` usada desde dentro del Codespace | usar `http://n8n:5678` |
| `Connection refused` en `localhost:5678` | con docker-outside-of-docker cada contenedor tiene su `localhost` | usar el nombre del servicio `n8n` |
| Respuesta doble | dos workflows activos con el mismo `path` | desactivar el viejo |
| Desde un PC fuera del Codespace no conecta | puerto 5678 en *Private* o Codespace detenido | encender el Codespace y poner 5678 en *Public*; usar la URL `https` |
