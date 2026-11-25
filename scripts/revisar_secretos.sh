#!/usr/bin/env bash
# Busca claves y tokens en los archivos versionados por git.
# Salida vacía + "OK" = repo limpio. Lo usan verificar_entorno.sh y el CI.
#
# Uso:  bash scripts/revisar_secretos.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# Prefijos y claves reales:
#   sk-or-v1-          API key de OpenRouter
#   GOCSPX-            Client Secret de Google OAuth
#   ya29.              access token de Google
#   "client_secret":   JSON de credenciales descargado de Google Cloud
#   "refresh_token":   token OAuth exportado
#   "private_key":     JSON de cuenta de servicio
PATRON='sk-or-v1-|GOCSPX-|ya29\.[0-9A-Za-z_-]{20,}|"(client_secret|refresh_token|private_key)"[[:space:]]*:'

# --untracked: revisa también archivos nuevos aún sin commit (respeta .gitignore),
# así sirve ANTES de hacer commit. Este mismo archivo contiene los patrones:
# se excluye de la búsqueda.
if git grep --untracked -nIE "$PATRON" -- . ':(exclude)scripts/revisar_secretos.sh'; then
  echo
  echo "FALLO: hay posibles secretos en el repo (líneas de arriba)."
  echo "Quítalos, haz commit y REVOCA la clave en su servicio: borrarla del repo no basta."
  exit 1
fi

# Archivos .env versionados por error
if git ls-files | grep -E '(^|/)\.env$'; then
  echo "FALLO: hay un .env versionado. Usa: git rm --cached <ruta>"
  exit 1
fi

echo "OK: no se encontraron secretos en los archivos versionados."
