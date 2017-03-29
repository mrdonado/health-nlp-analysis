"""
engine_test.py
"""
import pytest
from analyzer.engine import nlp_analysis

def test_nlp_analysis():
    example_analysis = nlp_analysis("Example")
    assert example_analysis == {"healthRelated": True, "tags": ["Tag1", "Tag2", "Tag3", "Example"]}


