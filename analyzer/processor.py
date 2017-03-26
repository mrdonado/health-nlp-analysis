"""
The task of the job processor is to take a JSON description
of a new job, send the message to the analyzer and post the
results to firebase.
"""

def process_job(job_json):
    """
    Given a JSON belonging to a job, process_job sends it to the
    analyzer and then it posts the output to firebase.
    """
    print 'Processing message...'
    print job_json['message']
    print 'Send results to firebase'
    return True
