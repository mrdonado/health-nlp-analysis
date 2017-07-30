from config_loader import BEANSTALKD_CONFIG, FIREBASE_CONFIG, ELASTICSEARCH_CONFIG
from analyzer.runner import setup_and_run

# Start the magic!
if __name__ == "__main__":
    setup_and_run(BEANSTALKD_CONFIG, FIREBASE_CONFIG,
                  ELASTICSEARCH_CONFIG, True)
