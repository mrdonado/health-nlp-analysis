"""
server_test.py
"""
from analyzer.processor import process_job

def test_base_route():
    """ Testing the base route """
    example_job = {"message": "Example message"}
    assert process_job(example_job)
