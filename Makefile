all: mbm.egg-info

mbm.egg-info:
	python3 setup.py egg_info

test: all
	python3 setup.py test

coverage: clean
	coverage3 run --source=. setup.py test
	coverage3 html
	coverage3 report

pep8:
	pep8 .

clean:
	rm -rf mbm.egg-info mbm/__pycache__/
	rm -rf .coverage htmlcov/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
