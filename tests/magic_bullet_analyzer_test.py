#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Magic bullet analyzer tests.
"""
from analyzer.engines import magic_bullet_analyzer
import re
from spacy.en import English
NLP = English()



def test_enlarge_message():

    result = magic_bullet_analyzer.enlarge_message('This is one message.')
    assert result == 'Pretty tinny long short yellow dummy. This is one message. Pretty tinny long short yellow dummy'

    result = magic_bullet_analyzer.enlarge_message('This is another message')
    assert result == 'Pretty tinny long short yellow dummy. This is another message. Pretty tinny long short yellow dummy'


def test_get_magic_bullet_instance_and_type():

    result = magic_bullet_analyzer.get_magic_bullet_instance_and_type('[np = treatment]')
    assert result == ['treatment', 'case A']

    result = magic_bullet_analyzer.get_magic_bullet_instance_and_type('[npl]is the treatment')
    assert result == ['(\S+ ){4}is the treatment', 'case B']

    result = magic_bullet_analyzer.get_magic_bullet_instance_and_type('the treatment is[npr]')
    assert result == ['the treatment is( \S+){4}', 'case C']


def test_get_string_match_plus_noun_phrases():

    magic_bullet_instance = 'treatment'
    start_word = 'obesity'
    noun_phrases = []

    message = 'Magic treatment is now available for obesity'

    result = magic_bullet_analyzer.get_string_match_plus_noun_phrases(magic_bullet_instance, start_word, noun_phrases, message)
    assert result == ['Magic treatment', ['Magic treatment', 'obesity']]



def test_get_regex_match():

    magic_bullet_instance = '(\S+ ){4}is the treatment'
    message = 'A new wonderful medicine is the treatment available in obesity'

    result = magic_bullet_analyzer.get_regex_match(magic_bullet_instance, message)
    assert result == 'A new wonderful medicine is the treatment'



def test_magic_bullet_analyzer():

    start_word = 'obesity'
    magic_bullet_grammar = [
        '[np = surgery]',
        '[npl]protect\w*( \w+){0,5} against',
        'analgesic \w+ of[npr]' ]
    stop_words = [
        'dummy']
    
    message = 'This medicine protects you against obesity'
    result = magic_bullet_analyzer.magic_bullet_analyzer(message, start_word, magic_bullet_grammar, stop_words)
    assert result == [
        'This medicine',
        'obesity',
        '[npl]protect\w*( \w+){0,5} against'
    ]

    message = 'Big surgery in obesity now'
    result = magic_bullet_analyzer.magic_bullet_analyzer(message, start_word, magic_bullet_grammar, stop_words)
    assert result == [
        'Big surgery',
        'obesity',
        '[np = surgery]'
    ]

    message = 'obesity and the analgesic power of this new medicine'
    result = magic_bullet_analyzer.magic_bullet_analyzer(message, start_word, magic_bullet_grammar, stop_words)
    assert result == [
        'this new medicine',
        'obesity',
        'analgesic \w+ of[npr]'
    ]