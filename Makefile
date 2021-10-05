.PHONY: docs
init:
	pip install -e .
	pip install -r requirements-dev.txt
ci:
	pytest formencode

flake8:
	flake8 --ignore=E501,F401,E128,E402,E731,F821 formencode

coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=formencode formencode

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg FormEncode.egg-info

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
