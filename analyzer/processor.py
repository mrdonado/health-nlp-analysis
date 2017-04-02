"""
The task of the job processor is to take a JSON description
of a new job, send the message to the analyzer and post the
results to firebase.
"""

import analyzer.engine

def process_job(job_json, uploader):
    """
    Given a JSON belonging to a job, process_job sends it to the
    analyzer and then it posts the output to firebase.
    """
    print('Processing message: ' + job_json['message'])
    analysis_result = analyzer.engine.dummy_nlp_analysis(job_json['message'])
    print('Send results to firebase')
    job_json['analysis'] = analysis_result
    uploader.upload_analysis(job_json)
    return True
