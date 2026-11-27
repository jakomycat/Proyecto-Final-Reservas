"""Prueba el contrato HTTP del agente de reservas sin interfaz (contrato v2).

Contrato (detalle en skills/n8n-webhook-reservas/SKILL.md):
    POST {N8N_CHAT_URL}
    Paso 1: {"sessionId", "chatInput", "confirmado": false}
            -> {"output", "propuesta": {...}|null, "evidencia": [...]}
    Paso 2: {"sessionId", "chatInput", "confirmado": true, "propuesta": {...}}
            -> {"output", "reserva": {...}}   (o solo {"output": motivo} si se rechaza)

Ejemplos (dentro del Codespace):
    # Conversar y guardar la propuesta cuando llegue
    python scripts/probar_contrato.py --session-id demo-01 \
        --mensaje "Mesa para 2 el viernes a las 19:00, soy Ana, ana@ejemplo.com" \
        --guardar-propuesta /tmp/propuesta.json

    # Intentar escribir SIN confirmar (no debe registrar nada)
    python scripts/probar_contrato.py --session-id demo-01 --propuesta /tmp/propuesta.json

    # Confirmar (registra en Sheets, Calendar y Gmail)
    python scripts/probar_contrato.py --session-id demo-01 --propuesta /tmp/propuesta.json --confirmado \
        --guardar evidencias/I1-T8_confirmacion.json

    # Memoria: 2 turnos misma sesion + 1 turno sesion nueva
    python scripts/probar_contrato.py --memoria
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime

import requests

URL_POR_DEFECTO = "http://n8n:5678/webhook/agente-reservas"


def normalizar(datos):
    """Devuelve la respuesta como dict aceptando {..} o [{..}]."""
    if isinstance(datos, list):
        return datos[0] if datos and isinstance(datos[0], dict) else {}
    return datos if isinstance(datos, dict) else {}


def diagnostico(codigo: int, url: str) -> str:
    if codigo == 404:
        if "/webhook-test/" in url:
            return "Usas /webhook-test/: esa URL solo escucha con 'Execute workflow' abierto. Usa /webhook/."
        return "Workflow no publicado o 'path' distinto al del contrato. Publícalo en n8n y revisa el path."
    if codigo == 401:
        return ("Usaste la URL https://...app.github.dev desde dentro del Codespace. "
                "El código interno usa http://n8n:5678.")
    if codigo >= 500:
        return "Error dentro del workflow (credencial vencida, hoja no compartida...): revisa Executions en n8n."
    return ""


def cargar_propuesta(valor: str) -> dict:
    """Acepta una ruta a un .json o el JSON directamente."""
    texto = open(valor, encoding="utf-8").read() if os.path.isfile(valor) else valor
    propuesta = json.loads(texto)
    if not isinstance(propuesta, dict):
        raise ValueError("la propuesta debe ser un objeto JSON")
    return propuesta


def enviar(url, session_id, mensaje, confirmado, timeout, propuesta=None) -> dict:
    cuerpo = {"sessionId": session_id, "chatInput": mensaje, "confirmado": confirmado}
    if propuesta is not None:
        cuerpo["propuesta"] = propuesta
    inicio = time.perf_counter()
    try:
        r = requests.post(url, json=cuerpo, timeout=timeout)
    except requests.exceptions.ConnectionError:
        consejo = ("Desde el Codespace usa http://n8n:5678 (no localhost)."
                   if "localhost" in url else "¿n8n está arriba? docker compose ps")
        return {"ok": False, "peticion": cuerpo, "error": f"Sin conexión con {url}. {consejo}"}
    except requests.exceptions.Timeout:
        return {"ok": False, "peticion": cuerpo,
                "error": f"Sin respuesta en {timeout} s. Revisa Executions en n8n o el modelo."}
    segundos = round(time.perf_counter() - inicio, 2)

    try:
        crudo = r.json()
    except ValueError:
        crudo = r.text
    datos = normalizar(crudo)

    resultado = {
        "ok": r.status_code == 200 and isinstance(datos.get("output"), str),
        "peticion": cuerpo,
        "status": r.status_code,
        "segundos": segundos,
        "respuesta_cruda": crudo,
        "output": datos.get("output"),
        "propuesta": datos.get("propuesta"),
        "evidencia": datos.get("evidencia"),
        "reserva": datos.get("reserva"),
    }
    if r.status_code != 200:
        resultado["error"] = diagnostico(r.status_code, url)
    elif resultado["output"] is None:
        resultado["error"] = "Respuesta 200 sin campo 'output': el contrato no se cumple."
    return resultado


def imprimir(res: dict) -> None:
    p = res["peticion"]
    print(f"> chatInput:  {p['chatInput']}")
    extra = "  + propuesta" if "propuesta" in p else ""
    print(f"  sessionId:  {p['sessionId']}  confirmado: {p['confirmado']}{extra}")
    if "status" in res:
        print(f"  Status: {res['status']}  ({res['segundos']} s)")
    if res.get("output") is not None:
        print(f"< output: {res['output']}")
    if res.get("propuesta"):
        print(f"< propuesta: {json.dumps(res['propuesta'], ensure_ascii=False)}")
    if res.get("evidencia"):
        herramientas = ", ".join(str(e.get("herramienta")) for e in res["evidencia"])
        print(f"< evidencia: {len(res['evidencia'])} llamada(s) a herramientas: {herramientas}")
    if res.get("reserva"):
        print(f"< reserva: {json.dumps(res['reserva'], ensure_ascii=False)}")
    if res.get("error"):
        print(f"! {res['error']}")
    print()


def main() -> int:
    p = argparse.ArgumentParser(description="Prueba el contrato HTTP del agente de reservas.")
    p.add_argument("--url", default=os.getenv("N8N_CHAT_URL", URL_POR_DEFECTO))
    p.add_argument("--session-id", default=f"prueba-{datetime.now():%H%M%S}")
    p.add_argument("--mensaje", default=None, help="texto del usuario")
    p.add_argument("--confirmado", action="store_true", help="envía confirmado=true")
    p.add_argument("--propuesta", help="ruta a un .json o JSON en línea con la propuesta a enviar")
    p.add_argument("--guardar-propuesta", help="si la respuesta trae propuesta, guardarla en esta ruta")
    p.add_argument("--memoria", action="store_true",
                   help="dos turnos con el mismo sessionId y uno con un sessionId nuevo")
    p.add_argument("--timeout", type=int, default=int(os.getenv("N8N_TIMEOUT_S", "120")))
    p.add_argument("--guardar", help="ruta .json donde guardar la evidencia")
    a = p.parse_args()

    propuesta = None
    if a.propuesta:
        try:
            propuesta = cargar_propuesta(a.propuesta)
        except (OSError, ValueError) as e:
            print(f"! Propuesta inválida: {e}")
            return 2

    mensaje = a.mensaje or ("Confirmo la reserva" if propuesta else "Hola, ¿qué horarios de reserva tienen?")
    print(f"URL: {a.url}\n")
    resultados = []

    if a.memoria:
        pasos = [
            (a.session_id, "Me llamo Valentina y somos 3 personas."),
            (a.session_id, "¿Cómo me llamo y cuántos somos?"),
            (a.session_id + "-nueva", "¿Cómo me llamo?"),
        ]
        for sid, msg in pasos:
            res = enviar(a.url, sid, msg, False, a.timeout)
            imprimir(res)
            resultados.append(res)
        print("Revisa a mano: el turno 2 debe recordar el nombre; el turno 3 (sesión nueva) no.")
    else:
        res = enviar(a.url, a.session_id, mensaje, a.confirmado, a.timeout, propuesta)
        imprimir(res)
        resultados.append(res)
        if propuesta is not None and not a.confirmado:
            print("Sin --confirmado: la respuesta NO debe traer 'reserva' y la hoja no debe cambiar.")
        if a.guardar_propuesta:
            if res.get("propuesta"):
                os.makedirs(os.path.dirname(a.guardar_propuesta) or ".", exist_ok=True)
                with open(a.guardar_propuesta, "w", encoding="utf-8") as f:
                    json.dump(res["propuesta"], f, ensure_ascii=False, indent=2)
                print(f"Propuesta guardada en {a.guardar_propuesta}")
            else:
                print("La respuesta no trae propuesta todavía: sigue conversando con el mismo --session-id.")

    if a.guardar:
        os.makedirs(os.path.dirname(a.guardar) or ".", exist_ok=True)
        with open(a.guardar, "w", encoding="utf-8") as f:
            json.dump({"fecha": datetime.now().isoformat(timespec="seconds"), "url": a.url,
                       "resultados": resultados}, f, ensure_ascii=False, indent=2)
        print(f"Evidencia guardada en {a.guardar}")

    return 0 if all(r["ok"] for r in resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
