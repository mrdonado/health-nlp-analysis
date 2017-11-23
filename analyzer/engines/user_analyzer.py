#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

###################
## User Analyzer ##
###################

This program receives 2 text inputs (user name and user description infor-
mation), and extracts key information from it to categorize the user profile,
according to a set of semantic tags.

"""

import re

# Auxiliar functions for User's description analysis:
# is_tag, dictionary_parser, lexicon_generator


def is_tag(value):
    """
    It identifies a value as tag
    A tag looks like this:
    <THIS_IS_A_TAG>

    These are not tags:
    <this is not a tag>
    <THIS IS NO TAG EITHER
    """
    pattern = re.compile("<[A-Z_]+>")
    return pattern.match(value)


def dictionary_parser(dictionary_file_path):
    """
    Create a dictionary of words (hospital, clinic) linked to nodes,
    e.g. <MEDICAL_PLACE>
    The input file 'user_dictionary.txt' should is as follows:
    (1 entry per line), e.g.
    <MEDICAL_PLACE> \t hospital
    <MEDICAL_PROFESSION> \t anesthesiologist
    """
    dictionary = dict()
    dictionary_file = open(dictionary_file_path, 'r')

    for line in dictionary_file:
        line = line.rstrip()
        (entry, definition) = line.split('\t')
        if entry not in dictionary.keys():
            dictionary[entry] = [definition]
        else:
            dictionary[entry].append(definition)

    dictionary_file.close()
    # The following loop reads dictionary's entries which have nodes inside,
    # e.g. <MEDICAL_JOB> \t <ADMINISTRATIVE_JOB>. It replaces the node for all
    # its words
    for (entry, values) in dictionary.items():
        nodes_with_variations = [value.split(
            '|') for value in values if is_tag(value)]
        for node_variations in nodes_with_variations:
            for insidenode in node_variations:
                if insidenode in dictionary.keys():
                    for definition in dictionary[insidenode]:
                        if definition not in dictionary[entry]:
                            dictionary[entry].append(definition)
                dictionary[entry].remove('|'.join(node_variations))
    return dictionary


def lexicon_generator(grammar_file_path, dictionary):
    """
    This function creates a set of lexical instances derived from the dictionary
    returned by dictionary_parser(), plus the set of pattern rules defined in 
    user_grammar.txt
    E.g.
        <MEDICAL_JOB> at <MEDICAL_PLACE>
        can generate:
        Anesthesiologist at Mayo Clinic
        Phisician at Hospital Gregorio Marañón
        etc.
    """
    generated_lexicon = dict()
    user_grammar_file = open(grammar_file_path, 'r')
    patterns = []
    for line in user_grammar_file:
        line = line.rstrip()
        patterns.append(line)
    user_grammar_file.close()
    for pattern_data in patterns:
        (pattern, semantic_tag) = pattern_data.split('\t')
        instance = pattern
        # (a) Pattern can have a node inside:
        if re.search(r'<\S+?>', pattern):
            node_list = re.findall(r'<\S+?>', pattern)
            for node in node_list:
                if node in dictionary.keys():
                    instance = re.sub(
                        node, '(' + '|'.join(dictionary[node]) + ')', instance)
            generated_lexicon[(pattern, semantic_tag)] = instance
        # (b) Pattern without node:
        else:
            generated_lexicon[(pattern, semantic_tag)] = instance
    return generated_lexicon

# Auxiliar functions for User's name analysis:
# user_name_parser, user_name_analysis,


def user_name_parser(user_name_patterns_path):
    '''
    Create a list of pattern expressions for user name's text. Each pattern
    has a corresponding semantic tag for user categorization. E.g.:
    , MD$  DOCTOR
    '''
    user_name_patterns = []
    user_name_file = open(user_name_patterns_path, 'r')
    for line in user_name_file:
        line = line.rstrip()
        (pattern, semantic_tag) = line.split('\t')
        user_name_patterns.append((pattern, semantic_tag))
    user_name_file.close()
    return user_name_patterns


def user_name_analysis(user_name, user_name_patterns):
    '''
    Analysis of user name's text. Given the text, this function maps user name pattern
    expressions into it. If found, it returns the list 'result', where:
    result[0] is the pattern found
    result[1] is the semantic tag linked to pattern
    '''
    result = []
    longest_match = ''
    matching_pattern_tuple = None
    for pattern_tuple in user_name_patterns:
        if re.search(pattern_tuple[0], user_name):
            possible_match = user_name[re.search(pattern_tuple[0], user_name).start(
            ):re.search(pattern_tuple[0], user_name).end()]
            if len(possible_match) > len(longest_match):
                longest_match = possible_match
                matching_pattern_tuple = pattern_tuple
    if len(longest_match) > 0:
        result.append(matching_pattern_tuple[0])
        result.append(matching_pattern_tuple[1])
        return result
    else:
        return None


# Analyzer:

def user_analyzer(user_name, user_description, user_name_patterns, lexicon):
    """
    This function performs a two-steps analysis to get a user profile categorization.
    The first step is to analyze the user name's text. If patterns are found, it returns
    the result and does not go further. If not, it proceeds with a second analysis on
    the user description's text, and try to give results on the same format.

    This function's outcome is the list 'user_analyzer_result', where:
    user_analyzer_result[0] is the pattern found
    user_analyzer_result[1] is the semantic tag linked to pattern
    """

    user_analyzer_result = []

    # Analysis on the user name's text:
    user_name_analysis_result = user_name_analysis(
        user_name, user_name_patterns)
    if user_name_analysis_result is not None:
        user_analyzer_result.append(user_name_analysis_result[0])
        user_analyzer_result.append(user_name_analysis_result[1])
        user_analyzer_result.append('<from Name>')

    # Analysis on the user description's text:
    if len(user_analyzer_result) == 0:
        longest_match = ''
        matching_pattern_tuple = None
        matching_instance = None
        all_pattern_tuples = dict()
        for pattern_tuple, instance in lexicon.items():
            if re.search(instance, user_description):
                if pattern_tuple[1] not in all_pattern_tuples.keys():
                    all_pattern_tuples[pattern_tuple[1]] = pattern_tuple[0]
                possible_match = user_description[re.search(instance, user_description).start(
                ):re.search(instance, user_description).end()]
                if len(possible_match) > len(longest_match):
                    longest_match = possible_match
                    matching_pattern_tuple = pattern_tuple
                    matching_instance = instance
        if len(longest_match) > 0:
            # We give preference to the following semantic tags, following this
            # order:
            if 'Doctor' in all_pattern_tuples.keys():
                user_analyzer_result.append(all_pattern_tuples['Doctor'])
                user_analyzer_result.append('Doctor')
                user_analyzer_result.append('<from Description>')
            elif 'Academia' in all_pattern_tuples.keys():
                user_analyzer_result.append(all_pattern_tuples['Academia'])
                user_analyzer_result.append('Academia')
                user_analyzer_result.append('<from Description>')
            elif 'Patient' in all_pattern_tuples.keys():
                user_analyzer_result.append(all_pattern_tuples['Patient'])
                user_analyzer_result.append('Patient')
                user_analyzer_result.append('<from Description>')
            elif 'Institution' in all_pattern_tuples.keys():
                user_analyzer_result.append(all_pattern_tuples['Institution'])
                user_analyzer_result.append('Institution')
                user_analyzer_result.append('<from Description>')
            elif 'Journal' in all_pattern_tuples.keys():
                user_analyzer_result.append(all_pattern_tuples['Journal'])
                user_analyzer_result.append('Journal')
                user_analyzer_result.append('<from Description>')
            elif 'News source' in all_pattern_tuples.keys():
                user_analyzer_result.append(all_pattern_tuples['News source'])
                user_analyzer_result.append('News source')
                user_analyzer_result.append('<from Description>')
            else:
                user_analyzer_result.append(matching_pattern_tuple[0])
                user_analyzer_result.append(matching_pattern_tuple[1])
                user_analyzer_result.append('<from Description>')
        else:
            user_analyzer_result.append('<no pattern>')
            user_analyzer_result.append('<no tag>')
            user_analyzer_result.append('<no name/description>')

    return user_analyzer_result


# Test message! #####
# def test_message():
#     user_name = raw_input('\n' + 'User name? ')
#     user_description = raw_input('\n' + 'User description? ')
#     DICTIONARY = dictionary_parser(
#     '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_dictionary.txt')
#     LEXICON = lexicon_generator(
#     '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_grammar.txt', DICTIONARY)
#     USER_NAME_PATTERNS = user_name_parser(
#     '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_name_patterns.txt')
#     result = user_analyzer(user_name, user_description, USER_NAME_PATTERNS, LEXICON)
#     print '\n'+'<'+result[1]+'>'+'\t'+'['+result[0]+']' + '\t' + result[2]

#     control = raw_input('(t)ry again ?')
#     while control == "t":
#         DICTIONARY = dictionary_parser(
#         '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_dictionary.txt')
#         LEXICON = lexicon_generator(
#         '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_grammar.txt', DICTIONARY)
#         USER_NAME_PATTERNS = user_name_parser(
#         '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_name_patterns.txt')
#         result = user_analyzer(user_name, user_description, USER_NAME_PATTERNS, LEXICON)
#         print '<m>'+user_name+'\t'+user_description+'</m>'
#         print '\n'+'<'+result[1]+'>'+'\t'+'['+result[0]+']' + '\t' + result[2]

#         control = raw_input('(t)ry again ?')
#     else:
#         test_message()

# test_message()

###### Test set of messages ################

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

# DICTIONARY = dictionary_parser('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_dictionary.txt')
# LEXICON = lexicon_generator('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_grammar.txt', DICTIONARY)
# USER_NAME_PATTERNS = user_name_parser('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_name_patterns.txt')


# def call_text_analyzer(message):
#     from text_analyzer import analyzer
#     from text_analyzer import language_data_loader
#     LANGUAGE_DATA = language_data_loader('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/grammar.txt',
#     '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/counter_grammar.txt',
#     '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt', 
#     '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/stop_words.txt')
#     message = unicode(message)
#     result = analyzer(message, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['counter_grammar'], LANGUAGE_DATA['stop_words'])
#     print result[0], result[1]

# messagesf = open('mensajes.txt', 'r')
# messages = []
# for line in messagesf:
#     line = line.rstrip()
#     messages.append(line)

# for line in messages:
#     input_text = line.split('\t')
#     user_name = input_text[0]
#     user_description = input_text[1]
#     message = input_text[2]
#     result = user_analyzer(user_name, user_description, USER_NAME_PATTERNS, LEXICON)
#     print 'User Name: ', user_name
#     print 'Description: ', '[', result[1], '] ', user_description
#     print 'Message: ', message
#     print '-----'
#     call_text_analyzer(message)
#     print result

