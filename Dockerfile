FROM python:latest
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ADD requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt && \
    python3 -m spacy download en
CMD python3 main.py
