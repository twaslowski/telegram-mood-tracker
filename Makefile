.PHONY: test run fmt

test:
	@bash scripts/test.sh

run:
	@bash scripts/run.sh

fmt:
	@bash -c 'pre-commit run black --all-files'
