import hashlib
import os

import psycopg
import requests

TEST_URL = "http://127.0.0.1:8000"
HTTP_OK = requests.status_codes.codes["OK"]
HTTP_UNAUTHORIZED = requests.status_codes.codes["unauthorized"]
HTTP_NOT_FOUND = requests.status_codes.codes["NOT_FOUND"]
HTTP_BAD_REQUEST = requests.status_codes.codes["BAD_REQUEST"]


class TestLiveDataServer:
    # authenticate with username and password
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    user_data = {"username": username, "password": password}

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
        # load html plot as autoreduce service
        filename = "reflectivity.html"
        files = {"file": open(data_server.path_to(filename)).read()}
        request_data = {
            **self.user_data,
            "data_id": filename,
        }

        request = requests.post(
            f"{TEST_URL}/plots/TEST_INST/12345/upload_plot_data/", data=request_data, files=files, verify=True
        )
        assert request.status_code == HTTP_OK

    def test_get_request(self, data_server):
        """Test GET request for HTML data like from monitor.sns.gov"""
        instrument = "REF_M"
        run_number = 12346

        # load html plot as autoreduce service
        filename = "reflectivity.html"
        files = {"file": open(data_server.path_to(filename)).read()}
        request_data = {
            **self.user_data,
            "data_id": filename,
        }

        request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=request_data,
            files=files,
            verify=True,
        )
        assert request.status_code == HTTP_OK

        base_url = f"{TEST_URL}/plots/{instrument}/{run_number}/update/html/"

        # test GET request - authenticate with secret key
        url = f"{base_url}?key={_generate_key(instrument, run_number)}"
        request = requests.get(url)
        assert request.status_code == HTTP_OK
        assert request.text == files["file"]

        # test GET request - no key
        url = base_url
        request = requests.get(url)
        assert request.status_code == HTTP_UNAUTHORIZED

        # test GET request - wrong key
        url = f"{base_url}?key=WRONG-KEY"
        request = requests.get(url)
        assert request.status_code == HTTP_UNAUTHORIZED

        # test GET request - wrong key
        request = requests.get(
            base_url,
            headers={"Authorization": "WRONG-KEY"},
        )
        assert request.status_code == HTTP_UNAUTHORIZED

    def test_bad_request(self):
        instrument = "instrument1"
        run_number = 1234

        # test if missing files in post request
        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
        }

        # missing files
        request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=monitor_user,
        )
        assert request.status_code == HTTP_BAD_REQUEST

        # used filename instead of file in files
        request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_number}/upload_plot_data/",
            data=monitor_user,
            files={"filename": ""},
        )
        assert request.status_code == HTTP_BAD_REQUEST

    def test_unauthorized(self):
        # test uploading without credentials
        response = requests.post(f"{TEST_URL}/plots/TEST_INST/999/upload_plot_data/")
        assert response.status_code == HTTP_UNAUTHORIZED

    def test_session(self):
        # Test that session authentication works for uploads
        session = requests.Session()

        monitor_user = {
            "username": os.environ.get("DJANGO_SUPERUSER_USERNAME"),
            "password": os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
        }

        # Upload should work with authenticated session
        files = {"file": "<div>Test</div>"}
        response = session.post(f"{TEST_URL}/plots/TEST_INST/888/upload_plot_data/", data=monitor_user, files=files)
        assert response.status_code == HTTP_OK

        # Verify session authentication persists without re-providing credentials
        files = {"file": "<div>Second upload</div>"}
        response = session.post(
            f"{TEST_URL}/plots/TEST_INST/889/upload_plot_data/",
            files=files
        )
        assert response.status_code == HTTP_OK


def _generate_key(instrument, run_id):
    """
    Generate a secret key for a run on a given instrument
    Used to simulate clients sending GET-requests using a secret key
    @param instrument: instrument name
    @param run_id: run number
    """
    secret_key = os.environ.get("LIVE_PLOT_SECRET_KEY")
    if secret_key is None or len(secret_key) == 0:
        return None

    return hashlib.sha1(f"{instrument.upper()}{secret_key}{run_id}".encode("utf-8")).hexdigest()
