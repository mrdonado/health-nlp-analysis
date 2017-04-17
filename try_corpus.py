"""
Put the corpus contents into the beanstalkd job queue.

This file is just a helper script that tests the job insertion into
the beanstalkd jobs queue.

"""
import pystalkd.Beanstalkd

BEANSTALK = pystalkd.Beanstalkd.Connection(host='localhost', port=11300)

BEANSTALK.use('default')


if __name__ == "__main__":
    # Test the job_analyzer using corpus data
    CORPUS = open(
        './corpus/heart_disease_cholesterol_hypertension_diabetes_obesity.json', 'r').readlines()

    count = 1

    for line in CORPUS:
        print('Inserting job:')
        BEANSTALK.put(line.rstrip())
        if count > 10:
            break
        else:
            count += 1
