# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

# [START gae_python37_auth_verify_token]
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import firestore
import google.oauth2.id_token

firebase_request_adapter = requests.Request()
# [END gae_python37_auth_verify_token]

firestore_client = firestore.Client()

app = Flask(__name__)


def store_time(email, dt):
    entity = firestore_client.collection(u'visit').document()
    entity.set({
        'email': email,
        'timestamp': dt
    })


def fetch_times(email, limit):
    ref = firestore_client.collection(u'visit')
    ref = ref.where('email', '==', email)
    ref = ref.order_by(u'timestamp', direction=firestore.Query.DESCENDING)
    query = ref.limit(limit).stream()

    return query


# [START gae_python37_auth_verify_token]
@app.route('/')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            store_time(claims['email'], datetime.datetime.now())
            times = fetch_times(claims['email'], 10)
        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    tstamps = []
    if times is not None:
        for t in times:
            tstamps.append(t.get('timestamp'))
    return render_template(
        'index.html',
        user_data=claims, error_message=error_message, times=tstamps)
# [END gae_python37_auth_verify_token]


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
