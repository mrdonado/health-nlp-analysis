init:
	pip install -r requirements.txt

test:
	pytest -f ./*_test.py

coverage:
	nosetests --with-coverage --cover-erase --cover-html --cover-package=src

run:
	python main.py

.PHONY: init test