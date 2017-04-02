[![Build Status](https://travis-ci.org/fjrd84/health-nlp-analysis.svg?branch=master)](https://travis-ci.org/fjrd84/health-nlp-analysis)
[![Coverage Status](https://coveralls.io/repos/github/fjrd84/health-nlp-analysis/badge.svg?branch=master)](https://coveralls.io/github/fjrd84/health-nlp-analysis?branch=master)

# health-nlp-analysis
This repository contains the jobs processor and the analysis part of the ***health-nlp*** project.

The ***health-nlp*** project is an NLP (Natural Language Processing) demo composed by the following repositories:

- [health-nlp-angular](https://github.com/fjrd84/health-nlp-angular): frontend part. It displays the results of the analysis (stored in firebase) and explains everything about the project. It is an Angular based web application.
- [health-nlp-node](https://github.com/fjrd84/health-nlp-node): nodeJS/express backend for the health-nlp-angular frontend. It takes new job requests and sends them to the beanstalkd job queue.
- [health-nlp-analysis](https://github.com/fjrd84/health-nlp-analysis) (this repository): it processes jobs from beanstalkd and sends the results to firebase. It is a Python project.

This project is still on an early stage of development. As soon as there's an online demo available, you'll find a link here.

## Get this thing running

This project contains a Python program that takes jobs from a beanstalkd service, sends them to the analyzer and posts the results to firebase. Follow these steps in order to run it on your machine.

### Beanstalkd

The first thing you need is a beanstalkd service.

If you have docker on your system just type `make runqueuedocker` in order to start a dockerized beanstalkd queue.

If you want to install it locally on your system, and you are running a debian based linux distribution, you can install beanstalkd by typing this on the console:

`sudo apt-get install beanstalkd`.

If you're using MacOSX or another linux distribution, just follow the [instructions on the official documentation](http://kr.github.io/beanstalkd/download.html).

In order to start the beanstalkd service, you can type this on the shell:

`beanstalkd -l 127.0.0.1 -p 11300`

Alternatively, `make runqueue` runs exactly that command.

By default, we're using port `11300` and IP `127.0.0.1`. You can change this in the `config.ini` file.

### Python Dependencies

In order to install the dependencies, you can simply type `make init`, or alternatively:

`sudo pip install -r requirements.txt`

### Configuration

There's a `config.ini.example` file in the root directory of this repository. You need to rename it as `config.ini` and specify your own configuration parameters before running the service.

In the `config.ini`, you set the details about the connection with firebase and beanstalkd.

### Run it!

Once beanstalkd is running on your machine and the configuration is ready, you can type `make run` to start the job processor and the analyzer.

### Is it working?

If you want to insert an example job into the jobs queue and see what happens, you can use the `put_message.py` utility. Just type the following on the console, from the root directory of this project:

`python put_message.py 'A message that you want to process.'`

Alternatively, `make putmessage` runs exactly that command.

A JSON string with the following format will be sent to the jobs queue:

```json
{
    "user_name": "jdonado",
    "user_description": "Some random radiologist.",
    "created_at": "2017-03-26 22:18:32.749317",
    "message": "Aspirin for diabetes",
    "source": "twitter",
    "query": "diabetes"
}
```

This JSON will be sent as it is directly to the analyzer. Once the analysis is ready, the original JSON will be extended with the analysis information and sent to firebase.

```json
{
    "user_name": "jdonado",
    "user_description": "Some random radiologist.",
    "created_at": "2017-03-26 22:18:32.749317",
    "message": "Aspirin for diabetes",
    "source": "twitter",
    "query": "diabetes",
    "analysis":  {
        "created_at": "2017-03-26 22:19:52.133117",
        "profile": "radiologist",
        "problem": "diabetes",
        "solution": "aspirin"
    }
}
```


## Unit Tests and Coverage

You can run the tests by typing this on the console:

`make test`

And the you can generate the coverage report with:

`make coverage`

## Docker

If you want to deploy this service inside Docker containers, you will find the `docker-compose.yml` file on the root directory of this repository.

Some helper scripts can be found into the `Makefile` in order to perform the usual tasks.
