.PHONY: test run fmt

test:
	@export PYTHONPATH=./ && poetry run pytest test/ --exclude test/integration/manual --disable-warnings -s

fmt:
	@bash -c 'pre-commit run black --all-files'

run:
	@poetry run python src/app.py

make unittest:
	@poetry run pytest test/unit/ --disable-warnings -s
