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

from flask import Flask, render_template

# [START gae_python37_datastore_store_and_fetch_times]
from google.cloud import firestore

firestore_client = firestore.Client()

# [END gae_python37_datastore_store_and_fetch_times]
app = Flask(__name__)


# [START gae_python37_datastore_store_and_fetch_times]
def store_time(dt):
    entity = firestore_client.collection(u'visit').document()
    entity.set({
        'timestamp': dt
    })


def fetch_times(limit):
    query = firestore_client.collection(u'visit').order_by(u'timestamp').limit(limit).stream()

    return query
# [END gae_python37_datastore_store_and_fetch_times]


# [START gae_python37_datastore_render_times]
@app.route('/')
def root():
    # Store the current access time in Datastore.
    store_time(datetime.datetime.now())

    # Fetch the most recent 10 access times from Datastore.
    tquery = fetch_times(10)

    times = []
    for t in tquery:
        times.append(str(t.get('timestamp')))

    return render_template(
        'index.html', times=times)
# [END gae_python37_datastore_render_times]


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
