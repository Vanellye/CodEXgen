#!/usr/bin/env sh
# ERIA Wiki Drop-Link API examples. Requires curl and jq (for safely encoding JSON request bodies).
set -eu
: "${ERIA_BASE_URL:?Set ERIA_BASE_URL, e.g. https://eria.example.com}"
: "${ERIA_API_TOKEN:?Set ERIA_API_TOKEN (32+ characters)}"
AUTH="Authorization: Bearer ${ERIA_API_TOKEN}"
JSON="Content-Type: application/json"

case "${1:-help}" in
  health)
    curl --fail-with-body --silent --show-error "${ERIA_BASE_URL}/health"
    ;;
  list)
    curl --fail-with-body --silent --show-error -H "${AUTH}" "${ERIA_BASE_URL}/api/links"
    ;;
  search)
    : "${2:?Usage: $0 search QUERY}"
    curl --fail-with-body --silent --show-error -G -H "${AUTH}" --data-urlencode "q=$2" "${ERIA_BASE_URL}/api/links"
    ;;
  add)
    : "${2:?Usage: $0 add TITLE URL [CATEGORY]}"
    : "${3:?Usage: $0 add TITLE URL [CATEGORY]}"
    CATEGORY="${4:-Other}"
    jq -n --arg title "$2" --arg url "$3" --arg category "$CATEGORY" '{title:$title,url:$url,category:$category}' |
      curl --fail-with-body --silent --show-error -X POST -H "${AUTH}" -H "${JSON}" --data-binary @- "${ERIA_BASE_URL}/api/links"
    ;;
  archive)
    : "${2:?Usage: $0 archive UUID}"
    curl --fail-with-body --silent --show-error -X DELETE -H "${AUTH}" "${ERIA_BASE_URL}/api/links/$2"
    ;;
  audit)
    curl --fail-with-body --silent --show-error -H "${AUTH}" "${ERIA_BASE_URL}/api/audit"
    ;;
  intent)
    : "${2:?Usage: $0 intent publish_wiki|background_dispatch [REASON]}"
    SCOPE="$2"
    REASON="${3:-}"
    jq -n --arg scope "$SCOPE" --arg reason "$REASON" '{scope:$scope,confirmation:$scope,reason:$reason}' |
      curl --fail-with-body --silent --show-error -X POST -H "${AUTH}" -H "${JSON}" --data-binary @- "${ERIA_BASE_URL}/api/authorization-intents"
    ;;
  *)
    echo "Usage: $0 {health|list|search QUERY|add TITLE URL [CATEGORY]|archive UUID|audit|intent SCOPE [REASON]}" >&2
    exit 2
    ;;
esac
