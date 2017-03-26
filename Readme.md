# health-nlp-analysis
This repository contains the jobs processor and the analysis part of the ***health-nlp*** project.

The ***health-nlp*** project is an NLP (Natural Language Processing) demo composed by the following repositories:

- [health-nlp-angular](https://github.com/fjrd84/health-nlp-angular): frontend part. It displays the results of the analysis (stored in firebase) and explains everything about the project. It is an Angular based web application.
- [health-nlp-node](https://github.com/fjrd84/health-nlp-node): nodeJS/express backend for the health-nlp-angular frontend. It takes new job requests and sends them to the beanstalkd job queue.
- [health-nlp-analysis](https://github.com/fjrd84/health-nlp-analysis) (this repository): it processes jobs from beanstalkd and sends the results to firebase. It is a Python project.

This project is still on an early stage of development. As soon as there's an online demo available, you'll find a link here.

## Get this thing running

This project takes jobs from a beanstalkd service, sends them to the analyzer and posts the results to firebase.

The first thing you need in your machine to make it work is a beanstalkd service. If you are running a debian based linux distribution, you can install beanstalkd by typing this on the console:

`sudo apt-get install beanstalkd`.

In order to start the beanstalkd service, you need to type this on the terminal:

`beanstalkd -l 127.0.0.1 -p 14711`

By default, we're using port `14711` and IP `127.0.0.1`. You can change this in the configuration.py file.

Once beanstalkd is running on your machine, you can type `make run` to start the job processor and the analyzer.

If you want to insert an example job into the jobs queue and see what happens, you can use the `put_message.py` utility. Just type the following on the console, from the root directory of this project:

`python put_message.py 'A message that you want to process.'`

A JSON string with the following format will be sent to the job queue:

```json
{
    "message": "A message that you want to process",
    "author": "jdonado",
    "source": "web-app"
}
```

### Python Dependencies

In order to install the dependencies, you can simply type `make init`, or alternatively:

`sudo pip install -r requirements.txt`
