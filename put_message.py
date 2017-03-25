"""
Put a message into the beanstalkd job queue.

This file is just a helper script that tests the job insertion into
the beanstalkd jobs queue.

"""
import sys
import beanstalkc

BEANSTALK = beanstalkc.Connection(host='localhost', port=14711)

print 'Inserting message: ' + sys.argv[1]

JSON_STRING = '{"message": "' + sys.argv[1] + '", "author":"jdonado", "source": "web-app"}'

BEANSTALK.put(JSON_STRING)
