import numpy as np
from scipy.stats import landau
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, Patch, no_update, ctx

from functions import signalCalcs, lin_interp_x, zero_crossing, rise_time
from layout import build_layout
from callbacks import register_callbacks

# initial parameters
loc = 0
scale = 0.5
sat = 0.7
ampl = 1
delay = 1
att = 0.2
sigma = 0.01
nzOn = 0

x = np.linspace(-5, 20, 1000)

f, y, delsig, attsig, cfd = signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn)

zcross = zero_crossing(x, cfd)
tr = rise_time(x,y)
# Looks for mpv including non-sampled points
mpv = minimize_scalar(f).x

#---------------------------------------------------------------------------------------------------
# Generate figures and table
#---------------------------------------------------------------------------------------------------
fig1 = go.Figure()
fig2 = go.Figure()

# formatting
fig1.update_layout(
    showlegend=True,  # or always True for both
    title="CFD Simulation",
    xaxis_range=(-5, 10), 
    yaxis_range=(-0.5,1), 
    width=1050, 
    height=600,
    autosize=False,
    legend=dict(
        x=1.01,    # slightly outside the figure
        y=1,
        xanchor='left',   # anchor relative to x
        yanchor='top',
        bgcolor='rgba(0,0,0,0)',  # optional: transparent
        bordercolor='black',
        borderwidth=1
    ),
    margin=dict(l=50, r=150, t=80, b=50)
)

fig2.update_layout(
    showlegend=True,  # or always True for both
    title="CFD Simulation",
    xaxis_range=(-5, 10), 
    yaxis_range=(-0.5,1), 
    width=1050, 
    height=600,
    autosize=False,
    legend=dict(
        x=1.01,    # slightly outside the figure
        y=1,
        xanchor='left',   # anchor relative to x
        yanchor='top',
        bgcolor='rgba(0,0,0,0)',  # optional: transparent
        bordercolor='black',
        borderwidth=1
    ),
    margin=dict(l=50, r=150, t=80, b=50)
)

# add traces
fig1.add_trace(go.Scatter(x=x, y=y, name="signal"))
fig1.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
fig1.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
fig1.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))
fig1.add_trace(go.Scatter(x=[zcross, zcross], y=[-3, 3], mode="lines", name="zero crossing", line=dict(dash="dash")))

fig2.add_trace(go.Scatter(x=x, y=cfd))

# table for Sweep Graph
table = go.Figure(data=[go.Table(
    header=dict(values=['Trace', 'Amplitude', 'Delay', 'Attenuation', 'Zero Crossing', 'Rise Time', 'MPV'],
                # line_color='darkslategray',
                # fill_color='lightskyblue',
                align='left'),

    cells=dict(values=[[1], [], [], [], [], [], []],
            #    line_color='darkslategray',
            #    fill_color='lightcyan',
               align='left'))
])

table.update_layout(
    width=650,
    height=2000,
    margin=dict(l=0, r=0, t=0, b=0),
)

#---------------------------------------------------------------------------------------------------
# Web App Layout
#---------------------------------------------------------------------------------------------------
app = Dash(__name__)

app.layout = build_layout(fig1, fig2, nzOn, loc, scale, ampl, delay, att, sigma, sat, table)

register_callbacks(app, x)


if __name__ == "__main__":
    app.run(debug=True)