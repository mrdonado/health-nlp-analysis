#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

##############
## Analyzer ##
##############

Given a grammar, and a set of start words and end words, this
file provides with the tools to analyze a human text written in
English.

The analyzer receives a text input (message), and extracts valuable
information from it within the DISEASE-TREATMENT cognitive frame, i.e. a
disease and a potential solution for it.

It consists of 3 functions: (1) language_data_loader loads
linguistic knowledge to feed the Analyzer (a simple NLP engine), (2)
start_word_match finds disease mentions in the incoming text message,
(3) Analyzer uses information from previous inputs to extract entities
(syntactically, noun phrases) that semantically express solutions for a
mentioned disease.

"""
import re
from spacy.en import English
# Function for text processing with Spacy
NLP = English()

def file_parser(path, to_lower):
    """
    Helper function to parse text files.
    """
    input_file = open(path, 'r')
    results = []
    for line in input_file:
        line = line.strip()
        if to_lower:
            line = line.lower()
        results.append(line)
    input_file.close()
    return results


def language_data_loader(grammar_path, start_words_path, stop_words_path):
    """
    It receives three file paths as input:
    - Grammar
    - Start words
    - Stop words
    Then it parses them and returns an array with their contents
    altogether.
    """
    language_data = dict()
    # Load grammar
    language_data['grammar'] = file_parser(grammar_path, False)
    # Load start words (a term list to recover messages on diseases)
    language_data['start_words'] = file_parser(start_words_path, True)
    # Load stop words (words tagged as noun phrases that cannot be extracted
    # as entities (e.g. You, @username11):
    language_data['stop_words'] = file_parser(stop_words_path, True)
    return language_data


def start_word_match(message, start_words):
    """
    'start word' finder: it looks for start words within a given message.
    Start words might be regular expressions.
    When a match is found, the whole match will be returned. Otherwise,
    None is returned.
    """
    start_word = None
    for word in start_words:
        if re.search(word, message):
            current_word = message[re.search(word, message).start():
                                   re.search(word, message).end()]
            if start_word is None or len(current_word) > len(start_word):
                start_word = current_word
    # we search for the longest match ('Mindfulness for anorexia nervosa' gets
    # 'anorexia nervosa' but not 'anorexia', although both are disease terms)
    return start_word


def analyzer(message, start_words, stop_words, grammar):
    """
    Analyzer (treatment-entity finder)
    The input grammar follows two basic syntactic schemes,
    where X = treatment/solution and Y = disease/problem:
    (a) X to treat Y -> X comes first,
    (b) Y treated with X -> Y comes first.
    """
    # Find the start word in message:
    start_word = start_word_match(message, start_words) or ''
    twitter_start_word = '(' + '#' + start_word + '|' + start_word + ')'
    # Necessary variables:
    longest_match = ''
    matching_pattern = ''
    output = []
    np_list = []
    # First, check if start_word is in message
    if start_word != None:
        # For every stored grammar rule, generate its counterpart including the
        # start word (e.g. '[s] for [p]' -> '[s] for anorexia')
        for pattern in grammar:
            instance = pattern.replace('[p]', twitter_start_word)
            instance = re.sub(r'\s*\[s\]\s*', '', instance)
            # Test every rule against the message:
            if re.search(instance, message):
                found_instance = instance
                match = message[re.search(found_instance, message).start(
                ):re.search(found_instance, message).end() + 1]
                # Find the rule with the longest match in the string:
                if len(match) > len(longest_match):
                    longest_match = match
                    matching_pattern = pattern
        # Rule matchs if 'longest_match' contains a string
        if len(longest_match) > 0:
            # The matching rule has the structure: S before P, where S is a
            # string potentially including the treatment entity
            if matching_pattern.find('[s]') < matching_pattern.find('[p]'):
                target_match = message[:message.find(longest_match)]
                # target_match = unicode(target_match, "utf-8" )
                if len(target_match) >= 3:
                    # # Search NPs within target_match (target string):
                    for noun_phrase in NLP(target_match).noun_chunks:
                        np_list.append(noun_phrase)
                    if len(np_list) > 0:
                        # Avoid the NP (noun phrase), if it's a stop word (e.g.
                        # You)
                        forbidden_np = False
                        for stop_word in stop_words:
                            if re.search(stop_word, str(np_list[-1])):
                                forbidden_np = True
                        if forbidden_np is False:
                            # Include start_word and NP in a list named
                            # 'ouput'. Choose the latest NP from the target
                            # string (e.g. 'This treatment is a medicine...'
                            # gets 'medicine' but not 'treatment')
                            np_outcome = str(np_list[-1])
                            output.append(np_outcome)
                            output.append(start_word)
                            output.append(matching_pattern)
                            return output
                    # output.append(target_match)
                    # output.append(start_word)
                    # output.append(matching_pattern)
                    # return output
            # The matching rule has the structure: P before S:
            elif matching_pattern.find('[s]') > matching_pattern.find('[p]'):
                target_match = message[message.find(
                    longest_match) + len(longest_match):]
                if len(target_match) >= 3:
                    for noun_phrase in NLP(target_match).noun_chunks:
                        np_list.append(noun_phrase)
                    if len(np_list) > 0:
                        forbidden_np = False
                        for stop_word in stop_words:
                            if re.search(stop_word, str(np_list[0])):
                                forbidden_np = True
                        if forbidden_np is False:
                            # Choose the first NP from the target string (e.g.
                            # 'treated by a medicine from the shop', gets
                            # 'medicine' but not 'shop')
                            np_outcome = str(np_list[0])
                            output.append(np_outcome)
                            output.append(start_word)
                            output.append(matching_pattern)
                            return output
                    # output.append(target_match)
                    # output.append(start_word)
                    # output.append(matching_pattern)
                    # return output
    if len(output) == 0:
        output.append('<nothing_found>')
        output.append(start_word)
        output.append('<no pattern found>')
        return output
