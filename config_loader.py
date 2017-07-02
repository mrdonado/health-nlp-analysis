"""
Configuration loader.
"""
import configparser
import sys

config = configparser.ConfigParser()

config.read('config.ini')

try:
    beanstalkd_section = config['beanstalkd']
    firebase_section = config['firebase']
    elasticsearch_section = config['elasticsearch']
except:
    print("ERROR: config.ini is not present or its format is wrong. \n\nPlease create a new config.ini file and set your configuration parameters. \n\nYou can find an example file in this directory, as config.example.ini. Just rename it as config.ini and set your local configuration parameters.")
    sys.exit()



BEANSTALKD_CONFIG = dict(
    beanstalk_ip=beanstalkd_section.get('BeanstalkdHost', 'localhost'),
    beanstalk_port=int(beanstalkd_section.get('BeanstalkdPort', '11300'), base=10)
)

FIREBASE_CONFIG = dict(
    api_key=firebase_section.get('ApiKey'),
    auth_domain=firebase_section.get('AuthDomain'),
    database_url=firebase_section.get('DatabaseUrl'),
    storage_bucket=firebase_section.get('StorageBucket'),
    email=firebase_section.get('Email'),
    password=firebase_section.get('Password')
)

ELASTICSEARCH_CONFIG = dict(
    url=elasticsearch_section.get('ElasticsearchUrl', 'http://localhost:9200'),
    user=elasticsearch_section.get('ElasticsearchUser', 'elastic'),
    password=elasticsearch_section.get('ElsaticsearchPassword', 'changeme'),
)
