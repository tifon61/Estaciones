"""
Descarga el archivo downld08.txt desde Nextcloud (WebDAV) y genera data.json
con las condiciones actuales + histórico, para que la página de GitHub Pages
lo consuma.

Variables de entorno necesarias (se configuran como "Secrets" en GitHub):
  NEXTCLOUD_USER  -> usuario de Nextcloud (ej: "meteo")
  NEXTCLOUD_PASS  -> contraseña de Nextcloud
  WEBDAV_URL      -> URL completa al archivo .txt vía WebDAV
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests

from parse_davis import parse_wlk_txt

# Cuántos registros históricos guardamos en data.json (para no crecer sin límite).
# Con lecturas cada 10 min, 30 días ≈ 4320 registros — dejamos margen para
# que la pestaña "Mes" de la página siempre tenga el mes completo.
MAX_HISTORY_RECORDS = 4500

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "docs", "data.json")


def fetch_remote_txt(url, user, password):
    response = requests.get(url, auth=(user, password), timeout=30)
    response.raise_for_status()
    return response.text


def build_payload(records):
    trimmed = records[-MAX_HISTORY_RECORDS:]
    current = trimmed[-1] if trimmed else None
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "current": current,
        "history": trimmed,
    }


def main():
    user = os.environ.get("NEXTCLOUD_USER")
    password = os.environ.get("NEXTCLOUD_PASS")
    url = os.environ.get("WEBDAV_URL")

    if not all([user, password, url]):
        print(
            "Faltan variables de entorno: NEXTCLOUD_USER, NEXTCLOUD_PASS, WEBDAV_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    raw_text = fetch_remote_txt(url, user, password)
    records = parse_wlk_txt(raw_text)

    if not records:
        print("No se encontraron registros en el archivo descargado.", file=sys.stderr)
        sys.exit(1)

    payload = build_payload(records)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(records)} registros procesados, {len(payload['history'])} guardados.")
    print(f"Último dato: {payload['current']}")


if __name__ == "__main__":
    main()
