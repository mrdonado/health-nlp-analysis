#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from spacy.en import English
NLP = English()



def enlarge_message(message):

    dummy_context = 'Pretty tinny long short yellow dummy'

    if message.endswith('.'):
        message = dummy_context + '. ' + message + ' ' + dummy_context
    else:
        message = dummy_context + '. ' + message + '. ' + dummy_context

    return message


def get_magic_bullet_instance_and_type(pattern):

    result = []
    magic_bullet_instance = None
    magic_bullet_type = None

    if '[np = ' in pattern:
    # e.g. '[np = treatment] as in Dexamethasone treatment'
        magic_bullet_instance = pattern.replace('[np = ', '').replace(']', '')
        magic_bullet_type = 'case A'
    elif '[npl]' in pattern:
    # e.g. '[npl]is the treatment'
        magic_bullet_instance = pattern.replace('[npl]', '(\S+ ){4}')
        magic_bullet_type = 'case B'
    elif '[npr]' in pattern:
    # e.g. 'the treatment is[npr]'
        magic_bullet_instance = pattern.replace('[npr]', '( \S+){4}')
        magic_bullet_type = 'case C'
    
    result.append(magic_bullet_instance)
    result.append(magic_bullet_type)
    return result


def get_string_match_plus_noun_phrases(magic_bullet_instance, start_word, noun_phrases, message):

    result = [None, noun_phrases]
    
    forbidden_tokens = [
        'the',
        'new',
        'its',
        'our',
        'her',
        'his',
        'my',
        'your',
        'which',
        'and'
    ]
    
    if magic_bullet_instance in message.lower():
        if len(noun_phrases) == 0:
            for np in NLP(message).noun_chunks:
                np = np.text
                noun_phrases.append(np)
        for np in noun_phrases:
            if magic_bullet_instance in np.lower():
                if np.split()[-1].lower() == magic_bullet_instance:
                    if len(np.split()) > 1:
                        penultimate_token = np.split()[len(np.split())-2].lower()
                        from_first_to_penultimate_tokens = ' '.join(np.split()[0:-1])
                        # First exception: 'Frontal Fybrosing Alopecia treatment' is not a valid solution
                        if start_word.lower() == from_first_to_penultimate_tokens.lower():
                            continue
                        # Second exception: 'New treatment' is not a valid solution
                        elif len(np.split()) == 2 and penultimate_token in forbidden_tokens:
                                continue
                        else:
                            result[0] = np
                            break
    
    return result


def get_regex_match(magic_bullet_instance, message):

    result = None

    magic_bullet_instance = re.compile(str(magic_bullet_instance), flags=re.IGNORECASE)

    search_regex = re.search(magic_bullet_instance, message)
    if search_regex is not None:
        match = message[search_regex.start():search_regex.end()]
        result = match

    return result


def magic_bullet_analyzer(message, start_word, magic_bullet_grammar, stop_words):

    message = enlarge_message(message)
    noun_phrases = []
    matching_pattern = None
    longest_match = ''
    type_of_longest_match = None
    output = []

    for pattern in magic_bullet_grammar:

        instance_and_type = get_magic_bullet_instance_and_type(pattern)

        if instance_and_type[1] == 'case A':
            result = get_string_match_plus_noun_phrases(instance_and_type[0], start_word, noun_phrases, message)
            match = result[0]
            type_of_match = 'case A'
        else:
            match = get_regex_match(instance_and_type[0], message)
            type_of_match = instance_and_type[1]
        
        if match is not None:
            if type_of_match == 'case A':
                if len(noun_phrases) == 0:
                    noun_phrases = result[1]
            if len(match) > len(longest_match):
                longest_match = match
                type_of_longest_match = type_of_match
                matching_pattern = pattern

    if type_of_longest_match == 'case A':
        output.append(longest_match)
        output.append(start_word)
        output.append(matching_pattern)
    
    elif type_of_longest_match == 'case B':
        if len(noun_phrases) == 0:
            for np in NLP(message).noun_chunks:
                np = np.text
                noun_phrases.append(np)
        pattern_context = matching_pattern.replace('[npl]', '')
        target_longest_match = re.sub(pattern_context, '' ,longest_match,flags=re.IGNORECASE)
        np_fits = False
        for np in noun_phrases[::-1]:
            stop_word_found = False
            if np in target_longest_match:
                for stop_word in stop_words:
                    if re.search(stop_word, str(np)):
                        stop_word_found = True
                if stop_word_found is False:
                    output.append(np)
                    output.append(start_word)
                    output.append(matching_pattern)
                    np_fits = True
                    break
        if np_fits is False:
            output.append('<nothing_found>')
            output.append(start_word)
            output.append(matching_pattern)

    elif type_of_longest_match == 'case C':
        if len(noun_phrases) == 0:
            for np in NLP(message).noun_chunks:
                np = np.text
                noun_phrases.append(np)
        pattern_context = matching_pattern.replace('[npr]', '')
        target_longest_match = re.sub(pattern_context, '' ,longest_match,flags=re.IGNORECASE)
        np_fits = False
        for np in noun_phrases:
            stop_word_found = False
            if np in target_longest_match:
                for stop_word in stop_words:
                    if re.search(stop_word, str(np)):
                        stop_word_found = True
                if stop_word_found is False:
                    output.append(np)
                    output.append(start_word)
                    output.append(matching_pattern)
                    np_fits = True
                    break
        if np_fits is False:
            output.append('<nothing_found>')
            output.append(start_word)
            output.append(matching_pattern)

    else:
        output.append('<nothing_found>')
        output.append(start_word)
        output.append('<no pattern found>')
    
    return output