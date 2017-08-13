# -*- coding: utf-8 -*-
"""
Test the user analyzer engine
"""
from analyzer.engines import user_analyzer

USER_DICTIONARY = './tests/engines/demo_user_dictionary.txt'
USER_GRAMMAR = './tests/engines/demo_user_grammar.txt'


def test_is_tag():
    """
    Test tag identification
    """
    # Valid tags
    assert user_analyzer.is_tag('<THIS_IS_A_TAG>')
    assert user_analyzer.is_tag('<TAG>')
    # Invalid tags
    assert not user_analyzer.is_tag('<THIS_I _A_TAG>')
    assert not user_analyzer.is_tag('<this is no tag>')
    assert not user_analyzer.is_tag('<SOME_INVALID_TAG')


def test_dictionary_parser():
    """
    Parse a demo dictionary
    """
    dictionary = user_analyzer.dictionary_parser(USER_DICTIONARY)
    assert dictionary['<DISEASE>'] == ['liver cancer']
    assert dictionary['<MEDICAL_FIELD>'] == ['family medicine', 'biotech']
    assert dictionary['<MEDICAL_ATTRIBUTE>'] == ['family medicine', 'biotech']
    assert dictionary['<MEDICAL_JOB>'] == ['physicist', 'dermat(ó|o)log(o|a)']


def test_lexicon_generator():
    """
    Generate a demo lexicon from a demo grammar file
    """

    dictionary = user_analyzer.dictionary_parser(USER_DICTIONARY)
    lexicon = user_analyzer.lexicon_generator(USER_GRAMMAR,
                                              dictionary)
    assert lexicon == {('(?i)(;|,|\\.) practitioner', 'Doctor'): '(?i)(;|,|\\.) practitioner',
                       ('(?i)^practitioner', 'Doctor'): '(?i)^practitioner',
                       ('(?i)nurse clinician', 'Professional'): '(?i)nurse clinician',
                       ('(?i)peer reviewed', 'Source'): '(?i)peer reviewed'}


def test_user_analyzer():
    """
    Test the user analyzer function
    """
    dictionary = user_analyzer.dictionary_parser(USER_DICTIONARY)
    lexicon = user_analyzer.lexicon_generator(USER_GRAMMAR, dictionary)

    assert user_analyzer.user_analyzer('Some random person',
                                       lexicon) == ['<no pattern>',
                                                    '<unknown source>']
    assert user_analyzer.user_analyzer('Some physicist and father',
                                       lexicon) == ['¡<MEDICAL_JOB>¡ (and|&) \\w+',
                                                    'physicist']
    assert user_analyzer.user_analyzer('family medicine website',
                                       lexicon) == ['¡<MEDICAL_ATTRIBUTE> (web|portal|site)¡',
                                                    'family medicine web']
