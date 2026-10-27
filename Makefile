.PHONY: test smoke public-audit

PYTHON ?= python3.12

test:
	$(PYTHON) -m compileall -q scripts tests
	$(PYTHON) -m unittest discover -s tests -v

smoke:
	$(PYTHON) scripts/benchmarking/local_gguf_matrix.py --help >/dev/null
	$(PYTHON) scripts/benchmarking/openclaw_local_model_suite.py --help >/dev/null
	$(PYTHON) scripts/benchmarking/openclaw_hosted_model_suite.py --help >/dev/null
	$(PYTHON) scripts/benchmarking/bunker_benchmark_v3.py --validate-only >/dev/null
	$(PYTHON) scripts/benchmarking/publish_v3_results.py --help >/dev/null
	$(PYTHON) scripts/benchmarking/rescore_bunker_benchmark_v3.py --help >/dev/null

public-audit:
	$(PYTHON) scripts/public_repo_audit.py
