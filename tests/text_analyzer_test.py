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


def test_language_data_loader():
    """
    Language data loader tests
    """
    language_data = text_analyzer.language_data_loader(
        GRAMMAR_PATH,
        COUNTER_GRAMMAR_PATH,
        START_WORDS_PATH,
        STOP_WORDS_PATH)
    assert 'eczema' in language_data['start_words']
    assert '^@\\w+$' in language_data['stop_words']
    assert '[s] \\w+ed to (healthier|better)( \\S+){0,7} [p]' in language_data['grammar']
    assert 'risk for( \S+){0,5} [p]' in language_data['counter_grammar']
    assert r'[s] effective( \w+){0,2} (in|for|to)( \w+){0,5} [p]' in language_data['grammar']


def test_start_word_match():
    """
    Start word match tests
    """
    result = text_analyzer.start_word_match("Some input message",
                                            ['one', 'word'])
    assert result is None
    result = text_analyzer.start_word_match("Some input message",
                                            ['input', 'word'])
    assert result == 'input'
    result = text_analyzer.start_word_match(
        "Some input message about anorexia nervosa and other things",
        ['one', 'word', 'anorexia', 'unrelated', 'anorexia nervosa'])
    assert result == 'anorexia nervosa'


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
                                      language_data['stop_words'])
    assert analysis[1] == 'hyperthyroidism'
    assert analysis[0] == 'a new medicine'
    message = "some unrelated message that only talks about watching tv"
    analysis = text_analyzer.analyzer(message,
                                      language_data['start_words'],
                                      language_data['grammar'],
                                      language_data['counter_grammar'],
                                      language_data['stop_words'])
    assert analysis[0] == '<nothing_found>'
