init:
	pip3 install -U -r requirements.txt; python3 -m spacy download en

runqueue:
	beanstalkd -l 127.0.0.1 -p 11300 

runservices:
	docker-compose up -d beanstalksvc 
	docker-compose up -d elasticsvc

runesdocker:
	docker run -p 9200:9200 -e "http.host=0.0.0.0" -e "transport.host=127.0.0.1" docker.elastic.co/elasticsearch/elasticsearch:5.4.3

runqueuedocker:
	docker run -d -p 11300:11300 schickling/beanstalkd

test:
	export PYTHONPATH=.;pytest tests

watchtest:
	export PYTHONPATH=.;pytest-watch tests 

coverage:
	python3 -m "nose" --with-coverage --cover-erase --cover-html --cover-package=analyzer

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
