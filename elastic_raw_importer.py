"""
Utility to import analyzed JSON data stored in plain text files
"""
from config_loader import ELASTICSEARCH_CONFIG as es_config
from analyzer.uploader import ElasticsearchAnalysisUploader
import sys
import json

# Setup the elasticsearch uploader
es_uploader = ElasticsearchAnalysisUploader(es_config['url'],
                                            es_config['user'],
                                            es_config['password'])

# Check that some filename has been specified as argument
if len(sys.argv) != 2:
    print('Wrong number of arguments. Please, specify the file\n' +
          'with the analysis data to be imported.')
    sys.exit(0)

# Attempt to open the specified file
print('Specified file: ' + sys.argv[1])

try:
    f = open(sys.argv[1])
except FileNotFoundError:
    print('The specified file couldn\'t be found')
    sys.exit(1)

# Read the contents of the file
for line in f:
    analysis = json.loads(line)
    analysis['source'] = analysis['source'].lower()
    es_uploader.upload_analysis(analysis)
    print('Analysis imported: ' + line)
