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
        pass

@mock.patch('analyzer.engine')
def test_process_job(mock_engine):
    """ Testing the base route """
    example_job = {"message": "Example message"}
    mock_uploader = MockAnalysisUploader()
    mock_engine.nlp_analysis.return_value = True
    analyzer.processor.process_job(example_job, mock_uploader)
    mock_engine.nlp_analysis.assert_called_once_with('Example message')
