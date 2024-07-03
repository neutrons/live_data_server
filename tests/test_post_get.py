# standard imports
import hashlib
import json
import os

import psycopg
import requests

TEST_URL = "http://127.0.0.1"
HTTP_OK = requests.status_codes.codes["OK"]
HTTP_UNAUTHORIZED = requests.status_codes.codes["unauthorized"]
HTTP_NOT_FOUND = requests.status_codes.codes["NOT_FOUND"]
HTTP_BAD_REQUEST = requests.status_codes.codes["BAD_REQUEST"]


class TestLiveDataServer:
    @classmethod
    def setup_class(cls):
        """Clean the database before running tests"""
        conn = psycopg.connect(
            dbname=os.environ.get("DATABASE_NAME"),
            user=os.environ.get("DATABASE_USER"),
            password=os.environ.get("DATABASE_PASS"),
            port=os.environ.get("DATABASE_PORT"),
            host="localhost",
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM plots_plotdata")
        cur.execute("DELETE FROM plots_datarun")
        cur.execute("DELETE FROM plots_instrument")
        conn.commit()
        conn.close()

    def test_post_request(self, data_server):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        monitor_user = {"username": username, "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD")}

        # load html plot as autoreduce service
        file_name = "reflectivity.html"
        files = {"file": open(data_server.path_to(file_name)).read()}
        monitor_user["data_id"] = file_name

        http_request = requests.post(
            TEST_URL + "/plots/REF_L/12345/upload_plot_data/", data=monitor_user, files=files, verify=True
        )
        assert http_request.status_code == HTTP_OK

        # load json plot a user "someuser" of the web-reflectivity app
        file_name = "reflectivity.json"
        with open(data_server.path_to(file_name), "r") as file_handle:
            files = {"file": json.dumps(json.load(file_handle))}
        monitor_user["data_id"] = file_name

        http_request = requests.post(
            TEST_URL + "/plots/" + username + "/upload_user_data/", data=monitor_user, files=files, verify=True
        )
        assert http_request.status_code == HTTP_OK

        monitor_user.pop("data_id")
        # get all plots for an instrument
        http_request = requests.post(TEST_URL + "/plots/REF_L/list/", data=monitor_user, files={}, verify=True)
        assert http_request.status_code == HTTP_OK

        # get all plots from someuser
        http_request = requests.post(
            TEST_URL + "/plots/" + username + "/list/", data=monitor_user, files={}, verify=True
        )
        assert http_request.status_code == HTTP_OK

    def test_get_request(self, data_server):
        """Test GET request for HTML data like from monitor.sns.gov"""
        instrument = "REF_M"
        run_number = 12346

        # upload the run data using POST (authenticate with username and password)
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        monitor_user = {"username": username, "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD")}
        # load html plot as autoreduce service
        file_name = "reflectivity.html"
        files = {"file": open(data_server.path_to(file_name)).read()}
        monitor_user["data_id"] = file_name

        http_request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=monitor_user,
            files=files,
            verify=True,
        )
        assert http_request.status_code == HTTP_OK

        base_url = f"{TEST_URL}/plots/{instrument}/{run_number}/update/html/"

        # test GET request - authenticate with secret key
        url = f"{base_url}?key={_generate_key(instrument, run_number)}"
        http_request = requests.get(url)
        assert http_request.status_code == HTTP_OK
        assert http_request.text == files["file"]

        # test that getting the json should return not found
        http_request = requests.get(
            f"{TEST_URL}/plots/{instrument}/{run_number}/update/json/?key={_generate_key(instrument, run_number)}"
        )
        assert http_request.status_code == HTTP_NOT_FOUND
        assert http_request.text == "No data available for REF_M 12346"

        # test GET request - no key
        # TODO: this should return 401 unauthorized
        url = base_url
        http_request = requests.get(url)
        assert http_request.status_code == HTTP_OK

        # test GET request - wrong key
        url = f"{base_url}?key=WRONG-KEY"
        http_request = requests.get(url)
        assert http_request.status_code == HTTP_UNAUTHORIZED

    def test_upload_plot_data_json(self):
        # test that when you upload json you can get back the same stuff
        instrument = "instrument0"
        run_number = 123
        data = {"a": "A", "b": 1, "c": ["C", 2]}

        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
        }

        # get that there is currently no data
        response = requests.post(f"{TEST_URL}/plots/{instrument}/list/", data=monitor_user)
        assert response.status_code == HTTP_NOT_FOUND

        # now upload json data
        http_request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=monitor_user,
            files={"file": json.dumps(data)},
        )
        assert http_request.status_code == HTTP_OK

        # check list of data
        response = requests.post(f"{TEST_URL}/plots/{instrument}/list/", data=monitor_user)
        assert response.status_code == HTTP_OK
        data_list = response.json()
        assert len(data_list) == 1
        assert data_list[0]["run_number"] == "123"

        # now get the data as json
        response = requests.get(
            f"{TEST_URL}/plots/{instrument}/{run_number}/update/json/?key={_generate_key(instrument, run_number)}"
        )
        assert response.status_code == HTTP_OK
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == data

        # now try getting it as html, should fail
        response = requests.get(
            f"{TEST_URL}/plots/{instrument}/{run_number}/update/html/?key={_generate_key(instrument, run_number)}"
        )
        assert response.status_code == HTTP_NOT_FOUND
        assert response.text == "No data available for instrument0 123"

    def test_bad_request(self):
        instrument = "instrument1"
        run_number = 1234

        # test if missing files in post request
        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
        }

        # missing files
        http_request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=monitor_user,
        )
        assert http_request.status_code == HTTP_BAD_REQUEST

        # used filename instead of file in files
        http_request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=monitor_user,
            files={"filename": ""},
        )
        assert http_request.status_code == HTTP_BAD_REQUEST

    def test_unauthorized(self):
        # test get request unauthorized
        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
        }
        response = requests.get(f"{TEST_URL}/plots/instrument/list/", data=monitor_user)
        assert response.status_code == HTTP_UNAUTHORIZED

        # test wrong password
        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": "WrongPassword",
        }
        response = requests.post(f"{TEST_URL}/plots/instrument/list/", data=monitor_user)
        assert response.status_code == HTTP_UNAUTHORIZED

        # missing username and password
        response = requests.post(f"{TEST_URL}/plots/instrument/list/")
        assert response.status_code == HTTP_UNAUTHORIZED

    def test_session(self):
        # once you authenicate once with username and password you should be able to reuse the session with credentials
        session = requests.Session()

        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
        }

        # initial get should be unauthorized
        response = session.get(f"{TEST_URL}/plots/not_a_instrument/list/")
        assert response.status_code == HTTP_UNAUTHORIZED

        # do post with username and password, expect not found for "not_a_instrument"
        response = session.post(f"{TEST_URL}/plots/not_a_instrument/list/", data=monitor_user)
        response.status_code == HTTP_NOT_FOUND

        # now get with same session should be authorized
        response = session.get(f"{TEST_URL}/plots/not_a_instrument/list/")
        response.status_code == HTTP_NOT_FOUND


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
