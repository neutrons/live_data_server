# pylint: disable=invalid-name
"""
Test client that uploads data
"""

import argparse
import datetime
import json
import string
import sys

import numpy as np
import plotly.graph_objs as go
import requests
from plotly.offline import plot

sys.path.insert(0, "../live_data_server")

JSON_DATA = False
API_USER = "admin"
API_PWD = "adminadmin"
INSTRUMENT = "REF_L"
RUN_NUMBER = 123456
UPLOAD_URL = "http://127.0.0.1:8888/plots/$instrument/$run_number/upload_plot_data/"
USER_UPLOAD_URL = "http://127.0.0.1:8888/plots/$user/upload_user_data/"


def test_sine_wave(run_number, instrument):
    """
    Produce test sine wave plot
    """
    now = datetime.datetime.now()
    x = np.arange(1, now.second)
    y = np.sin(x)
    x2 = np.arange(1, now.second)
    y2 = np.sin(x + 1.0)
    err = 0.2 * np.ones(len(x))
    sys.path.append("/opt/postprocessing/postprocessing")
    from publish_plot import plot1d

    data = [[x, y, err, 2 * err], [x2, y2, err, 2 * err]]
    data_names = ["data", "offset"]
    return plot1d(
        run_number, data_list=data, instrument=instrument, x_title="theta", y_title="sin(theta)", data_names=data_names
    )


def get_plot_as_json():
    """
    Generates normal distributed 2D points
    Number of points depends on the real time seconds.
    """
    now = datetime.datetime.now()
    n_points = 100 * now.second
    mean = [0, 0]
    cov = [[1, 0], [0, 1]]
    x, y = np.random.multivariate_normal(mean, cov, n_points).T
    data = dict(
        x=x.tolist(), y=y.tolist(), mode="markers", name="points", marker=dict(color="rgb(0,0,0)", size=4, opacity=0.4)
    )
    return data


def get_plot_as_div():
    """
    Return a plot as a div
    """
    trace = go.Scatter(get_plot_as_json())
    data = [trace]

    layout = go.Layout(
        showlegend=False,
        autosize=False,
        width=800,
        height=700,
        xaxis=dict(
            range=[-4, 4],
        ),
        yaxis=dict(
            range=[-4, 4],
        ),
        margin=dict(t=50),
        hovermode="closest",
        bargap=0,
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type="div", include_plotlyjs=False)
    return plot_div


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test plot data producer")
    parser.add_argument("--json", help="Produce json data", action="store_true", dest="as_json")
    parser.add_argument("--html", help="Produce html data", action="store_false", dest="as_json")
    parser.add_argument("-r", metavar="runid", type=int, help="Run number (int)", dest="runid", required=True)
    parser.add_argument("-d", metavar="description", help="Data description", dest="description", required=False)
    parser.add_argument("-i", metavar="instrument", help="Instrument", dest="instrument", required=True)
    parser.add_argument("-c", metavar="config", help="Config file", dest="config_file", required=False)
    namespace = parser.parse_args()
    as_json_data = JSON_DATA if namespace.as_json is None else namespace.as_json

    monitor_user = {"username": API_USER, "password": API_PWD}
    url_template = string.Template(UPLOAD_URL)
    url = url_template.substitute(instrument=namespace.instrument, run_number=namespace.runid)

    if as_json_data:
        print("Producing json data")
        files = {"file": json.dumps(get_plot_as_json())}
    else:
        print("Producing html data")
        files = {"file": get_plot_as_div()}

    if namespace.config_file is not None:
        sys.path.append("/opt/postprocessing/postprocessing")
        from publish_plot import publish_plot

        request = publish_plot(namespace.instrument, namespace.runid, files=files, config_file=namespace.config_file)
    else:
        # request = test_sine_wave(namespace.runid, namespace.instrument)
        if namespace.description is not None:
            url_template = string.Template(USER_UPLOAD_URL)
            url = url_template.substitute(user=namespace.instrument)
            monitor_user["data_id"] = namespace.description

        request = requests.post(url, data=monitor_user, files=files, verify=False)
    print(request.status_code)
