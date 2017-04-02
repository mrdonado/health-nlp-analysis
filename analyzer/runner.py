#!/usr/bin/python3
"""

This script starts listening to the beanstalkd jobs queue
and whenever it finds any new jobs, it sends them to the jobs
processor.

The process will remain active until the user manually stops it.

"""
import json
import pystalkd.Beanstalkd
import sys
from analyzer.processor import process_job
from analyzer.uploader import AnalysisUploader


def setup_and_run(beanstalkd_config, firebase_config, loop_forever):
    """
    Setup the beanstalkd connection and the firebase uploader.
    Then start listening to the jobs queue and send the jobs
    to the analyzer.
    """
    # Setup connection to the jobs queue
    beanstalk = pystalkd.Beanstalkd.Connection(
        host=beanstalkd_config['beanstalk_ip'], port=beanstalkd_config['beanstalk_port'])
    print('Listening on ' + beanstalkd_config['beanstalk_ip'] +
          ':' + str(beanstalkd_config['beanstalk_port']))

    # Setup the firebase uploader
    uploader = AnalysisUploader(firebase_config["api_key"],
                                firebase_config["auth_domain"],
                                firebase_config["database_url"],
                                firebase_config["storage_bucket"],
                                firebase_config["email"], firebase_config["password"])

    # Start waiting for jobs from the queue.
    while True:
        # reserve blocks the execution until there's a new job
        current_job = beanstalk.reserve()

        try:
            process_job(json.loads(current_job.body), uploader)
        except:
            print("Unexpected error:", sys.exc_info()[0])

        current_job.delete()

        if not loop_forever:
            return
