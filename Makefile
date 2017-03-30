init:
	pip install -r requirements.txt

runqueue:
	beanstalkd -l 127.0.0.1 -p 14711

runqueuedocker:
	docker run -d -p 14711:11300 schickling/beanstalkd

test:
	export PYTHONPATH=.;pytest tests

watchtest:
	export PYTHONPATH=.;pytest-watch tests 

coverage:
	nosetests --with-coverage --cover-erase --cover-html --cover-package=analyzer

clean:
	find . -name "*.pyc" -exec rm -f {} \;

putmessage:
	python put_message.py 'A message that you want to process.'

builddocker:
	docker build -t python-health-nlp .

rundocker:
	docker run python-health-nlp

composedocker:
	docker-compose up

cleancontainers:
	sudo docker ps --filter "status=exited" | awk '{print $1}' | xargs sudo docker rm -f

run:
	python main.py

.PHONY: init test coverage run runqueue putmessage