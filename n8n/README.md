# n8n

| Archivo | Qué es | Responsable |
| --- | --- | --- |
| `workflow.json` | Workflow final del agente (export de n8n). Lo evalúan. | Integrante 2 lo construye; Integrante 1 exporta la versión final desde el n8n de la demo |
| `pruebas/ping.json` | Webhook mínimo para probar la red interna (`POST /webhook/ping`). No es parte del agente. | Integrante 1 |

## Importar

En n8n (abierto por la URL `https` de PORTS): *Workflows → … → Import from file*.

Por consola, desde la terminal del Codespace (el repo está montado en solo lectura en `/home/node/files`):

```bash
cd .devcontainer
docker compose exec n8n n8n import:workflow --input=/home/node/files/n8n/pruebas/ping.json
```

Después de importar: abrir el workflow, **reasignar las credenciales propias en cada nodo** (los IDs de credencial de otra instancia no existen en la tuya) y *Publish*. Desactiva cualquier otro workflow con el mismo `path`.

## Exportar (antes de cada pull request del workflow)

1. Quita los *pinned data* de todos los nodos (pueden contener nombres o correos reales).
2. *… → Download* y guarda como `n8n/workflow.json`.
3. `bash scripts/revisar_secretos.sh` debe decir OK.
4. Commit en tu rama y pull request.

El export no incluye claves, solo el nombre e ID de cada credencial.
