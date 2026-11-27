# n8n

| Archivo | Qué es | Responsable |
| --- | --- | --- |
| `workflow.json` | Workflow del agente `WF_01_Agente_Reservas` (export de n8n). Lo evalúan. | Integrante 2 lo construye; Integrante 1 integra y exporta la versión final desde el n8n de la demo |
| `pruebas/ping.json` | Webhook mínimo para probar la red interna (`POST /webhook/ping`). | Integrante 1 |
| `pruebas/contrato_simulado.json` | Responde con el contrato v2 en `agente-reservas` **sin escribir nada**. Para desarrollar la UI sin el agente real. | Integrante 1 |

## Credenciales que pide `workflow.json`

| Credencial | Nodos |
| --- | --- |
| OpenRouter | `OpenRouter Chat Model` (modelo `nvidia/nemotron-3.5-super-vl:free`, temperatura 0) |
| Google Sheets OAuth2 API | `Consultar_Mesas`, `Consultar_Reservas`, `Verificar_Mesa`, `Verificar_Reservas`, `Registrar_Reserva`, `Actualizar_Reserva` |
| Google Calendar OAuth2 API | `Crear_Evento` (calendario de `RESERVAS_CALENDAR_ID`) |
| Gmail OAuth2 | `Enviar_Correo` |

Cómo crearlas: `skills/google-calendar-n8n/SKILL.md`.

## Importar

En n8n (abierto por la URL `https` de PORTS): *Workflows → … → Import from file*.

Por consola, desde la terminal del Codespace (el repo está montado en solo lectura en `/home/node/files`):

```bash
cd .devcontainer
docker compose exec n8n n8n import:workflow --input=/home/node/files/n8n/workflow.json
```

Después de importar:

1. **Desactiva `contrato_simulado`**: usa la misma ruta `agente-reservas`.
2. Abre el workflow y **reasigna tus credenciales en cada nodo** de la tabla de arriba (los IDs de credencial
   de otra instancia no existen en la tuya).
3. Comprueba que `RESERVAS_CALENDAR_ID` está definido:
   `docker compose -f .devcontainer/docker-compose.yml exec n8n printenv RESERVAS_CALENDAR_ID`.
4. *Publish*.

## Prueba punta a punta

Desde la terminal del Codespace, con el workflow real publicado:

```bash
S=demo-$(date +%H%M)
# 1. Conversar hasta que llegue una propuesta (repetir con el mismo --session-id si pide datos)
python scripts/probar_contrato.py --session-id $S \
  --mensaje "Mesa para 2 el próximo viernes a las 19:00. Soy Ana Pérez, ana@ejemplo.com" \
  --guardar-propuesta /tmp/propuesta.json --guardar evidencias/I1-T8_1_propuesta.json
# 2. Enviar la propuesta SIN confirmar: no debe aparecer fila nueva en la hoja
python scripts/probar_contrato.py --session-id $S --propuesta /tmp/propuesta.json \
  --guardar evidencias/I1-T8_2_sin_confirmar.json
# 3. Confirmar: fila en Reservas, evento en el calendario, correo y calendar_event_id en la fila
python scripts/probar_contrato.py --session-id $S --propuesta /tmp/propuesta.json --confirmado \
  --guardar evidencias/I1-T8_3_confirmada.json
# 4. Repetir la confirmación: debe rechazarse (antiduplicado)
python scripts/probar_contrato.py --session-id $S --propuesta /tmp/propuesta.json --confirmado \
  --guardar evidencias/I1-T8_4_duplicada.json
```

Usa un correo de prueba real tuyo en el paso 1 para comprobar que llega la confirmación.

## Exportar (antes de cada pull request del workflow)

1. Quita los *pinned data* de todos los nodos (pueden contener nombres o correos reales).
2. *… → Download* y guarda como `n8n/workflow.json`.
3. `bash scripts/revisar_secretos.sh` debe decir OK.
4. Commit en tu rama y pull request.

El export no incluye claves, solo el nombre e ID de cada credencial.
