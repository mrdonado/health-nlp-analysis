"""
engine_test.py
"""
from analyzer.engine import dummy_nlp_analysis

def test_dummy_nlp_analysis():
    example_analysis = dummy_nlp_analysis("Example")
    assert example_analysis["health_related"] == "true"
    assert example_analysis["profile"] == "radiologist"
    assert example_analysis["problem"] == "diabetes"
    assert example_analysis["solution"] == "aspirin"
