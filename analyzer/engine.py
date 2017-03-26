"""
Example of a script performing an NLP analysis of a given message
"""

def nlp_analysis(message):
    """
    An nlp analysis function returns a JSON with different tags and a
    classification.
    """
    result = {"healthRelated": True, "tags": ["Tag1", "Tag2", "Tag3", message]}
    return result
