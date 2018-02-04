#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

##############
## Analyzer ##
##############

Text analyzer receives an input (message), and extracts valuable
information from it: a "solution" (management, treatment, funds, etc.)
and its corresponding disease.

"""
import re
# Text codification must be UTF-8 for SpaCy (NLP library)

# There's no sys.sederaultencoding in Python3
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

# Load SpaCy and English module
from spacy.en import English
NLP = English()

# Load magic_bullet_analyzer() function, a separate module
# Before: from analyzer.engines import magic_bullet_analyzer
import sys
sys.path.append('./analyzer/engines')
import magic_bullet_analyzer

def file_parser(path, to_lower):
    """
    Helper function to parse language resource files.
    """
    input_file = open(path, 'r', encoding='utf-8')
    #input_file = open(path, 'r')
    results = []
    for line in input_file:
        line = line.strip()
        if to_lower:
            line = line.lower()
        results.append(line)
    input_file.close()
    return results


def start_words_to_dict(start_words):
    """
    Create a dict of "start words" from a large file of disease
    keywords. E.g. 'brain cancer', 'skin cancer' are stored in
    {'cancer': ['brain cancer', 'skin cancer']}
    """
    single_tokens = dict()
    for start_word in start_words:
        for token in start_word.split():
            if token in single_tokens.keys():
                single_tokens[token].append(start_word)
            else:
                single_tokens[token] = []
                single_tokens[token].append(start_word)
    forbidden_single_tokens = [
        '^of$',
        '^type$',
        '^with$',
        '^and$',
        '^the$',
        '^\d+$',
        '^acute$',
        '^system$',
        '^primary$',
        '^involving$',
        '^dominant$',
        '^recurrent$',
        '^or$',
        '^to$',
        '^in$',
        '^without$',
        '^situ$',
        '^types$',
        '^due$',
        '^(I|II|III|IV|V|VI|VII|VIII|XIX|X)$',
        '^[A-Z]$',
        '^by$'
    ]
    single_tokens_to_delete = []
    for single_token in single_tokens.keys():
        for forbidden_single_token in forbidden_single_tokens:
            if re.search(forbidden_single_token, single_token):
                single_tokens_to_delete.append(single_token)
                break
    for single_token_to_delete in single_tokens_to_delete:
        del single_tokens[single_token_to_delete]
    return single_tokens


def language_data_loader(grammar_path, counter_grammar_path, start_words_path, stop_words_path):
    """
    It receives three file paths as input:
    - Grammar
    - Start words
    - Stop words
    - Counter grammar
    Then it parses them and returns an array with their contents
    altogether.
    """
    language_data = dict()

    # Load grammar
    language_data['grammar'] = file_parser(grammar_path, False)

    # From langua_data['grammar'], load a subset of rules for magic_bullet_analyzer()
    language_data['magic_bullet_grammar'] = []
    for pattern in language_data['grammar']:
        if '[np' in pattern:
            language_data['magic_bullet_grammar'].append(pattern)
    for pattern in language_data['magic_bullet_grammar']:
        language_data['grammar'].remove(pattern)

    # Load counter_grammar
    language_data['counter_grammar'] = file_parser(counter_grammar_path, False)
    
    # Load start words (a term list to recover messages on diseases)
    language_data['start_words'] = file_parser(start_words_path, True)
    language_data['start_words'] = start_words_to_dict(language_data['start_words'])

    # Load stop words (words tagged as noun phrases that cannot be extracted
    # as entities (e.g. You, @username11):
    language_data['stop_words'] = file_parser(stop_words_path, False)
    
    return language_data


def start_word_match(message, start_words):
    """
    Find possible string matches of disease words into messages
    """
    start_word = None
    longest_term = ''
    message_to_lower = message.lower()
    for single_token in start_words.keys():
        if single_token in message_to_lower:
            for term in start_words[single_token]:
                if term in message_to_lower:
                    if len(term) > len(longest_term):
                        longest_term = term
    if len(longest_term) > 0:
        start_word = longest_term
    if start_word is not None:
        start_position = re.search(re.escape(start_word), message_to_lower).start()
        end_position = re.search(re.escape(start_word), message_to_lower).end()
        start_word = message[start_position:end_position]
    return start_word


def get_start_word_from_sentence(message, start_words):
    """
    Divides the incoming message into sentences, and look for the
    start word in each sentence. When found, it returns the sentence and
    the start word found in it
    """

    start_word = start_word_match(message, start_words)
    result = []

    if start_word is not None:
        # A start_word has been found, now
        # specify the sentence:
        bounds = [
            '(?<=[^A-Z].[.?]) +(?=[A-Z])',
            '\.\.\.',
            '\? ',
            '\! ',
            ' \- ',
            '\, ',
            '\: ',
            '; ',
            'http']
        for bound in bounds:
            message = re.sub(bound, '<bound>', message)
        sentences = message.split('<bound>')
        for sentence in sentences:
            if re.search(re.escape(start_word), sentence):
                result.append(start_word)
                result.append(sentence)
                break
    
    # Return output:
    if len(result) == 0:
        return None
    else:
        return result


def get_noun_phrase(message, longest_match, position, stop_words):
    """
    Extracts the exact noun phrase corresponding to the solution of the
    disease problem. The arguments this function gets are defined in 
    analyzer()
    """

    longest_match_start = re.search(re.escape(longest_match), message).start()
    longest_match_end = re.search(re.escape(longest_match), message).end()
    noun_phrases = []

    # Get all noun phrases from the whole text:
    for np in NLP(message).noun_chunks:
        noun_phrases.append(np)
    # If no NP is found:
    if len(noun_phrases) == 0:
        return None
    else:

        # This variable stores the chosen noun phrase:
        target_noun_phrase = None

        # 1) Search for noun phrases in solution-problem position: 'sp'
        # In this position, the solution is mentioned before the problem
        if position == "sp":
            candidate_nps = []
            for np in noun_phrases:
                np_end = re.search(re.escape(np.text), message).end()
                if np_end <= longest_match_start:
                    candidate_nps.append(np.text)
            # Exclude noun phrase if it is stop word:
            for candidate_np in candidate_nps[::-1]:
                stop_word_found = False
                for stop_word in stop_words:
                    if re.search(stop_word, str(candidate_np)):
                        stop_word_found = True
                        break
                if stop_word_found is False:
                    target_noun_phrase = candidate_np
                    break
                else:
                    continue

        # 2) Search for noun phrase in problem-solution position: 'ps'
        # In this position, the solution is mentioned after the problem
        elif position == "ps":
            candidate_nps = []
            for np in noun_phrases:
                np_start = re.search(re.escape(np.text), message).start()
                if np_start >= longest_match_end:
                    candidate_nps.append(np.text)
            # Exclude noun phrase if it is stop word:
            for candidate_np in candidate_nps:
                stop_word_found = False
                for stop_word in stop_words:
                    if re.search(stop_word, str(candidate_np)):
                        stop_word_found = True
                        break
                if stop_word_found is False:
                    target_noun_phrase = candidate_np
                    break
                else:
                    continue

        # Return noun phrase ('None' if not found):
        return target_noun_phrase


def counter_analyzer(message, start_word, counter_grammar):
    """
    Maps a set of grammar rules into the message, in order to prevent false
    positives. 
    E.g. risk for + problem, is a "counter rule" that prevents a case of false
    positive in the rule: solution + for + problem
    """
    longest_match = ''
    for pattern in counter_grammar:
        instance = pattern.replace('[p]', start_word)
        if re.search(instance, message, flags=re.IGNORECASE):
            found_instance = instance
            match = message[re.search(found_instance, message, flags=re.IGNORECASE).start(
                ):re.search(found_instance, message, flags=re.IGNORECASE).end()]
            # Find the rule with the longest match in the string:
            if len(match) > len(longest_match):
                longest_match = match
    if len(longest_match) > 0:
        return True
    else:
        return False


def analyzer(message, start_words, grammar, counter_grammar, stop_words, magic_bullet_grammar):
    """
    Analyzer, a treatment-entity finder.
    The input grammar follows two basic syntactic schemes,
    where [s] = treatment/solution and [p] = disease/problem:

    It gets as input:
    (a) The incoming message
    (b) Language data (start_words, grammar, stop_words)

    It returns as output:
    output = []
    A list with 3 elements, where:
    output[0]
        is the solution found, a unicode string or '<nothing_found>'
    output[1]
        is the problem found, a unicode string or '<no start_word>'
    output[2]
        is the rule pattern matched, an string or '<no pattern found>'

    Two functions operate before the basic problem-solution pattern
    matching:
        counter_analyzer() prevents false positive cases before analyzer()
        operates,
        magic_bullet_analyzer() looks for rich-context pattern rules that have
        priority over the conventional problem-solution rules

    """
    # Necessary variables:
    magic_bullet_analyzer_result = None
    longest_match = ''
    matching_pattern = ''
    output = []

    # 1) Find the start word in the correct sentence in message,
    # then assign "message" a new value with only one sentence.
    start_word_And_message = get_start_word_from_sentence(message, start_words)
    if start_word_And_message is not None:
        no_splitted_message = message
        start_word = start_word_And_message[0]
        message = start_word_And_message[1]
        # As we are're monitoring Twitter, we turn start_word into
        # twitter_start_word to get more mentions as follows:
        twitter_start_word = '(' + '#\w*' + start_word + '|' + start_word + ')'
    else:
        start_word = '<no start_word>'

    # Before the analysis, check if start word (twitter_start_word)
    # is in message:
    if start_word_And_message is not None:

        # 2) Analysis process

        # 2.1) Counter analysis to avoid false positives:
        counter_analyzer_result = counter_analyzer(message, twitter_start_word, counter_grammar)
        if counter_analyzer_result is False:
            
            # 2.2) Try first 'magic bullet' rules:
            magic_bullet_analyzer_result = magic_bullet_analyzer.magic_bullet_analyzer(no_splitted_message, start_word, magic_bullet_grammar, stop_words)
            if magic_bullet_analyzer_result[0] != '<nothing_found>':
                output.append(magic_bullet_analyzer_result[0])
                output.append(magic_bullet_analyzer_result[1])
                output.append(magic_bullet_analyzer_result[2])
                return output
            else:

                # 2.3) Look for problem-solution rule matching, as follows:

                # For every stored grammar rule, generate its counterpart including the
                # start word (e.g. '[s] for [p]' -> '[s] for anorexia')
                for pattern in grammar:

                    instance = pattern.replace('[p]', twitter_start_word)
                    instance = instance.replace('[s]', '')

                    # Test every rule against the message:
                    if re.search(instance, message, flags=re.IGNORECASE):
                        found_instance = instance
                        match = message[re.search(found_instance, message, flags=re.IGNORECASE).start(
                        ):re.search(found_instance, message, flags=re.IGNORECASE).end()]
                        # Find the rule with the longest match in the string:
                        if len(match) > len(longest_match):
                            longest_match = match
                            matching_pattern = pattern

                # Rule matchs if 'longest_match' contains a string,
                # so the analysis can continue:
                if len(longest_match) > 0:

                    # First possible structure: SOLUTION before PROBLEM
                    if matching_pattern.find('[s]') < matching_pattern.find('[p]'):
                        target_match = message[:message.find(longest_match)]
                        # target_match = unicode(target_match, "utf-8" )
                        if len(target_match) >= 3:
                            target_noun_phrase = get_noun_phrase(
                                message, longest_match, 'sp', stop_words)
                            if target_noun_phrase is not None:
                                output.append(target_noun_phrase)
                                output.append(start_word)
                                output.append(matching_pattern)
                                return output
                        
                    # Second possible structure: SOLUTION after PROBLEM:
                    elif matching_pattern.find('[s]') > matching_pattern.find('[p]'):
                        target_match = message[message.find(
                            longest_match) + len(longest_match):]
                        if len(target_match) >= 3:
                            target_noun_phrase = get_noun_phrase(
                                message, longest_match, 'ps', stop_words)
                            if target_noun_phrase is not None:
                                output.append(target_noun_phrase)
                                output.append(start_word)
                                output.append(matching_pattern)
                                return output
                    
                    # This returns matching rules without [s] or [p], neither
                    # they're magic bullets. So, they are possibly mispelled:
                    else:
                        output.append('<nothing_found>')
                        output.append(start_word)
                        output.append('This rule may be erroneous: ' + matching_pattern)
                        return output

    # Get no results if no solution or start word is found, or if solution =
    # start_word
    if len(output) == 0:
        output.append('<nothing_found>')
        output.append(start_word)
        # Append this to output if a pattern was found in magic_bullet_analyzer(),
        # but any noun phrase wasn't found:
        if magic_bullet_analyzer_result is not None:
            if magic_bullet_analyzer_result[2] != '<no pattern found>':
                output.append(magic_bullet_analyzer_result[2])
            else:
                output.append('<no pattern found>')
        else:
            output.append('<no pattern found>')
        return output