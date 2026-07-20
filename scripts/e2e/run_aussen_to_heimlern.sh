#!/usr/bin/env bash
set -euo pipefail
cat >&2 << 'EOF'
ARCHIVED_PATH: Der direkte E2E-Pfad aussensensor -> chronik -> heimlern ist stillgelegt.
Heimlern ist eine archivierte Referenz ohne Ingest-, Runtime- oder Produktionsautorität.
Kein Environment-Flag, Trockenlauf oder Endpunkt kann diesen Pfad reaktivieren.
EOF
exit 64
