"""
Put a message into the beanstalkd job queue.

This file is just a helper script that tests the job insertion into
the beanstalkd jobs queue.

"""
import sys
import json
import datetime
import pystalkd.Beanstalkd

BEANSTALK = pystalkd.Beanstalkd.Connection(host='localhost', port=11300)


if len(sys.argv) == 1:
    print("\nERROR:Please, specify the message to be posted as an argument. E.g.:\n\npython3 put_message.py 'Some example message'.\n")
    sys.exit()

json_job = {
    "user_name": "jdonado",
    "user_description": "Some random radiologist.",
    "created_at": datetime.datetime.now().isoformat(),
    "message": sys.argv[1],
    "source": "twitter",
    "query": "diabetes"
}

print('Inserting job:')
print(json.dumps(json_job))

BEANSTALK.put(json.dumps(json_job))
