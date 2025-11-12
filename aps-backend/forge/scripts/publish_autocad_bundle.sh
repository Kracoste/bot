#!/usr/bin/env bash

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq est requis pour parser le token APS." >&2
  exit 1
fi

if [[ -z "${APS_CLIENT_ID:-}" || -z "${APS_CLIENT_SECRET:-}" ]]; then
  echo "APS_CLIENT_ID et APS_CLIENT_SECRET doivent être définies dans l'environnement." >&2
  exit 1
fi

BUNDLE_ZIP=${1:-"../autocad-room-bundle/LBF.Acad.Rooms.bundle.zip"}
APP_BUNDLE_ID=${APP_BUNDLE_ID:-"LBF-Acad-Rooms-v1"}
ACTIVITY_ID=${ACTIVITY_ID:-"LBF-Acad-Rooms-v1"}
ENGINE=${ENGINE:-"Autodesk.AutoCAD+24_2"}

if [[ ! -f "$BUNDLE_ZIP" ]]; then
  echo "Bundle introuvable: $BUNDLE_ZIP" >&2
  exit 1
fi

TOKEN=$(curl -s -X POST "https://developer.api.autodesk.com/authentication/v2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$APS_CLIENT_ID&client_secret=$APS_CLIENT_SECRET&grant_type=client_credentials&scope=data:read data:write bucket:create bucket:read code:all" | jq -r '.access_token')

if [[ "$TOKEN" == "null" ]]; then
  echo "Impossible d'obtenir un token APS." >&2
  exit 1
fi

echo "Publication de l'app bundle $APP_BUNDLE_ID…"
curl -s -X POST "https://developer.api.autodesk.com/da/us-east/v3/applications" \
  -H "Authorization: Bearer $TOKEN" \
  -F "data=@${BUNDLE_ZIP}" \
  -F "id=${APP_BUNDLE_ID}" \
  -F "engine=${ENGINE}" \
  -F "description=LBF AutoCAD rooms exporter" \
  > /tmp/${APP_BUNDLE_ID}_bundle_response.json

echo "Réponse bundle enregistrée dans /tmp/${APP_BUNDLE_ID}_bundle_response.json"

echo "Création de l'activité $ACTIVITY_ID…"
read -r -d '' ACTIVITY_PAYLOAD <<JSON
{
  "id": "${ACTIVITY_ID}",
  "commandLine": [
    "$(printf "%%AUTODESK%%/autocadcoreconsole.exe /i input.dwg /al LBF.Acad.Rooms.dll /s LBF_EXPORT_ROOMS")"
  ],
  "parameters": {
    "inputDwg": {
      "verb": "get",
      "description": "Plan DWG",
      "required": true,
      "ondemand": false
    },
    "outputJson": {
      "verb": "put",
      "description": "Rooms JSON",
      "required": true,
      "ondemand": false
    }
  },
  "engine": "${ENGINE}",
  "appbundles": [
    "${APP_BUNDLE_ID}"
  ]
}
JSON

curl -s -X POST "https://developer.api.autodesk.com/da/us-east/v3/activities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$ACTIVITY_PAYLOAD" \
  > /tmp/${ACTIVITY_ID}_activity_response.json

echo "Réponse activity enregistrée dans /tmp/${ACTIVITY_ID}_activity_response.json"
echo "Publication AutoCAD terminée."
