run:
	poetry run python open_theremin

install:
	poetry install

format:
	poetry run black .
	poetry run isort .

test:
	poetry run pytest
