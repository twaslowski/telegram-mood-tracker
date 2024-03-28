.PHONY: test run fmt

test:
	@poetry run pytest test/ --disable-warnings

run:
	@bash scripts/run.sh

fmt:
	@bash -c 'pre-commit run black --all-files'

build:
	@bash scripts/build.sh
