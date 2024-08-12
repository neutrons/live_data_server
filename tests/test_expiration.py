import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

import psycopg
import requests

TEST_URL = "http://127.0.0.1"
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

    def test_expiration_plot(self, data_server):
        """Test the expiration field on DataRun model for upload_plot_data"""

        instrument = "TEST_INST"

        # request data
        filename = "reflectivity.html"
        files = {"file": open(data_server.path_to(filename)).read()}
        request_data = {
            **self.user_data,
            "data_id": filename,
        }

        # create a new run
        run_id = 12345
        request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_id}/upload_plot_data/", data=request_data, files=files, verify=True
        )
        assert request.status_code == HTTP_OK

        # create expired run
        run_id += 1
        expiration_date = datetime.now(tz=timezone.utc) - timedelta(days=365 * 3)
        request_data["expiration_date"] = expiration_date
        request = requests.post(
            f"{TEST_URL}/plots/{instrument}/{run_id}/upload_plot_data/",
            data=request_data,
            files=files,
            verify=True,
        )
        assert request.status_code == HTTP_OK

        request = requests.post(
            f"{TEST_URL}/plots/{instrument}/list/",
            data=self.user_data,
        )
        assert request.status_code == HTTP_OK

        r = request.json()
        assert r[0]["expired"] is False
        assert r[1]["expired"] is True

    def test_expiration_user(self, data_server):
        """Test the expiration field on DataRun model for upload_user_data"""

        filename = "reflectivity.json"
        with open(data_server.path_to(filename), "r") as file_handle:
            files = {"file": json.dumps(json.load(file_handle))}
        request_data = {
            **self.user_data,
            "data_id": filename,
        }

        # create a new run
        request = requests.post(
            f"{TEST_URL}/plots/{self.username}/upload_user_data/", data=request_data, files=files, verify=True
        )
        assert request.status_code == HTTP_OK

        # create expired run
        expiration_date = datetime.now(tz=timezone.utc) - timedelta(days=365 * 3)
        request_data["data_id"] = "reflectivity_expired.json"
        request_data["expiration_date"] = expiration_date
        request = requests.post(
            f"{TEST_URL}/plots/{self.username}/upload_user_data/", data=request_data, files=files, verify=True
        )
        assert request.status_code == HTTP_OK

        request = requests.post(
            f"{TEST_URL}/plots/{self.username}/list/",
            data=self.user_data,
        )
        assert request.status_code == HTTP_OK

        # check that expiration field for runs are marked correctly
        r = request.json()
        assert r[0]["expired"] is False
        assert r[1]["expired"] is True

    def test_deleting_expired(self):
        """Test the purge_expired_data command"""
        command = "docker exec -i live_data_server-livedata-1 bash -ic"
        subcommand = "conda activate livedata && cd app && coverage run manage.py purge_expired_data"
        # subcommand = "conda activate livedata && cd app && python manage.py purge_expired_data"
        output = subprocess.check_output([*command.split(" "), subcommand])
        print(output)

        # Ensure the above ran and worked
        r = requests.post(f"{TEST_URL}/plots/get_all_runs/", data=self.user_data)
        runs = r.json()
        assert len(runs) == 2
        assert all(run["expired"] is False for run in runs)
