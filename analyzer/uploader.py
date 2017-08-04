"""
Upload an analysis to firebase
"""
import pyrebase
import requests


def irrelevant_analysis(analysis_json):
    return (analysis_json['analysis']['problem'] == ''
            or analysis_json['analysis']['solution'] == '<nothing_found>') \
        and analysis_json['source'] != 'web'


class FirebaseAnalysisUploader(object):
    """
    Class for setting up the connection with firebase and providing
    JSON upload helpers.
    """

    def __init__(self, api_key, auth_domain, database_url, storage_bucket, email, password):
        print('Setting up the firebase connection')
        self.firebaseConfig = {"apiKey": api_key,
                               "authDomain": auth_domain,
                               "databaseURL": database_url,
                               "storageBucket": storage_bucket}
        # Try to set up the connection to firebase
        self.firebase = pyrebase.initialize_app(self.firebaseConfig)
        # Get a reference to the auth service
        self.auth = self.firebase.auth()
        print('Logging in into firebase')
        # Log the user in
        self.user = self.auth.sign_in_with_email_and_password(email, password)
        print('Firebase connection ready')

    def upload_analysis(self, analysis_json):
        """
        Upload the results of an analysis to firebase.
        """

        # If the analysis is not relevant, it won't be uploaded
        if irrelevant_analysis(analysis_json):
            return False

        # Refresh Token
        fb_user = self.auth.refresh(self.user['refreshToken'])

        # Get a reference to the analysis database
        analysis_db = self.firebase.database().child('analysis')
        # Pass the user's idToken to the push method
        analysis_db.push(analysis_json, fb_user['idToken'])
        return True


class ElasticsearchAnalysisUploader(object):
    """
    Class for wrapping up the uploading function to firebase.
    """

    def __init__(self, url, user, password):
        self.url = url + '/analysis/health'
        self.user = user
        self.password = password

    def upload_analysis(self, analysis_json):
        """
        Upload the results of an analysis to firebase.
        """

        # If the analysis is not relevant, it won't be uploaded
        if irrelevant_analysis(analysis_json):
            return False

        post = requests.post(self.url, json=analysis_json,
                             auth=(self.user, self.password))

        print(post)

        return True
