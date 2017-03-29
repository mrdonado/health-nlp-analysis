init:
	pip install -r requirements.txt

runqueue:
	beanstalkd -l 127.0.0.1 -p 14711

test:
	export PYTHONPATH=.;pytest tests

watchtest:
	export PYTHONPATH=.;pytest tests -f

coverage:
	nosetests --with-coverage --cover-erase --cover-html --cover-package=analyzer

clean:
	find . -name "*.pyc" -exec rm -f {} \;

putmessage:
	python put_message.py 'A message that you want to process.'

run:
	python main.py

.PHONY: init test coverage run runqueue putmessage