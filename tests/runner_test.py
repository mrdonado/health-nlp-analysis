#!/usr/bin/python3
"""
runner_test.py
"""

import analyzer.runner


class DummyUploader(object):
    def __init__(self, api_key, auth_domain, database_url, storage_bucket, email, password):
        assert api_key == 'someKey'
        assert auth_domain == 'authDomain'
        assert database_url == 'databaseUrl'
        assert storage_bucket == 'storageBucket'
        assert email == 'email'
        assert password == 'password'


class DummyJob(object):
    body = "Job body"

    def delete(self):
        pass


class DummyBeanstalkd(object):
    def __init__(self, host, port):
        assert host == 'localhost'
        assert port == 11300

    def reserve(self):
        return DummyJob()


analyzer.runner.FirebaseAnalysisUploader = DummyUploader
analyzer.runner.pystalkd.Beanstalkd.Connection = DummyBeanstalkd


def test_runner():
    beanstalkd_config = dict(beanstalk_ip='localhost', beanstalk_port=11300)
    es_config = dict(url='http://localhost:9200',
                     user='elastic', password='changeme')
    firebase_config = dict(api_key="someKey", auth_domain="authDomain", database_url="databaseUrl",
                           storage_bucket="storageBucket", email="email", password="password")
    analyzer.runner.setup_and_run(
        beanstalkd_config, firebase_config, es_config, False)
