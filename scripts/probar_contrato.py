"""Prueba el contrato HTTP del agente de reservas sin interfaz.

Equivale a Peticion.py de la Clase 10, adaptado al contrato del proyecto:
    POST {N8N_CHAT_URL}
    {"sessionId": "...", "chatInput": "...", "confirmado": false}
    -> [{"output": "..."}]  o  {"output": "..."}

Ejemplos (dentro del Codespace):
    python scripts/probar_contrato.py --mensaje "¿Hay mesa para 4 el viernes a las 20:00?"
    python scripts/probar_contrato.py --memoria
    python scripts/probar_contrato.py --mensaje "Confirmo la reserva" --confirmado \
        --session-id demo-01 --guardar evidencias/I1-T7_contrato.json
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


def extraer_output(datos):
    """Devuelve el texto del agente aceptando [{output}] o {output}."""
    if isinstance(datos, list) and datos and isinstance(datos[0], dict):
        return datos[0].get("output")
    if isinstance(datos, dict):
        return datos.get("output")
    return None


def diagnostico(codigo: int, url: str) -> str:
    if codigo == 404:
        if "/webhook-test/" in url:
            return "Usas /webhook-test/: esa URL solo escucha con 'Execute workflow' abierto. Usa /webhook/."
        return "Workflow no publicado o 'path' distinto al del contrato. Publícalo en n8n y revisa el path."
    if codigo == 401:
        return ("Usaste la URL https://...app.github.dev desde dentro del Codespace. "
                "El código interno usa http://n8n:5678.")
    if codigo >= 500:
        return "Error dentro del workflow: revisa la pestaña Executions de n8n."
    return ""


def enviar(url: str, session_id: str, mensaje: str, confirmado: bool, timeout: int) -> dict:
    cuerpo = {"sessionId": session_id, "chatInput": mensaje, "confirmado": confirmado}
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
        datos = r.json()
    except ValueError:
        datos = r.text

    resultado = {
        "ok": r.status_code == 200 and extraer_output(datos) is not None,
        "peticion": cuerpo,
        "status": r.status_code,
        "segundos": segundos,
        "respuesta_cruda": datos,
        "output": extraer_output(datos),
    }
    if r.status_code != 200:
        resultado["error"] = diagnostico(r.status_code, url)
    elif resultado["output"] is None:
        resultado["error"] = "Respuesta 200 sin campo 'output': el contrato no se cumple."
    return resultado


def imprimir(res: dict) -> None:
    print(f"> chatInput:  {res['peticion']['chatInput']}")
    print(f"  sessionId:  {res['peticion']['sessionId']}  confirmado: {res['peticion']['confirmado']}")
    if "status" in res:
        print(f"  Status: {res['status']}  ({res['segundos']} s)")
    if res.get("output") is not None:
        print(f"< output: {res['output']}")
    if res.get("error"):
        print(f"! {res['error']}")
    print()


def main() -> int:
    p = argparse.ArgumentParser(description="Prueba el contrato HTTP del agente de reservas.")
    p.add_argument("--url", default=os.getenv("N8N_CHAT_URL", URL_POR_DEFECTO))
    p.add_argument("--session-id", default=f"prueba-{datetime.now():%H%M%S}")
    p.add_argument("--mensaje", default="Hola, ¿qué horarios de reserva tienen?")
    p.add_argument("--confirmado", action="store_true", help="envía confirmado=true")
    p.add_argument("--memoria", action="store_true",
                   help="dos turnos con el mismo sessionId y uno con un sessionId nuevo")
    p.add_argument("--timeout", type=int, default=int(os.getenv("N8N_TIMEOUT_S", "120")))
    p.add_argument("--guardar", help="ruta .json donde guardar la evidencia")
    a = p.parse_args()

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
        res = enviar(a.url, a.session_id, a.mensaje, a.confirmado, a.timeout)
        imprimir(res)
        resultados.append(res)

    if a.guardar:
        os.makedirs(os.path.dirname(a.guardar) or ".", exist_ok=True)
        with open(a.guardar, "w", encoding="utf-8") as f:
            json.dump({"fecha": datetime.now().isoformat(timespec="seconds"), "url": a.url,
                       "resultados": resultados}, f, ensure_ascii=False, indent=2)
        print(f"Evidencia guardada en {a.guardar}")

    return 0 if all(r["ok"] for r in resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
