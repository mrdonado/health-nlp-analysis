"""
Upload an analysis to firebase
"""
import datetime
import pyrebase
from analyzer.configuration import FIREBASE_CONFIG

print 'Setting up the firebase connection'

FB_CONFIG = {"apiKey": FIREBASE_CONFIG['api_key'],
             "authDomain": FIREBASE_CONFIG['auth_domain'],
             "databaseURL": FIREBASE_CONFIG['database_url'],
             "storageBucket": FIREBASE_CONFIG['storage_bucket']}

# Try to set up the connection to firebase
FIREBASE = pyrebase.initialize_app(FB_CONFIG)
# Get a reference to the auth service
AUTH = FIREBASE.auth()
print 'Logging in into firebase'
# Log the user in
USER = AUTH.sign_in_with_email_and_password(FIREBASE_CONFIG['email'],
                                            FIREBASE_CONFIG['password'])
print 'Firebase connection ready'


def upload_analysis(analysis_json):
    """
    Upload the results of an analysis to firebase.
    """
    # Add a createdAt field
    analysis_json['createdAt'] = str(datetime.datetime.now())

    # Refresh Token
    fb_user = AUTH.refresh(USER['refreshToken'])

    # Get a reference to the analysis database
    analysis_db = FIREBASE.database().child('analysis')

    # Pass the user's idToken to the push method
    analysis_db.push(analysis_json, fb_user['idToken'])

    return True
