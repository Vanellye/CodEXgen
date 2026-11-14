#!/usr/bin/env bash
# ERIA — Bash M*ASH SSD Rhythm Engine
# Safe filesystem orchestration; no device, partition, or firmware commands.
set -Eeuo pipefail
umask 077

ROOT="${ERIA_STORAGE_ROOT:-./eria-storage}"
LOG="$ROOT/rhythm.log"
CHECKPOINTS="$ROOT/checkpoints"

init_storage() { mkdir -p -- "$ROOT" "$CHECKPOINTS"; }

pulse() {
    init_storage
    printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$LOG"
}

require_file() {
    local path=${1:-}
    [[ -n "$path" && -f "$path" && -r "$path" ]]
}

read_rhythm() {
    local source=${1:-}
    if ! require_file "$source"; then
        pulse "READ_REJECTED: ${source:-<missing>}"
        return 1
    fi
    sha256sum -- "$source"
}

write_rhythm() {
    local source=${1:-} destination=${2:-} overwrite=${3:-false}
    local destination_dir tmp

    if ! require_file "$source"; then
        pulse "WRITE_REJECTED: source is missing or unreadable"
        return 1
    fi
    if [[ -z "$destination" ]]; then
        pulse "WRITE_REJECTED: destination is required"
        return 2
    fi
    if [[ -e "$destination" && "$source" -ef "$destination" ]]; then
        pulse "WRITE_REJECTED: source and destination are the same file"
        return 1
    fi

    destination_dir=$(dirname -- "$destination")
    if [[ ! -d "$destination_dir" || ! -w "$destination_dir" ]]; then
        pulse "WRITE_REJECTED: destination directory is missing or not writable"
        return 1
    fi
    if [[ -e "$destination" && "$overwrite" != true ]]; then
        pulse "WRITE_REJECTED: destination exists; pass --overwrite to replace it"
        return 1
    fi

    tmp=$(mktemp "$destination_dir/.eria-write.XXXXXX")
    if ! cat -- "$source" > "$tmp"; then
        rm -f -- "$tmp"
        pulse "WRITE_FAILED: staging copy failed"
        return 1
    fi
    if ! sync -f "$tmp"; then
        rm -f -- "$tmp"
        pulse "WRITE_FAILED: staged data could not be synchronized"
        return 1
    fi

    if [[ "$overwrite" == true ]]; then
        if ! mv -f -- "$tmp" "$destination"; then
            rm -f -- "$tmp"
            pulse "WRITE_FAILED: atomic replacement failed"
            return 1
        fi
    else
        # link(2) creates the destination only if it does not already exist.
        if ! ln -- "$tmp" "$destination"; then
            rm -f -- "$tmp"
            pulse "WRITE_REJECTED: destination appeared during write"
            return 1
        fi
        rm -f -- "$tmp"
    fi

    if ! sync -f "$destination_dir"; then
        pulse "WRITE_WARNING: destination committed but directory sync failed"
        return 1
    fi
    pulse "WRITE_COMMITTED: $destination"
}

verify_rhythm() {
    local source=${1:-} destination=${2:-}
    local source_hash destination_hash

    if ! require_file "$source" || ! require_file "$destination"; then
        pulse "VERIFY_REJECTED: source or destination is missing or unreadable"
        return 1
    fi
    source_hash=$(sha256sum -- "$source" | cut -d ' ' -f1)
    destination_hash=$(sha256sum -- "$destination" | cut -d ' ' -f1)

    if [[ "$source_hash" != "$destination_hash" ]]; then
        pulse "VERIFY_FAILED: $destination"
        return 1
    fi
    pulse "VERIFY_PASSED: $destination"
}

sync_rhythm() {
    local source=${1:-} destination=${2:-} overwrite=${3:-false}
    write_rhythm "$source" "$destination" "$overwrite"
    verify_rhythm "$source" "$destination"
}

checkpoint_rhythm() {
    local source=${1:-} label=${2:-checkpoint}
    local stamp manifest digest

    if ! require_file "$source"; then
        pulse "CHECKPOINT_REJECTED: source is missing or unreadable"
        return 1
    fi
    if [[ ! "$label" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]]; then
        pulse "CHECKPOINT_REJECTED: label must be 1-64 safe filename characters"
        return 2
    fi

    init_storage
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    digest=$(sha256sum -- "$source" | cut -d ' ' -f1)
    manifest=$(mktemp "$CHECKPOINTS/${stamp}-${label}.XXXXXX.checkpoint")
    {
        printf 'timestamp=%s\n' "$stamp"
        printf 'sha256=%s\n' "$digest"
        printf 'source=%q\n' "$source"
    } > "$manifest"
    sync -f "$manifest"
    pulse "CHECKPOINT_CREATED: $manifest"
}

usage() {
    cat <<'USAGE'
ERIA Bash M*ASH SSD Rhythm Engine

Usage:
  rhythm-engine.sh read FILE
  rhythm-engine.sh write [--overwrite] SOURCE DESTINATION
  rhythm-engine.sh verify SOURCE DESTINATION
  rhythm-engine.sh sync [--overwrite] SOURCE DESTINATION
  rhythm-engine.sh checkpoint FILE [LABEL]

Writes are staged in the destination directory. Existing destinations are
never replaced unless --overwrite is explicitly supplied. Checkpoints record
a SHA-256 manifest; they do not copy data or control physical SSD hardware.
USAGE
}

main() {
    local command=${1:-help}
    shift || true

    case "$command" in
        read)
            [[ $# -eq 1 ]] || { usage >&2; return 2; }
            read_rhythm "$1"
            ;;
        write|sync)
            local overwrite=false
            if [[ ${1:-} == --overwrite ]]; then
                overwrite=true
                shift
            fi
            [[ $# -eq 2 ]] || { usage >&2; return 2; }
            if [[ "$command" == write ]]; then
                write_rhythm "$1" "$2" "$overwrite"
            else
                sync_rhythm "$1" "$2" "$overwrite"
            fi
            ;;
        verify)
            [[ $# -eq 2 ]] || { usage >&2; return 2; }
            verify_rhythm "$1" "$2"
            ;;
        checkpoint)
            [[ $# -ge 1 && $# -le 2 ]] || { usage >&2; return 2; }
            checkpoint_rhythm "$1" "${2:-checkpoint}"
            ;;
        help|-h|--help) usage ;;
        *) usage >&2; return 2 ;;
    esac
}
main "$@"
