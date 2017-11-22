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
        if re.search(re.escape(word), message, flags=re.IGNORECASE):
            current_word = message[re.search(re.escape(word), message, flags=re.IGNORECASE).start():
                                   re.search(re.escape(word), message, flags=re.IGNORECASE).end()]
            if start_word is None or len(current_word) > len(start_word):
                start_word = current_word
    # we search for the longest match ('Mindfulness for anorexia nervosa' gets
    # 'anorexia nervosa' but not 'anorexia', although both are disease terms)
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

def magic_bullet_analyzer(message, start_word, grammar):
    """
    Maps a set of grammar rules with very high precision as the context is 
    rich. E.g. prescribe + noun phrase + to stop. The problem's
    position doesn't need to be explicit.
    """
    # 1) Find the matching magic bullet rule from the grammar
    # They have '[np]' (noun phrase) instead of [s] or [p] as variables
    
    magic_bullet = [None, None]
    case_B_C = None
    longest_match = ''
    target_noun_phrase = ''
    pattern_context = None
    output = []

    for pattern in grammar:
        possible_magic_bullet = ''
    
        # Skip conventional grammar rules
        if re.search('\[(p|s)\]', pattern):
            continue

        # Case A: "prescribe + np + to stop" (with left and right contexts)
        if re.search('\[np\]', pattern):
            possible_magic_bullet = pattern.replace('[np]', '.+')
            case_B_C = False

        # Case B: "npl secondary effects" (no left context)
        # Look for 3 words to the left by defaut
        elif re.search('\[npl\]', pattern):
            possible_magic_bullet = pattern.replace('[npl]', '(\S+ ){4}')
            pattern_context = pattern.replace('[npl]', '')
            case_B_C = True

        # Case C: "the solution is npr" (no right context)
        # Look for 3 words to the right by default
        elif re.search('\[npr\]', pattern):
            possible_magic_bullet = pattern.replace('[npr]', '( \S+){4}')
            pattern_context = pattern.replace('[npr]', '')
            case_B_C = True

        # Look for a possible pattern match into the message:
        if re.search(possible_magic_bullet, message, flags=re.IGNORECASE):
            match = message[
                re.search(possible_magic_bullet, message, flags=re.IGNORECASE).start():
                re.search(possible_magic_bullet, message, flags=re.IGNORECASE).end()
            ]
            if len(match) > len(longest_match):
                # Store the longest match to avoid the ambiguity of one rule
                # against another
                longest_match = match
                magic_bullet[0] = possible_magic_bullet 
                magic_bullet[1] = case_B_C

    # 2) If magic bullet is found, get the NP for its match into the message:
    if magic_bullet[0] is not None:
        noun_phrases = []
        for np in NLP(message).noun_chunks:
            np = np.text
            noun_phrases.append(np)

        # Get the NP that fits into the pattern match:
        # In case B and C, we take context out of the longest_match string,
        # to avoid confussion if more than one NP is present:
        if magic_bullet[1] == True:
            target_longest_match = longest_match.replace(pattern_context, '')
        else:
            target_longest_match = longest_match
        for np in noun_phrases:
            if np in target_longest_match:
                output.append(np)
                output.append(start_word)
                output.append(magic_bullet[0])
                break

        # Return output if the right NP is found:
        if len(output) == 3:
            return output

        # Else, no NP fit although a magic bullet rule
        # is matched: 
        else:
            output.append('<nothing_found>')
            output.append(start_word)
            output.append(magic_bullet[0])
            return output
    else:
        output.append('<nothing_found>')
        output.append(start_word)
        output.append('<no pattern found>')
        return output


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
            
            # 2.2) Look for magic bullet rule matching. If found, return output
            # and stop analyzer process

            magic_bullet_result = magic_bullet_analyzer(no_splitted_message, start_word, grammar)

            if magic_bullet_result[0] != '<nothing_found>':
                output.append(magic_bullet_result[0])
                output.append(magic_bullet_result[1])
                output.append(magic_bullet_result[2])
                return output

            else:

            # 2.3) Look for problem-solution rule matching, as follows:

                # For every stored grammar rule, generate its counterpart including the
                # start word (e.g. '[s] for [p]' -> '[s] for anorexia')
                for pattern in grammar:

                    # Skip magic bullet rules tested before:
                    if re.search('(\[np\]|\[npl\]|\[npr\])', pattern):
                        continue

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


# # Test message! #####
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

# ###### Test set of messages ################

# messages = open('mensajes.txt', 'r').readlines()
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


# LANGUAGE_DATA = language_data_loader('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/grammar.txt',
# '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/counter_grammar.txt',
# '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt', 
# '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/stop_words.txt')


# count = 0
# for message in messages:
#     count = count +1
#     print str(count)+'/'+str(len(messages))
#     message = unicode(message)
#     result = analyzer(message, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['counter_grammar'], LANGUAGE_DATA['stop_words'])
#     if result[0] != "<nothing_found>":
#         print result[0], ' --> ', result[1]
