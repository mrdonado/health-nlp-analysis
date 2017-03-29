"""
server_test.py
"""
import mock
import analyzer.processor

@mock.patch('analyzer.engine')
@mock.patch('analyzer.uploader')
def test_process_job(mock_uploader, mock_engine):
    """ Testing the base route """
    example_job = {"message": "Example message"}
    mock_engine.nlp_analysis.return_value = True
    analyzer.processor.process_job(example_job)
    mock_engine.nlp_analysis.assert_called_once_with('Example message')
    mock_uploader.upload_analysis.assert_called_once()

