from __future__ import print_function

# standard imports
import json
import os
import requests


def test_post_get(data_server):
    http_ok = requests.status_codes.codes["OK"]
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    monitor_user = {"username": username,
                    "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD")}
    print(monitor_user)
    # load html plot as autoreduce service
    file_name = 'reflectivity.html'
    files = {"file": open(data_server.path_to(file_name)).read()}
    monitor_user["data_id"] = file_name

    http_request = requests.post("http://127.0.0.1:80/plots/REF_L/12345/upload_plot_data/",
                                 data=monitor_user, files=files, verify=True)
    assert http_request.status_code == http_ok

    # load json plot a user "someuser" of the web-reflectivity app
    file_name = 'reflectivity.json'
    with open(data_server.path_to(file_name), 'r') as file_handle:
        files = {"file": json.dumps(json.load(file_handle))}
    monitor_user["data_id"] = file_name

    http_request = requests.post("http://127.0.0.1:80/plots/" + username + "/upload_user_data/",
                                 data=monitor_user, files=files, verify=True)
    assert http_request.status_code == http_ok

    monitor_user.pop("data_id")
    # get all plots for an instrument
    http_request = requests.post("http://127.0.0.1:80/plots/REF_L/list/",
                                 data=monitor_user, files={}, verify=True)
    assert http_request.status_code == http_ok

    # get all plots from someuser
    http_request = requests.post("http://127.0.0.1:80/plots/" + username + "/list/",
                                 data=monitor_user, files={}, verify=True)
    assert http_request.status_code == http_ok


