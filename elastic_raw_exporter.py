"""
Utility to export analysis data from the elasticsearch into an
export.txt file where each line is a json document.
"""
from config_loader import ELASTICSEARCH_CONFIG as es_config
import json
import requests


def export_hits(hits, file):
    # Export each element to the export.txt file
    for analysis in hits:
        file.write(json.dumps(analysis['_source']) + '\n')


f = open('export.txt', 'w')

r = requests.get(es_config['url'] + '/analysis/_search?scroll=1m&size=5000',
                 auth=(es_config['user'],
                       es_config['password']))

data = r.json()
scroll_id = data['_scroll_id']
hits_count = len(data['hits']['hits'])
export_hits(data['hits']['hits'], f)

while hits_count > 0:
    payload={'scroll': '1m', 'scroll_id': scroll_id}
    # Get analysis data
    r=requests.post(es_config['url'] + '/_search/scroll',
                      auth=(es_config['user'],
                            es_config['password']),
                      json=payload)
    data=r.json()
    scroll_id=data['_scroll_id']
    export_hits(data['hits']['hits'], f)
    hits_count=len(data['hits']['hits'])
    print('.', end='', flush=True)

f.close()
