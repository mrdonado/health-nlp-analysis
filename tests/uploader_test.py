#!/usr/bin/python3
"""
uploader_test.py
"""
import analyzer.uploader


class DummyAuth(object):

    def sign_in_with_email_and_password(self, email, password):
        assert email == "email5"
        assert password == "password6"
        return dict(name="someUser",
                    refreshToken="someToken")

    def refresh(self, userToken):
        assert userToken == "someToken"
        return dict(idToken="someIdToken")


class DummyChild(object):

    def push(self, analysis, token):
        assert analysis["source"] == "twitter"
        assert token == "someIdToken"
        return


class DummyDatabase(object):

    def child(self, db_name):
        assert db_name == 'analysis'
        return DummyChild()


class DummyPyrebase(object):

    auth_calls = 0

    def auth(self):
        self.auth_calls += 1
        return DummyAuth()

    def database(self):
        assert self.auth_calls == 1
        return DummyDatabase()


def dummy_initialize_app(config):
    assert config["apiKey"] == "apiKey1"
    assert config["authDomain"] == "authDomain2"
    assert config["databaseURL"] == "databaseUrl3"
    assert config["storageBucket"] == "storageBucket4"
    return DummyPyrebase()


# We replace pyrebase.initialize_app with a dummy class
analyzer.uploader.pyrebase.initialize_app = dummy_initialize_app


def test_uploader():
    uploader = analyzer.uploader.AnalysisUploader(
        "apiKey1",
        "authDomain2",
        "databaseUrl3",
        "storageBucket4",
        "email5",
        "password6"
    )

    example_analysis = {
        "source": "twitter",
        "analysis": {
            "problem": "some problem",
            "solution": "some solution"
        }
    }

    example_analysis_2 = {
        "source": "twitter",
        "analysis": {
            "problem": "",
            "solution": "<nothing_found>"
        }
    }

    # All assertions are into the mocked classes
    assert uploader.upload_analysis(example_analysis)
    assert not uploader.upload_analysis(example_analysis_2)
    return
