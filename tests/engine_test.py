"""
engine_test.py
"""
from analyzer.engine import dummy_nlp_analysis


def test_dummy_nlp_analysis():
    input_job = {
        "user_name": "jdonado",
        "user_description": "Some random radiologist.",
        "created_at": "2017-04-02T22:35:04.868Z",
        "message": "Some random message",
        "source": "twitter",
        "query": "diabetes"
    }
    example_analysis = dummy_nlp_analysis(input_job)
    assert example_analysis["health_related"] == "Doctor"
    assert example_analysis["profile"] == "radiologist"
    assert example_analysis["problem"] == "diabetes"
    assert example_analysis["solution"] == "aspirin"
