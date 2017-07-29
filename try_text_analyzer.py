from analyzer.engines import text_analyzer
## Initialization ##

LANGUAGE_DATA = text_analyzer.language_data_loader(
    './language_data/grammar.txt',
    './language_data/start_words.txt',
    './language_data/stop_words.txt'
)
corpus_name = raw_input('Name of the corpus for testing: ')
testfile = open('corpus/' + corpus_name, 'r')
for line in testfile:
    line = line.rstrip()
    line = unicode(line)
    result = text_analyzer.analyzer(line, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['stop_words'])
    if result[0] != '<nothing_found>':
        solution = result[0]
        problem = result[1]
        message = line
        rule = result[2]
        print solution, '\t', problem, '\t', rule, '\t', message


