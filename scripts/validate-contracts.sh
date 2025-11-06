#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d contracts ]]; then
	echo "contracts directory not found – nothing to validate"
	exit 0
fi
if ! command -v npm >/dev/null 2>&1; then
	echo "::error::npm is required to validate contracts"
	exit 1
fi
# Prefer npx to avoid global state on shared runners
shopt -s nullglob
mapfile -t schemas < <(compgen -G 'contracts/**/*.schema.json' || true)
if ((${#schemas[@]} == 0)); then
	echo "::notice::No schemas found under contracts/"
else
	for schema in "${schemas[@]}"; do
		echo "::group::Schema ${schema}"
		npx --yes ajv-cli@5 compile -s "${schema}" --strict=true
		echo "::endgroup::"
	done
fi
if compgen -G 'fixtures/**/*.jsonl' >/dev/null; then
	for fixture in fixtures/**/*.jsonl; do
		base="$(basename "${fixture}" .jsonl)"
		schema="contracts/${base}.schema.json"
		echo "::group::Validate ${fixture}"
		if [[ -f "${schema}" ]]; then
			npx --yes ajv-cli@5 validate -s "${schema}" -d "${fixture}" --spec=draft2020 --errors=line --all-errors
		else
			echo "::notice::No matching schema for ${fixture} (expected ${schema})"
		fi
		echo "::endgroup::"
	done
else
	echo "No fixtures found under fixtures/"
fi
