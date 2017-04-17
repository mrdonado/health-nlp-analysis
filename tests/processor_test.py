"""
server_test.py
"""
import analyzer.processor
from unittest import mock


class MockAnalysisUploader(object):
    """
    Mock for the Analysis Uploader class
    """

    def __init__(self):
        pass

    def upload_analysis(self, analysis_json):
        assert analysis_json['analysis']['health_related'] == "true"
        assert analysis_json['user_name'] == "jdonado"
        assert analysis_json['user_description'] == "Some random radiologist."
        assert analysis_json['query'] == "diabetes"


@mock.patch('analyzer.engine')
def test_process_job(mock_engine):
    """ Testing the base route """
    example_job = {
        "user_name": "jdonado",
        "user_description": "Some random radiologist.",
        "created_at": "2017-04-02T22:35:04.868Z",
        "message": "Some random message",
        "source": "twitter",
        "query": "diabetes"
    }
    mock_uploader = MockAnalysisUploader()
    mock_engine.nlp_analysis.return_value = {
        "health_related": "true",
        "created_at": "2017-04-02T22:35:04.868Z",
        "profile": "radiologist",
        "problem": "diabetes",
        "solution": "aspirin"
    }
    analyzer.processor.process_job(example_job, mock_uploader)
    mock_engine.nlp_analysis.assert_called_once_with(example_job)
