"""

This script starts listening to the beanstalkd jobs queue
and whenever it finds any new jobs, it sends them to the jobs
processor.

The process will remain active until the user manually stops it.

"""
import json
import pystalkd.Beanstalkd
from analyzer.configuration import CONFIG
from analyzer.processor import process_job
from analyzer.uploader import AnalysisUploader

BEANSTALK = pystalkd.Beanstalkd.Connection(host=CONFIG['beanstalk_ip'], port=CONFIG['beanstalk_port'])

def load_jobs():
    """
    Load and process all jobs from beanstalkd
    """
    print('Listening on ' + CONFIG['beanstalk_ip'] + ':' + str(CONFIG['beanstalk_port']))

    uploader = AnalysisUploader()

    while True:
        # reserve blocks the execution until there's a new job
        current_job = BEANSTALK.reserve()

        try:
            process_job(json.loads(current_job.body), uploader)
        except(ValueError, err):
            print(err)

        current_job.delete()

# Start the magic!
load_jobs()
