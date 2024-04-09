.PHONY: test run fmt

test:
	@bash -c 'scripts/test.sh'

fmt:
	@bash -c 'pre-commit run -av'

run:
	@poetry run python src/app.py

make unittest:
	@poetry run pytest test/unit/ --disable-warnings -s
