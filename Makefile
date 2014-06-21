all: mbm.egg-info man/mbm.1.gz

install: all
	python3 setup.py install

mbm.egg-info:
	python3 setup.py egg_info

test: all
	python3 setup.py test

coverage: clean
	coverage3 run --source=. setup.py test
	coverage3 html
	coverage3 report

man/mbm.1.gz:
	gzip -kf man/mbm.1

pep8:
	pep8 .

clean:
	python3 setup.py clean
	rm -rf mbm.egg-info mbm/__pycache__/
	rm -rf .coverage htmlcov/
	rm -rf man/mbm.1.gz
	rm -rf test_config
	rm -rf build
	rm -rf dist
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
