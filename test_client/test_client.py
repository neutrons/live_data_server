#pylint: disable=invalid-name
"""
    Test client that uploads data
"""
from __future__ import print_function
import sys
import string
import requests
import datetime
from plotly.offline import plot
import plotly.graph_objs as go
import numpy as np
sys.path.insert(0, '../live_data_server')

GENERATE_DATA = True
API_USER = 'admin'
API_PWD = 'adminadmin'
INSTRUMENT = "REF_L"
RUN_NUMBER = 123456
FILE_PATH = "test_plot.html"
UPLOAD_URL = "http://127.0.0.1:8000/plots/$instrument/$run_number/upload_plot_data/"


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
        x=x.tolist(), y=y.tolist(), mode='markers', name='points',
        marker=dict(color='rgb(0,0,0)', size=4, opacity=0.4)
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
        xaxis=dict(range=[-4, 4],),
        yaxis=dict(range=[-4, 4],),
        margin=dict(t=50),
        hovermode='closest',
        bargap=0,
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

if __name__ == "__main__":
    monitor_user = {'username': API_USER, 'password': API_PWD}
    url_template = string.Template(UPLOAD_URL)
    url = url_template.substitute(instrument=INSTRUMENT, run_number=RUN_NUMBER)

    if GENERATE_DATA:
        files = {'file': get_plot_as_div()}
    else:
        files = {'file': open(FILE_PATH, 'rb')}

    request = requests.post(url, data=monitor_user, files=files, verify=False)
    print(request.status_code)
