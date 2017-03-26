init:
	pip install -r requirements.txt

runqueue:
	beanstalkd -l 127.0.0.1 -p 14711

test:
	pytest -f ./*_test.py

coverage:
	nosetests --with-coverage --cover-erase --cover-html --cover-package=src

putmessage:
	python put_message.py 'A message that you want to process.'

run:
	python main.py

.PHONY: init test coverage run runqueue putmessage