#!/usr/bin/env bash
# THANKs simulated actuator. This program never controls physical hardware or dispatches externally.
set -euo pipefail

trigger=""
simulation=""
approval=""
actor=""
scope=""
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
  bash thanks-actuator.sh --simulate --trigger detected \
    --approval-id ID --actor ID --scope THANKs:simulated-motion:execute \
    --evidence-status SUPPORTED --evidence-id ID \
    --independent yes --reproducible yes \
    --requested-speed NUMBER --max-speed NUMBER [--emergency-stop yes]

This is a local simulation only. No physical actuator or external dispatch exists.
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
[[ "$trigger" == "detected" ]] || deny TRIGGER "no recognized trigger; detection alone never authorizes motion"
[[ "$emergency_stop" != "yes" ]] || deny STOP "emergency stop is active"

# Pheônix authorization gate: all fields are required and scope is exact.
[[ -n "$approval" && -n "$actor" && "$scope" == "THANKs:simulated-motion:execute" ]] ||
  deny PHEONIX_AUTHORIZATION "missing approval identity, actor, or exact simulation scope"

# Sure-rarity evidence gate is independent of authorization.
[[ "$evidence_status" == "SUPPORTED" && -n "$evidence_id" &&
   "$independent" == "yes" && "$reproducible" == "yes" ]] ||
  deny SURE_RARITY_EVIDENCE "evidence must be SUPPORTED, identified, independent, and reproducible"

# Numeric validation and configured speed ceiling.
number_re='^[0-9]+([.][0-9]+)?$'
[[ "$requested_speed" =~ $number_re && "$max_speed" =~ $number_re ]] ||
  deny MOTION_BOUNDS "speed values must be non-negative decimal numbers"
within_limit=$(awk -v requested="$requested_speed" -v maximum="$max_speed" 'BEGIN { print (requested <= maximum) ? "yes" : "no" }')
[[ "$within_limit" == "yes" ]] || deny MOTION_BOUNDS "requested speed exceeds configured simulation ceiling"

# Simulation-only actuator: emits a command record; it does not move hardware.
printf 'DECISION=SIMULATED_ACTUATION\nTARGET=THANKs:virtual-motion\n'
printf 'APPROVAL_ID=%s\nACTOR=%s\nEVIDENCE_ID=%s\n' "$approval" "$actor" "$evidence_id"
printf 'REQUESTED_SPEED=%s\nMAX_SPEED=%s\nMEASURED_SPEED=%s\n' "$requested_speed" "$max_speed" "$requested_speed"
printf 'EXTERNAL_DISPATCH=none\nPHYSICAL_ACTUATION=none\n'
