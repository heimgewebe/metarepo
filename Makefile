UV ?= uv
REPOS_YML := repos.yml
ORG_GENERATOR := $(UV) run scripts/generate_org_assets.py --repos-file $(REPOS_YML)

.PHONY: all deps index graph linkcheck fleet fleet-check doctor doctor-ci

all: index graph

deps:
	$(UV) sync --frozen

index: deps
	$(ORG_GENERATOR) --index docs/org-index.md

graph: deps
	$(ORG_GENERATOR) --graph docs/org-graph.mmd

linkcheck:
	docker run --rm -v $$(pwd):/work ghcr.io/lycheeverse/lychee:v0.15.1 --config /work/.lychee.toml

fleet:
	@echo "→ Generating Heimgewebe fleet readiness and repos list"
	@python scripts/fleet/generate_readiness.py \
		--matrix docs/repo-matrix.md \
		--out-json reports/heimgewebe-readiness.json \
		--write-repos-txt fleet/repos.txt
	@echo "✓ Done."

fleet-check:
	@python scripts/fleet/verify_generated_repos_txt.py \
		--matrix docs/repo-matrix.md \
		--fleet fleet/repos.txt

doctor:
	@[ -f reports/heimgewebe-readiness.json ] || $(MAKE) fleet
	@python scripts/fleet/doctor.py --report reports/heimgewebe-readiness.json

doctor-ci:
	@[ -f reports/heimgewebe-readiness.json ] || $(MAKE) fleet
	@python scripts/fleet/doctor.py --report reports/heimgewebe-readiness.json --ci
