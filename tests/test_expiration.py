import os
import subprocess
from datetime import datetime, timedelta, timezone

import psycopg
import requests

from tests.conftest import generate_key

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

        # Verify both runs were created (we can't easily check expiration without the list endpoint)
        # But we can verify they're retrievable
        response1 = requests.get(
            f"{TEST_URL}/plots/{instrument}/12345/update/html/",
            headers={"Authorization": generate_key(instrument, 12345)},
            timeout=10,
        )
        assert response1.status_code == HTTP_OK

        response2 = requests.get(
            f"{TEST_URL}/plots/{instrument}/12346/update/html/",
            headers={"Authorization": generate_key(instrument, 12346)},
            timeout=10,
        )
        assert response2.status_code == HTTP_OK

    def test_deleting_expired(self):
        """Test the purge_expired_data command"""
        command = "docker exec -i live_data_server-django-1 bash -ic"
        subcommand = "cd app && pixi run -e deploy coverage run manage.py purge_expired_data"
        output = subprocess.check_output([*command.split(" "), subcommand])
        print(output)

        # Ensure the above ran and worked
        conn = psycopg.connect(
            dbname=os.environ.get("DATABASE_NAME"),
            user=os.environ.get("DATABASE_USER"),
            password=os.environ.get("DATABASE_PASS"),
            port=os.environ.get("DATABASE_PORT"),
            host="localhost",
        )
        cur = conn.cursor()

        cur.execute("SELECT * FROM plots_datarun")
        results = cur.fetchall()
        print(f"Runs after purge: {len(results)}")
        for i in results:
            print(i)
        assert len(results) == 1

        # Plots after purge
        cur.execute("SELECT * FROM plots_plotdata")
        results = cur.fetchall()
        print(f"Plots after purge: {len(results)}")
        assert len(results) == 1  # Only one non-expired run should remain
