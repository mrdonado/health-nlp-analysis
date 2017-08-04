"""
Example of a script performing an NLP analysis of a given message
"""
from datetime import datetime
from analyzer.engines import user_analyzer
from analyzer.engines import text_analyzer
## Initialization ##

# User analysis
DICTIONARY = user_analyzer.dictionary_parser(
    './language_data/user_dictionary.txt')
LEXICON = user_analyzer.lexicon_generator(
    './language_data/user_grammar.txt', DICTIONARY)
USER_NAME_PATTERNS = user_analyzer.user_name_parser(
    './language_data/user_name_patterns.txt')


# Text analysis
LANGUAGE_DATA = text_analyzer.language_data_loader(
    './language_data/grammar.txt',
    './language_data/start_words.txt',
    './language_data/stop_words.txt'
)


def nlp_analysis(job_json):
    """
    It takes a job as an input and returns an analysis.
    """
    analysis = dict()
    # Get 'profile' and 'health_related'
    analysis['profile'] = user_analyzer.user_analyzer(job_json['user_name'],
                                                    job_json['user_description'],
                                                    USER_NAME_PATTERNS,
                                                    LEXICON)[1]

    # Identified medical sources will be tagged as health related
    analysis['health_related'] = analysis['profile'] != '<no tag>'

    # The text analyzer inferes a health related problem and its solution,
    # when available
    text_analysis = text_analyzer.analyzer(job_json['message'],
                                           LANGUAGE_DATA['start_words'],
                                           LANGUAGE_DATA['grammar'],
                                           LANGUAGE_DATA['stop_words'])

    analysis['solution'] = text_analysis[0]
    analysis['problem'] = text_analysis[1]

    # Save the analysis timestamp
    analysis['created_at'] = datetime.now().isoformat()
    return analysis

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
        "health_related": "Doctor",
        "created_at": datetime.now().isoformat(),
        "profile": "radiologist",
        "problem": "diabetes",
        "solution": "aspirin"
    }
    return result
