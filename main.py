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
from config_loader import BEANSTALKD_CONFIG, FIREBASE_CONFIG
from analyzer.processor import process_job
from analyzer.uploader import AnalysisUploader

BEANSTALK = pystalkd.Beanstalkd.Connection(
    host=BEANSTALKD_CONFIG['beanstalk_ip'], port=BEANSTALKD_CONFIG['beanstalk_port'])


def load_jobs():
    """
    Load and process all jobs from beanstalkd
    """
    print('Listening on ' + BEANSTALKD_CONFIG['beanstalk_ip'] +
          ':' + str(BEANSTALKD_CONFIG['beanstalk_port']))

    uploader = AnalysisUploader(FIREBASE_CONFIG["api_key"],
                                FIREBASE_CONFIG["auth_domain"],
                                FIREBASE_CONFIG["database_url"],
                                FIREBASE_CONFIG["storage_bucket"],
                                FIREBASE_CONFIG["email"], FIREBASE_CONFIG["password"])

    while True:
        # reserve blocks the execution until there's a new job
        current_job = BEANSTALK.reserve()

        try:
            process_job(json.loads(current_job.body), uploader)
        except:
            print("Unexpected error:", sys.exc_info()[0])

        current_job.delete()


# Start the magic!
load_jobs()
