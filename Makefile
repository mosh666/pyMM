install:
	pip install -e .[dev]

test:
	pytest

lint:
	ruff check .
	mypy .

run:
	python launcher.py

format:
	ruff format .

clean:
	Remove-Item -Recurse -Force python3*, lib-py3*, *.zip, *.sha256, build, dist, *.egg-info, .pytest_cache, .mypy_cache, __pycache__ -ErrorAction SilentlyContinue

build:
	python scripts/build_distribution.py
