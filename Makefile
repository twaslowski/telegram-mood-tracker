.PHONY: test run fmt

test:
	@export PYTHONPATH=./ && poetry run pytest test/ --disable-warnings

fmt:
	@bash -c 'pre-commit run black --all-files'
