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


def setup_and_run():
    """
    Setup the beanstalkd connection and the firebase uploader.
    Then start listening to the jobs queue and send the jobs
    to the analyzer.
    """
    # Setup connection to the jobs queue
    beanstalk = pystalkd.Beanstalkd.Connection(
        host=BEANSTALKD_CONFIG['beanstalk_ip'], port=BEANSTALKD_CONFIG['beanstalk_port'])
    print('Listening on ' + BEANSTALKD_CONFIG['beanstalk_ip'] +
          ':' + str(BEANSTALKD_CONFIG['beanstalk_port']))

    # Setup the firebase uploader
    uploader = AnalysisUploader(FIREBASE_CONFIG["api_key"],
                                FIREBASE_CONFIG["auth_domain"],
                                FIREBASE_CONFIG["database_url"],
                                FIREBASE_CONFIG["storage_bucket"],
                                FIREBASE_CONFIG["email"], FIREBASE_CONFIG["password"])

    # Start waiting for jobs from the queue.
    while True:
        # reserve blocks the execution until there's a new job
        current_job = beanstalk.reserve()

        try:
            process_job(json.loads(current_job.body), uploader)
        except:
            print("Unexpected error:", sys.exc_info()[0])

        current_job.delete()

# Start the magic!
if __name__ == "__main__":
    setup_and_run()
