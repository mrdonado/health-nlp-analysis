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
                    instanced_node = '(' + '|'.join(dictionary[node]) + ')'
                    instance = instance.replace(node, instanced_node)
            generated_lexicon[(pattern, semantic_tag)] = instance
        # (b) Pattern without node:
        else:
            generated_lexicon[(pattern, semantic_tag)] = instance
    return generated_lexicon


def string_twitter_queriesParser(string_twitter_queries_path):
    """
    Read a file with all Twitter queries' possible variations (all lower, all caps,
    upper initial). Store them into a list.
    """
    string_twitter_queries = []
    string_twitter_queries_file = open(string_twitter_queries_path, 'r')
    for line in string_twitter_queries_file:
        line = line.rstrip()
        string_twitter_queries.append(line)
    string_twitter_queries_file.close()

    return string_twitter_queries



def user_description_HasQuery(user_description, string_twitter_queries):
    """
    Helper function of user_analyzer(). If a Twitter query is not present in a user
    description text, user_analyzer() doesn't go further to save time processing.
    """
    
    result = False

    for string_twitter_query in string_twitter_queries:
        if string_twitter_query in str(user_description):
            result = True
            break
    
    return result



def user_name_analysis(user_name):
    """
    Analysis of user name's text. Given the text, this function maps a set of
    simple string patterns into it. If found, it returns the list 'result',
    where:
    result[0] is the pattern found
    result[1] is the semantic tag linked to pattern
    """

    result = []
    user_name_end_pos = len(user_name) - 1

    if ', MD' in user_name[user_name_end_pos -4:]:
        result.append(', MD')
        result.append('Doctor')
        return result
    elif ',MD' in user_name[user_name_end_pos -3:]:
        result.append(',MD')
        result.append('Doctor')
        return result
    elif ', GP' in user_name[user_name_end_pos -4:]:
        result.append(', GP')
        result.append('Doctor')
        return result
    elif ',GP' in user_name[user_name_end_pos -3:]:
        result.append(',GP')
        result.append('Doctor')
        return result
    elif 'MD' in user_name[user_name_end_pos -2:] and user_name[user_name_end_pos -4:user_name_end_pos -1:].islower():
        result.append('MD')
        result.append('Doctor')
        return result
    elif 'GP' in user_name[user_name_end_pos -2:] and user_name[user_name_end_pos -4:user_name_end_pos -1:].islower():
        result.append('GP')
        result.append('Doctor')
        return result
    elif 'Dr' in user_name[0:2] and user_name[2].isupper():
        result.append('Dr')
        result.append('Doctor')
        return result
    else:
        return None



# Analyzer:

def user_analyzer(user_name, user_description, string_twitter_queries, lexicon):
    """
    This function performs a two-steps analysis to get a user profile categorization.
    The first step is to analyze the user name's text. If patterns are found, it returns
    the result and does not go further. If not, it proceeds with a second analysis on
    the user description's text, and tries to give results on the same format.

    This function's outcome is the list 'user_analyzer_result', where:
    user_analyzer_result[0] is the pattern found
    user_analyzer_result[1] is the semantic tag linked to pattern
    """

    user_analyzer_result = []

    # Before the analysis, look for queries in the user description's text.
    # If queries are not present, no analysis is performed to save time processing.

    HasQuery = user_description_HasQuery(user_description, string_twitter_queries)
    if HasQuery is False:
        user_analyzer_result.append('<no pattern>')
        user_analyzer_result.append('<no tag>')
        user_analyzer_result.append('<no name/description>')
    else:

        # User analysis process
        # 1) Analysis on the user name's text:

        user_name_analysis_result = user_name_analysis(user_name)
        if user_name_analysis_result is not None:
            user_analyzer_result.append(user_name_analysis_result[0])
            user_analyzer_result.append(user_name_analysis_result[1])
            user_analyzer_result.append('<from Name>')
        else:

            # 2) Analysis on the user description's text:
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
                # We give preference to the following semantic tags,
                # following this order:
                if 'Doctor' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Doctor'])
                    user_analyzer_result.append('Doctor')
                    user_analyzer_result.append('<from Description>')
                elif 'Academia' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Academia'])
                    user_analyzer_result.append('Academia')
                    user_analyzer_result.append('<from Description>')
                elif 'Publishing source' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Publishing source'])
                    user_analyzer_result.append('Publishing source')
                    user_analyzer_result.append('<from Description>')
                elif 'Institution' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Institution'])
                    user_analyzer_result.append('Institution')
                    user_analyzer_result.append('<from Description>')
                elif 'Association' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Association'])
                    user_analyzer_result.append('Association')
                    user_analyzer_result.append('<from Description>')
                elif 'Professional' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Professional'])
                    user_analyzer_result.append('Professional')
                    user_analyzer_result.append('<from Description>')
                elif 'News source' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['News source'])
                    user_analyzer_result.append('News source')
                    user_analyzer_result.append('<from Description>')
                elif 'Healthcare initiative' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Healthcare initiative'])
                    user_analyzer_result.append('Healthcare initiative')
                    user_analyzer_result.append('<from Description>')
                elif 'Patient' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Patient'])
                    user_analyzer_result.append('Patient')
                    user_analyzer_result.append('<from Description>')
                elif 'Med Business' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Med Business'])
                    user_analyzer_result.append('Med Business')
                    user_analyzer_result.append('<from Description>')
                elif 'Interested in healthcare' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Interested in healthcare'])
                    user_analyzer_result.append('Interested in healthcare')
                    user_analyzer_result.append('<from Description>')
                elif 'Generic' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['Generic'])
                    user_analyzer_result.append('Generic')
                    user_analyzer_result.append('<from Description>')
                elif '<no tag>' in all_pattern_tuples.keys():
                    user_analyzer_result.append(all_pattern_tuples['<no tag>'])
                    user_analyzer_result.append('<no tag>')
                    user_analyzer_result.append('<from Description>')                
            else:
                user_analyzer_result.append('<no pattern>')
                user_analyzer_result.append('<no tag>')
                user_analyzer_result.append('<no name/description>')

    return user_analyzer_result