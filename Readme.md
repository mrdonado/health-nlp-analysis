# health-nlp-analysis
This repository contains the analysis part of the ***health-nlp*** project.

The ***health-nlp*** project is an NLP (Natural Language Processing) demo composed by the following repositories:

- [health-nlp-angular](https://github.com/fjrd84/health-nlp-angular): frontend part. It displays the results of the analysis (stored in firebase) and explains everything about the project. It is an Angular based web application.
- [health-nlp-node](https://github.com/fjrd84/health-nlp-node): nodeJS/express backend for the health-nlp-angular frontend. It takes new job requests and sends them to the beanstalkd job queue.
- [health-nlp-analysis](https://github.com/fjrd84/health-nlp-analysis) (this repository): it processes jobs from beanstalkd and sends the results to firebase. It is a Python project.

This project is now in an early stage of development. As soon as there's an online demo available, you'll find a link on this page.

## Get this thing running
In order to start the beanstalkd service, you can run the `start-beanstalkd.sh` script (on a Linux machine). If you're using other system, just make sure that your beanstalkd service is running (by default, we're using port 14711 and IP 127.0.0.1).

## Dependencies

### Python

`sudo pip install -r requirements.txt`

### Beanstalkd

If you are running a debian based linux distribution, you can install beanstalkd by typing this on the console: `sudo apt-get install beanstalkd`