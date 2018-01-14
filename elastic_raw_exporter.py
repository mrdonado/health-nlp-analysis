"""
Utility to export analysis data from the elasticsearch into an
export.txt file where each line is a json document.
"""
from config_loader import ELASTICSEARCH_CONFIG as es_config
import json
import requests

current_index = 0

page_size = 1000
total = page_size + 1


def export_hits(hits, file):
    # Export each element to the export.txt file
    for analysis in hits:
        file.write(json.dumps(analysis['_source']) + '\n')


f = open('export.txt', 'w')

r = requests.get(es_config['url'] + '/analysis/_search?scroll=1m',
                 auth=(es_config['user'],
                       es_config['password']))

data = r.json()
scroll_id = data['_scroll_id']
total = data['hits']['total']
export_hits(data['hits']['hits'], f)

while scroll_id:
    payload = {'scroll': '1m', 'scroll_id': scroll_id}
    # Get analysis data
    r = requests.post(es_config['url'] + '/_search/scroll',
                      auth=(es_config['user'],
                            es_config['password']),
                      json=payload)
    data = r.json()
    scroll_id = data['_scroll_id']
    export_hits(data['hits']['hits'], f)
    print('.', end='', flush=True)

f.close()
