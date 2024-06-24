# standard imports
import hashlib
import json
import os

import requests


def test_post_request(data_server):
    http_ok = requests.status_codes.codes["OK"]
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    monitor_user = {"username": username, "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD")}
    print(monitor_user)
    # load html plot as autoreduce service
    file_name = "reflectivity.html"
    files = {"file": open(data_server.path_to(file_name)).read()}
    monitor_user["data_id"] = file_name

    http_request = requests.post(
        "http://127.0.0.1:80/plots/REF_L/12345/upload_plot_data/", data=monitor_user, files=files, verify=True
    )
    assert http_request.status_code == http_ok

    # load json plot a user "someuser" of the web-reflectivity app
    file_name = "reflectivity.json"
    with open(data_server.path_to(file_name), "r") as file_handle:
        files = {"file": json.dumps(json.load(file_handle))}
    monitor_user["data_id"] = file_name

    http_request = requests.post(
        "http://127.0.0.1:80/plots/" + username + "/upload_user_data/", data=monitor_user, files=files, verify=True
    )
    assert http_request.status_code == http_ok

    monitor_user.pop("data_id")
    # get all plots for an instrument
    http_request = requests.post("http://127.0.0.1:80/plots/REF_L/list/", data=monitor_user, files={}, verify=True)
    assert http_request.status_code == http_ok

    # get all plots from someuser
    http_request = requests.post(
        "http://127.0.0.1:80/plots/" + username + "/list/", data=monitor_user, files={}, verify=True
    )
    assert http_request.status_code == http_ok


def test_get_request(data_server):
    """Test GET request for HTML data like from monitor.sns.gov"""
    instrument = "REF_M"
    run_number = 12346
    http_ok = requests.status_codes.codes["OK"]
    http_unauthorized = requests.status_codes.codes["unauthorized"]

    # upload the run data using POST (authenticate with username and password)
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    monitor_user = {"username": username, "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD")}
    # load html plot as autoreduce service
    file_name = "reflectivity.html"
    files = {"file": open(data_server.path_to(file_name)).read()}
    monitor_user["data_id"] = file_name

    http_request = requests.post(
        f"http://127.0.0.1:80/plots/{instrument}/{run_number}/upload_plot_data/",
        data=monitor_user,
        files=files,
        verify=True,
    )
    assert http_request.status_code == http_ok

    base_url = f"http://127.0.0.1:80/plots/{instrument}/{run_number}/update/html/"

    # test GET request - authenticate with secret key
    url = f"{base_url}?key={_generate_key(instrument, run_number)}"
    http_request = requests.get(url)
    assert http_request.status_code == http_ok
    assert http_request.text == files["file"]

    # test GET request - no key
    # TODO: this should return 401 unauthorized
    url = base_url
    http_request = requests.get(url)
    assert http_request.status_code == http_ok

    # test GET request - wrong key
    url = f"{base_url}?key=WRONG-KEY"
    http_request = requests.get(url)
    assert http_request.status_code == http_unauthorized


def _generate_key(instrument, run_id):
    """
    Generate a secret key for a run on a given instrument
    Used to simulate clients sending GET-requests using a secret key
    @param instrument: instrument name
    @param run_id: run number
    """
    secret_key = os.environ.get("LIVE_PLOT_SECRET_KEY")
    if len(secret_key) == 0:
        return None
    else:
        h = hashlib.sha1()
        h.update(("%s%s%s" % (instrument.upper(), secret_key, run_id)).encode("utf-8"))
        return h.hexdigest()
