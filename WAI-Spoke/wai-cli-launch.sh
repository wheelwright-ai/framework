#!/usr/bin/env bash
set -e

WAI_WORKSPACE_VERSION="2026.01.05"

WAI_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WAI_TAB_NAME="${1:-WAI - CLI}"
export WAI_ROOT
export PS1="[$WAI_TAB_NAME \\A \\$(pwd | sed \"s#^$WAI_ROOT##; s#^$#/#\") ]\\$ "

cd "$WAI_ROOT"
set +e
./WAI-CLI
set -e
exec bash --noprofile --norc -i
