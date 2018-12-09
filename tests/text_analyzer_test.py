#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text analyzer tests.
"""
from analyzer.engines import text_analyzer

START_WORDS_PATH = './tests/engines/demo_start_words.txt'
STOP_WORDS_PATH = './tests/engines/demo_stop_words.txt'
GRAMMAR_PATH = './tests/engines/demo_grammar.txt'
COUNTER_GRAMMAR_PATH = './tests/engines/demo_counter_grammar.txt'


def test_file_parser():
    """
    File parser tests.
    """
    start_words = text_analyzer.file_parser(START_WORDS_PATH, True)
    assert 'negativity' in start_words
    assert 'pci' in start_words
    assert r'acute \w+' in start_words
    assert 'eczema' in start_words
    assert 'wrinkles' in start_words
    assert 'yeast infections' in start_words
    assert 'wrinkless' not in start_words
    assert 'invented_word' not in start_words


def test_start_words_to_dict():
    """
    start_words_to_dict() test
    """

    start_words = ['blue toothache', 'black toothache', 'blue backpain', 'black backpain']
    result = text_analyzer.start_words_to_dict(start_words)
    assert result == {'blue': ['blue toothache', 'blue backpain'], 'toothache': ['blue toothache', 'black toothache'], 'black': ['black toothache', 'black backpain'], 'backpain': ['blue backpain', 'black backpain']}


def test_language_data_loader():
    """
    Language data loader tests
    """
    language_data = text_analyzer.language_data_loader(
        GRAMMAR_PATH,
        COUNTER_GRAMMAR_PATH,
        START_WORDS_PATH,
        STOP_WORDS_PATH)
    assert 'eczema' in language_data['start_words'].keys()
    assert '^@\\w+$' in language_data['stop_words']
    assert '[s] \\w+ed to (healthier|better)( \\S+){0,7} [p]' in language_data['grammar']
    assert 'chances for ( \S+){0,5} [p]' in language_data['counter_grammar']
    assert r'[s] effective( \w+){0,2} (in|for|to)( \w+){0,5} [p]' in language_data['grammar']


def test_start_word_match():
    """
    Start word match tests
    """
    result = text_analyzer.start_word_match("Some input message",
                                            {'disease': ['acute disease', 'hard disease']})
    assert result is None
    result = text_analyzer.start_word_match("Hard disease to treat",
                                            {'disease': ['acute disease', 'hard disease']})
    assert result == 'Hard disease'

def test_get_start_word_from_sentence():
    """
    Start word from sentence tests
    """
    result = text_analyzer.get_start_word_from_sentence("This is one-sentence message without a start word",
                                                        {'disease': ['acute disease', 'hard disease']})
    assert result is None
    result = text_analyzer.get_start_word_from_sentence("This is the first sentence, and in the second you can find acute disease",
                                                        {'disease': ['acute disease', 'hard disease']})
    assert result[0] == 'acute disease'
    assert result[1] == 'and in the second you can find acute disease'


def test_counter_analyzer():
    """
    Counter analyzer tests
    """
    language_data = text_analyzer.language_data_loader(
        GRAMMAR_PATH,
        COUNTER_GRAMMAR_PATH,
        START_WORDS_PATH,
        STOP_WORDS_PATH)
    message = "A new medicine for obesity"
    analysis = text_analyzer.counter_analyzer(message,
                                      'obesity',
                                      language_data['counter_grammar'])
    assert analysis is False


def test_get_noun_phrase():
    """
    get_noun_phrase() test
    """

    message = 'Farma labs develop a new device for diabetes'
    longest_match = 'for diabetes'
    position = 'sp'
    result = text_analyzer.get_noun_phrase(message, longest_match, position, ['random stop word'])
    assert result == 'a new device'

    message = 'Diabetes is now treated with a new device that Farma labs have created'
    longest_match = 'Diabetes is now treated with'
    position = 'ps'
    result = text_analyzer.get_noun_phrase(message, longest_match, position, ['random stop word'])
    assert result == 'a new device'

    message = 'were for diabetes'
    longest_match = 'for diabetes'
    position = 'sp'
    result = text_analyzer.get_noun_phrase(message, longest_match, position, ['random stop word'])
    assert result == None


def test_check_if_problem_in_solution():
    result = text_analyzer.check_if_problem_in_solution('stop eating', 'obesity')
    assert result is None

    result = text_analyzer.check_if_problem_in_solution('obesity medicine', 'obesity')
    assert result is True

    result = text_analyzer.check_if_problem_in_solution('#obesity', 'obesity')
    assert result is True


def test_analyzer():
    """
    Analyzer tests
    """
    language_data = text_analyzer.language_data_loader(
        GRAMMAR_PATH,
        COUNTER_GRAMMAR_PATH,
        START_WORDS_PATH,
        STOP_WORDS_PATH)
    message = "This is a new medicine for hyperthyroidism"
    #  \
    #     "and helps fight against diabetes, cancer + heart disease. " \
    #     "https://t.co/sw6mvsslg"
    analysis = text_analyzer.analyzer(message,
                                      language_data['start_words'],
                                      language_data['grammar'],
                                      language_data['counter_grammar'],
                                      language_data['stop_words'],
                                      language_data['magic_bullet_grammar'])
    assert analysis[1] == 'hyperthyroidism'
    assert analysis[0] == 'a new medicine'
    message = "some unrelated message that only talks about watching tv"
    analysis = text_analyzer.analyzer(message,
                                      language_data['start_words'],
                                      language_data['grammar'],
                                      language_data['counter_grammar'],
                                      language_data['stop_words'],
                                      language_data['magic_bullet_grammar'])
    assert analysis[0] == '<nothing_found>'
    message = "#hyperthyroidism for hyperthyroidism"
    analysis = text_analyzer.analyzer(message,
                                      language_data['start_words'],
                                      language_data['grammar'],
                                      language_data['counter_grammar'],
                                      language_data['stop_words'],
                                      language_data['magic_bullet_grammar'])
    assert analysis[0] == '<nothing_found>'
    assert analysis[1] == 'hyperthyroidism'
