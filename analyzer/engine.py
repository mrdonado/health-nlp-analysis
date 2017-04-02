"""
Example of a script performing an NLP analysis of a given message
"""
import datetime

def dummy_nlp_analysis(message):
    """
    An nlp analysis function returns a JSON with different tags and a
    classification.
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
