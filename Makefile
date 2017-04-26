init:
	pip3 install -r requirements.txt; python3 -m spacy.en.download all

runqueue:
	beanstalkd -l 127.0.0.1 -p 11300 

runqueuedocker:
	docker run -d -p 11300:11300 schickling/beanstalkd

test:
	export PYTHONPATH=.;pytest tests

watchtest:
	export PYTHONPATH=.;pytest-watch tests 

coverage:
	nosetests --with-coverage --cover-erase --cover-html --cover-package=analyzer

clean:
	find . -name "*.pyc" -exec rm -f {} \;

putmessage:
	python3 put_message.py 'A message that you want to process.'

builddocker:
	docker build -t python-health-nlp .

rundocker:
	docker run python-health-nlp

composedocker:
	docker-compose up

cleancontainers:
	sudo docker ps --filter "status=exited" | awk '{print $1}' | xargs sudo docker rm -f

run:
	python3 main.py

.PHONY: init test coverage run runqueue putmessage
