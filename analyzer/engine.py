"""
Example of a script performing an NLP analysis of a given message
"""
import datetime

def dummy_nlp_analysis(input_job):
    """
    An nlp analysis function returns a JSON with the analysis results
    for a given input JSON (input_job) that contains a message and
    information about the source.

    Here's an example of the expected JSON format for input_job:

    {
        "user_name": "jdonado",
        "user_description": "Some random radiologist.",
        "created_at": "2017-04-02T22:35:04.868Z",
        "message": "Some random message",
        "source": "twitter",
        "query": "diabetes"
    }

    This function provides just a dummy analizer that can be used as
    a model for future analysis engines.
    """
    result = {
        "health_related": "true",
        "created_at": datetime.datetime.now().isoformat(),
        "profile": "radiologist",
        "problem": "diabetes",
        "solution": "aspirin"
    }
    return result
