"""
    Utility functions to support views.
"""
import datetime
import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go

def get_plot_as_json():
    """
        Generates normal distributed 2D points
        Number of points depends on the real time seconds.
    """
    now = datetime.datetime.now()
    n_points = 100 * now.second;
    mean = [0, 0]
    cov = [[1, 0], [0, 1]]  # diagonal covariance
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
        xaxis=dict(
            range=[-4, 4],
        ),
        yaxis=dict(
            range=[-4, 4],
        ),
        margin=dict(
            t=50
        ),
        hovermode='closest',
        bargap=0,
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
