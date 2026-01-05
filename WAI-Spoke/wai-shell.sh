#!/usr/bin/env bash
set -e

WAI_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WAI_TAB_NAME="${1:-WAI}"
export WAI_ROOT
export PS1="[$WAI_TAB_NAME \\A \\$(pwd | sed \"s#^$WAI_ROOT##; s#^$#/#\") ]\\$ "

exec bash --noprofile --norc -i
