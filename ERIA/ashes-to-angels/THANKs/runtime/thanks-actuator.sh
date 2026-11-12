#!/usr/bin/env bash
# THANKs simulated actuator. Never controls physical hardware or dispatches externally.
set -euo pipefail
readonly TRIGGER_OVERRIDE=ON

trigger=""
simulation=""
approval=""
actor=""
scope=""
manual_trigger_approval=""
manual_trigger_reason=""
evidence_status=""
evidence_id=""
independent=""
reproducible=""
requested_speed=""
max_speed=""
emergency_stop="no"

usage() {
  cat <<'USAGE'
Usage:
  bash thanks-actuator.sh --simulate --trigger detected|manual \
    --approval-id ID --actor ID --scope THANKs:simulated-motion:execute \
    [--manual-trigger-approval-id ID --manual-trigger-reason TEXT] \
    --evidence-status SUPPORTED --evidence-id ID \
    --independent yes --reproducible yes \
    --requested-speed NUMBER --max-speed NUMBER [--emergency-stop yes]

TRIGGER_OVERRIDE is fixed ON. Manual trigger requires its own authorization ID
and reason. Both independent gates remain mandatory. Local simulation only.
USAGE
}

deny() {
  printf 'DECISION=BLOCKED\nGATE=%s\nREASON=%s\n' "$1" "$2"
  exit 2
}

while (($#)); do
  case "$1" in
    --simulate) simulation="yes"; shift ;;
    --trigger) trigger="${2-}"; shift 2 ;;
    --approval-id) approval="${2-}"; shift 2 ;;
    --actor) actor="${2-}"; shift 2 ;;
    --scope) scope="${2-}"; shift 2 ;;
    --manual-trigger-approval-id) manual_trigger_approval="${2-}"; shift 2 ;;
    --manual-trigger-reason) manual_trigger_reason="${2-}"; shift 2 ;;
    --evidence-status) evidence_status="${2-}"; shift 2 ;;
    --evidence-id) evidence_id="${2-}"; shift 2 ;;
    --independent) independent="${2-}"; shift 2 ;;
    --reproducible) reproducible="${2-}"; shift 2 ;;
    --requested-speed) requested_speed="${2-}"; shift 2 ;;
    --max-speed) max_speed="${2-}"; shift 2 ;;
    --emergency-stop) emergency_stop="${2-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) deny INPUT "unknown argument: $1" ;;
  esac
done

[[ "$simulation" == "yes" ]] || deny MODE "explicit --simulate is required"
[[ "$emergency_stop" != "yes" ]] || deny STOP "emergency stop is active"

case "$trigger" in
  detected)
    printf 'TRIGGER_PATH=AUTOMATIC_DETECTION\n'
    ;;
  manual)
    [[ "$TRIGGER_OVERRIDE" == "ON" ]] || deny TRIGGER_OVERRIDE "manual trigger override is disabled"
    [[ -n "$manual_trigger_approval" && -n "$manual_trigger_reason" ]] ||
      deny MANUAL_TRIGGER_AUTHORIZATION "manual trigger requires a separate authorization ID and reason"
    printf 'TRIGGER_PATH=MANUAL_OVERRIDE\nTRIGGER_OVERRIDE=%s\n' "$TRIGGER_OVERRIDE"
    printf 'MANUAL_TRIGGER_APPROVAL_ID=%s\nMANUAL_TRIGGER_REASON=%s\n' "$manual_trigger_approval" "$manual_trigger_reason"
    ;;
  *)
    deny TRIGGER "trigger must be detected or manually authorized; detection or absence alone is not permission"
    ;;
esac

# Pheônix authorization gate: separate from manual-trigger authorization.
[[ -n "$approval" && -n "$actor" && "$scope" == "THANKs:simulated-motion:execute" ]] ||
  deny PHEONIX_AUTHORIZATION "missing approval identity, actor, or exact simulation scope"

# Sure-rarity evidence gate is independent of authorization.
[[ "$evidence_status" == "SUPPORTED" && -n "$evidence_id" &&
   "$independent" == "yes" && "$reproducible" == "yes" ]] ||
  deny SURE_RARITY_EVIDENCE "evidence must be SUPPORTED, identified, independent, and reproducible"

number_re='^[0-9]+([.][0-9]+)?$'
[[ "$requested_speed" =~ $number_re && "$max_speed" =~ $number_re ]] ||
  deny MOTION_BOUNDS "speed values must be non-negative decimal numbers"
within_limit=$(awk -v requested="$requested_speed" -v maximum="$max_speed" 'BEGIN { print (requested <= maximum) ? "yes" : "no" }')
[[ "$within_limit" == "yes" ]] || deny MOTION_BOUNDS "requested speed exceeds configured simulation ceiling"

printf 'DECISION=SIMULATED_ACTUATION\nTARGET=THANKs:virtual-motion\n'
printf 'APPROVAL_ID=%s\nACTOR=%s\nEVIDENCE_ID=%s\n' "$approval" "$actor" "$evidence_id"
printf 'REQUESTED_SPEED=%s\nMAX_SPEED=%s\nMEASURED_SPEED=%s\n' "$requested_speed" "$max_speed" "$requested_speed"
printf 'EXTERNAL_DISPATCH=none\nPHYSICAL_ACTUATION=none\n'
