#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

##############
## Analyzer ##
##############

Given a grammar, and a set of start words, this
file provides the tools to analyze a human text written in
English.

The analyzer receives a text input (message), and extracts valuable
information from it within the DISEASE-TREATMENT cognitive frame, i.e. a
disease and a potential solution for it.

It consists of the following functions:

(1) file_parser:
    Parses language data files before loading them as language resources
(2) language_data_loader:
    Loads linguistic knowledge to feed the Analyzer (a simple NLP engine)
(3) start_word_match:
    Finds disease mentions in the incoming text message
(4) get_start_word_from_sentence:
    Divides the incoming message into sentences, and look for the
    start word in each sentence. When found, it returns the sentence and
    the start word found in it
(5) get_noun_phrase:
    Extracts the exact noun phrase corresponding to the solution of the
    disease problem. Before, it parses the whole sentences to look for all
    the noun structures, and then chooses the appropriate one
(6) counter_analyzer:
    Maps a set of grammar rules into the message, in order to prevent false
    positives. These rules have priority over the rules from analyzer()
    E.g. risk for + problem, is a "counter rule" that prevents a case of false
    positive in the rule: solution + for + problem
(7) magic_bullet_analyzer:
    Maps a set of grammar rules with very high precision as the context is 
    rich. E.g. prescribe + noun phrase + to stop. For these reason, the problem's
    position doesn't need to be explicit.
(6) analyzer:
    Maps the language dataset's rules into the text mensage, and get the best 
    noun phrase as the solution for the disease problem.


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


def file_parser(path, to_lower):
    """
    Helper function to parse text files.
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
        'of',
        'type',
        'with',
        'and',
        'the',
        '^\d+$',
        'acute',
        'system',
        'primary',
        'involving',
        'dominant',
        'recurrent',
        'or',
        'to',
        'in',
        'without',
        'situ',
        'types',
        'due',
        '(I|II|III|IV|V|VI|VII|VIII|XIX|X)',
        '^[A-Z]$',
        'by'
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
    Then it parses them and returns an array with their contents
    altogether.
    """
    language_data = dict()
    # Load grammar
    language_data['grammar'] = file_parser(grammar_path, False)
    # Load counter_grammar
    language_data['counter_grammar'] = file_parser(counter_grammar_path, False)
    # Load start words (a term list to recover messages on diseases)
    language_data['start_words'] = file_parser(start_words_path, True)

    ### Testing this:
    language_data['start_words'] = start_words_to_dict(language_data['start_words'])

    # Load stop words (words tagged as noun phrases that cannot be extracted
    # as entities (e.g. You, @username11):
    language_data['stop_words'] = file_parser(stop_words_path, True)
    return language_data


def start_word_match(message, start_words):
    """
    """
    start_word = None
    message_to_lower = message.lower()
    for single_token in start_words.keys():
        term_has_been_found = False
        if single_token in message_to_lower:
            for term in start_words[single_token]:
                if term in message_to_lower:
                    term_has_been_found = True
                    if start_word is None or len(term) > len(start_word):
                        start_word = term
        if term_has_been_found is True:
            break
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
    analyzer(), the next function
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
                    if re.search(stop_word, str(candidate_np), flags=re.IGNORECASE):
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
                    if re.search(stop_word, str(candidate_np), flags=re.IGNORECASE):
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

def analyzer(message, start_words, grammar, counter_grammar, stop_words):
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
            
            # magic_bullet_analyzer() comes here #

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

    # Get no results if no solution or start word is found, or if solution =
    # start_word
    if len(output) == 0 or output[0] in output[1]:
        output.append('<nothing_found>')
        output.append(start_word)
        output.append('<no pattern found>')
        return output


###Test message! #####
# def test_message():
#     message = raw_input('\n' + 'New message? ')
#     message = unicode(message)

#     LANGUAGE_DATA = language_data_loader('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/grammar.txt',
#      '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/counter_grammar.txt',
#      '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt', 
#      '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/stop_words.txt')
#     result = analyzer(message, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['counter_grammar'], LANGUAGE_DATA['stop_words'])
    
#     print '\n'+'<'+result[0]+'>'+'\t'+'<'+result[1]+'>'+'\t'+'<'+result[2]+'>'+'\n'

#     control = raw_input('(t)ry again ?')
#     while control == "t":
#         LANGUAGE_DATA = language_data_loader('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/grammar.txt',
#         '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/counter_grammar.txt', '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt', '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/stop_words.txt')
#         result = analyzer(message, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['counter_grammar'], LANGUAGE_DATA['stop_words'])
#         print '<m>'+message+'</m>'
#         print '\n'+'<'+result[0]+'>'+'\t'+'<'+result[1]+'>'+'\t'+'<'+result[2]+'>'+'\n'

#         control = raw_input('(t)ry again ?')
#     else:
#         test_message()

# test_message()

# #### Test set of messages ################

# messages = open('mensajes.txt', 'r').readlines()
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


# LANGUAGE_DATA = language_data_loader('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/grammar.txt',
# '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/counter_grammar.txt',
# '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt', 
# '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/stop_words.txt')

# ### Medir el tiempo
# import time
# ###

# count = 0
# for message in messages:

#     start = time.time()

#     count = count +1
#     print str(count)+'/'+str(len(messages))
#     message = unicode(message)
#     result = analyzer(message, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['counter_grammar'], LANGUAGE_DATA['stop_words'])
#     if result[0] != "<nothing_found>":
#         print result[0], ' --> ', result[1]

#     end = time.time()
#     print end - start
