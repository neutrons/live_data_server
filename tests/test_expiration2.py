import json
import os
from datetime import datetime, timedelta, timezone

import psycopg
import pytest
import requests

# from django.core.management import call_command
from django.test import Client

TEST_URL = "http://127.0.0.1"
HTTP_OK = requests.status_codes.codes["OK"]
HTTP_UNAUTHORIZED = requests.status_codes.codes["unauthorized"]
HTTP_NOT_FOUND = requests.status_codes.codes["NOT_FOUND"]
HTTP_BAD_REQUEST = requests.status_codes.codes["BAD_REQUEST"]

# @pytest.fixture
# def client():
#     return Client()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "live_data_server.live_data_server.settings")
c = Client()


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

    def test_expiration_plot(self, data_server):  # , client):
        """Test the expiration field on DataRun model for upload_plot_data"""
        # client = Client()
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
        request = c.post(
            f"{TEST_URL}/plots/{instrument}/{run_id}/upload_plot_data/", data=request_data, files=files, verify=True
        )
        # request = requests.post(
        #     f"{TEST_URL}/plots/{instrument}/{run_id}/upload_plot_data/", data=request_data, files=files, verify=True
        # )
        assert request.status_code == HTTP_OK
        return
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

    @pytest.mark.skip("Not implemented")
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

    @pytest.mark.skip("Not implemented")
    def test_deleting_expired(self):
        """Test the purge_expired view"""
        # r = requests.post(f"{TEST_URL}/plots/purge_expired/", data=self.user_data)
        # assert r.status_code == HTTP_OK
        # call_command("purge_expired_data.py")
        import subprocess

        subprocess.call(["python", "src/live_data_server/manage.py", "purge_expired_data"])

        # check if all expired runs are deleted
        r = requests.post(f"{TEST_URL}/plots/get_all_runs/", data=self.user_data)
        runs = r.json()
        assert len(runs) == 2
        assert all(run["expired"] is False for run in runs)
