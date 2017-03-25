"""
This file starts the jobs processor.
"""
import json
import beanstalkc

BEANSTALK = beanstalkc.Connection(host='localhost', port=14711)

def process_job(job_json):
    """
    Given a JSON belonging to a job, process_job sends it to the
    analyzer and then it posts the output to firebase.
    """
    print 'Processing message...'
    print job_json['message']
    print 'Send results to firebase'
    return True

def load_jobs():
    """
    Load and process all jobs from beanstalkd
    """
    while True:
        # reserve blocks the execution until there's a new job
        current_job = BEANSTALK.reserve()

        try:
            process_job(json.loads(current_job.body))
        except ValueError, err:
            print err

        current_job.delete()

# Start the magic!
load_jobs()
