init:
	pip install -e .
	pip install -r requirements-test.txt

.PHONY: tests

tests:
	pytest tests

flake8:
	flake8 src tests

coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=formencode formencode

publish:
	pip install "twine>=4" build
	python -m build
	twine upload dist/*
	rm -fr build dist .egg src/FormEncode.egg-info

.PHONY: docs

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
