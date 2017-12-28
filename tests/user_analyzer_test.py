# -*- coding: utf-8 -*-
"""
Test the user analyzer engine
"""
from analyzer.engines import user_analyzer

USER_DICTIONARY = './tests/engines/demo_user_dictionary.txt'
USER_GRAMMAR = './tests/engines/demo_user_grammar.txt'
STRING_TWITTER_QUERIES = './tests/engines/demo_string_twitter_queries.txt'


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
                       ('(?i)^physicist', 'Doctor'): '(?i)^physicist'}


def test_string_twitter_queriesParser():
    """
    Generate a demo Twitter query list from a demo Twitter query file
    """
    
    string_twitter_queries = user_analyzer.string_twitter_queriesParser(STRING_TWITTER_QUERIES)

    assert string_twitter_queries == ['physicist', 'Physicist', 'PHYSICIST']


def test_user_description_HasQuery():
    """
    Test the user_description_HasQuery function
    """
    
    string_twitter_queries = user_analyzer.string_twitter_queriesParser(STRING_TWITTER_QUERIES)

    user_description = 'I am Justin Bieber'
    result = user_analyzer.user_description_HasQuery(user_description, string_twitter_queries)
    assert result is False

    user_description = 'Physicist, father, runner'
    result = user_analyzer.user_description_HasQuery(user_description, string_twitter_queries)
    assert result is True


def test_user_name_analysis():
    """
    Test the user_name_analysis function
    """
    
    user_name = 'John Paul, MD'
    result = user_analyzer.user_name_analysis(user_name)
    assert result == [', MD', 'Doctor']

    user_name = 'johnpaulMD'
    result = user_analyzer.user_name_analysis(user_name)
    assert result == ['MD', 'Doctor']

    user_name = 'johnpauLMD'
    result = user_analyzer.user_name_analysis(user_name)
    assert result == None


def test_user_analyzer():
    """
    Test the user analyzer function
    """
    dictionary = user_analyzer.dictionary_parser(USER_DICTIONARY)
    lexicon = user_analyzer.lexicon_generator(USER_GRAMMAR, dictionary)
    string_twitter_queries = user_analyzer.string_twitter_queriesParser(
        STRING_TWITTER_QUERIES)

    assert user_analyzer.user_analyzer('Mr. Proper',
                                       'Some random person',
                                       string_twitter_queries,
                                       lexicon) == [
                                           '<no pattern>',
        '<no tag>',
        '<no name/description>']

    assert user_analyzer.user_analyzer('Doctor Proper',
                                       'Physicist and father',
                                       string_twitter_queries,
                                       lexicon) == ['(?i)^physicist', 'Doctor', '<from Description>']