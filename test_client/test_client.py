"""
Test client that uploads data
"""

import argparse
import datetime
import json
import os
import string

import numpy as np
import plotly.graph_objs as go
import requests
from plotly.offline import plot

API_USER = os.environ.get("DJANGO_SUPERUSER_USERNAME")
API_PWD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
UPLOAD_URL = "http://127.0.0.1/plots/$instrument/$run_number/upload_plot_data/"
USER_UPLOAD_URL = "http://127.0.0.1/plots/$user/upload_user_data/"


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
    namespace = parser.parse_args()

    monitor_user = {"username": API_USER, "password": API_PWD}
    url_template = string.Template(UPLOAD_URL)
    url = url_template.substitute(instrument=namespace.instrument, run_number=namespace.runid)

    if namespace.as_json:
        print("Producing json data")
        files = {"file": json.dumps(get_plot_as_json())}
    else:
        print("Producing html data")
        files = {"file": get_plot_as_div()}

    if namespace.description is not None:
        url_template = string.Template(USER_UPLOAD_URL)
        url = url_template.substitute(user=namespace.instrument)
        monitor_user["data_id"] = namespace.description

    request = requests.post(url, data=monitor_user, files=files, verify=False)
    print(request.status_code)
