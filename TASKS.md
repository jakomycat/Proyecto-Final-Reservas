# TASKS — Grupo04_Reservas

Formato de cada tarea: **qué se hace**, **evidencia** (comando + salida o captura en `evidencias/`) y **commit**.
Una tarea = un cambio. Se marca `[x]` solo cuando su evidencia está en el repo.

Etapas: 1 Preparación · 2 Desarrollo inicial · 3 Desarrollo central · 4 Integración · 5 Verificación · 6 Entrega.

## Integrante 1 — Infraestructura e integración

- [ ] **I1-T1 Estructura del repo** (etapa 1). Carpetas del enunciado, `.devcontainer/`, `.gitignore`, esqueletos SDD, colaboradores.
      Evidencia: `tree -a -L 2 -I .git > evidencias/I1-T1_tree.txt`.
- [ ] **I1-T2 Codespace con 2 contenedores** (etapa 1). `dev` + `n8n` arriba.
      Evidencia: `docker compose -f .devcontainer/docker-compose.yml ps > evidencias/I1-T2_compose_ps.txt`.
- [ ] **I1-T3 Red interna** (etapa 2). Importar y publicar `n8n/pruebas/ping.json`.
      Evidencia: `bash scripts/verificar_entorno.sh > evidencias/I1-T3_verificar_entorno.txt 2>&1` (todo PASA salvo app.py).
- [ ] **I1-T4 Cero secretos** (etapa 2). `app/.env.example`, `.gitignore`, CI `revisar-secretos.yml`.
      Evidencia: `bash scripts/revisar_secretos.sh` → OK, y check verde en GitHub Actions.
- [ ] **I1-T5 Google Cloud y calendario** (etapa 3). APIs Sheets/Drive/Calendar, OAuth (Externo + usuarios de prueba),
      calendario "Reservas Restaurante" compartido. Evidencia: capturas `I1-T5_*.png` sin claves visibles.
- [ ] **I1-T6 Pruebas de humo Calendar y Sheets** (etapa 3). Credenciales conectadas en n8n; evento de prueba a la hora correcta.
      Evidencia: `I1-T6_evento_prueba.png`, `I1-T6_lectura_sheets.png`.
- [ ] **I1-T7 Integración** (etapa 4). `workflow.json` importado y publicado en el n8n de la demo; `app/` del Integrante 3 en el repo.
      Evidencia: `python scripts/probar_contrato.py --guardar evidencias/I1-T7_contrato.json` y `python -m py_compile app/app.py`.
- [ ] **I1-T8 Prueba punta a punta** (etapa 5). Memoria, consulta, escritura sin y con confirmación, sin duplicados, PDF.
      Evidencia: `python scripts/probar_contrato.py --memoria --guardar evidencias/I1-T8_memoria.json` + capturas `I1-T8_*.png`.
- [ ] **I1-T9 Repo final** (etapa 6). Estructura completa, `workflow.json` final sin pinned data, README, etiqueta `v1.0`.
      Evidencia: `bash scripts/verificar_entorno.sh` todo PASA, `git status` limpio.

## Integrante 2 — Workflow y agente en n8n
*(por completar: Sheets Mesas/Reservas, webhook + contrato, agente T = 0, memoria, 5 herramientas, publicación)*

## Integrante 3 — Interfaz, SDD y documentación
*(por completar: SPEC, app.py con chat/evidencia/confirmación/estados, comprobante PDF, matriz de pruebas, presentación)*
