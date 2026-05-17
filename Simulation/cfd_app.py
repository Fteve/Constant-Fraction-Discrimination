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
arm = 0
nzOn = 0

amplStepSize = 0.01 #step size for amplitude slide bar

x = np.linspace(-5, 20, 1000)

f, y, delsig, attsig, cfd = signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn)

zcross = zero_crossing(x, y, cfd, arm)
tr = rise_time(x,y)

# Energy probability distribution
xP = np.linspace(0, 8, 400)
fProb = lambda x: -ampl * landau.pdf(x, loc=2, scale=scale)
probDist = -fProb(xP)
# Looks for mpv including non-sampled points
mpvX = minimize_scalar(fProb).x
mpvY = landau.pdf(mpvX, loc=2, scale=scale)

#---------------------------------------------------------------------------------------------------
# Generate figures and table
#---------------------------------------------------------------------------------------------------
fig1 = go.Figure()
fig2 = go.Figure()
figProb = go.Figure()

# formatting
fig1.update_layout(
    showlegend=True,
    title="CFD Model",
    title_font_size=32,
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
        bgcolor='rgba(0,0,0,0)', 
        bordercolor='black',
        borderwidth=1
    ),
    margin=dict(l=50, r=150, t=80, b=50)
)

fig2.update_layout(
    showlegend=True,
    title="CFD Model",
    title_font_size=32,
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
        bgcolor='rgba(0,0,0,0)', 
        bordercolor='black',
        borderwidth=1
    ),
    margin=dict(l=50, r=150, t=80, b=50)
)

figProb.update_layout(
    showlegend=False, 
    title="Amplitude Probability Density Function",
    title_font_size=32,
    xaxis_range=(0, 8), 
    yaxis_range=(0,0.6), 
    width=1050, 
    height=600,
    autosize=False,
    # legend=dict(
    #     x=1.01,    # slightly outside the figure
    #     y=1,
    #     xanchor='left',   # anchor relative to x
    #     yanchor='top',
    #     bgcolor='rgba(0,0,0,0)', 
    #     bordercolor='black',
    #     borderwidth=1
    # ),
    margin=dict(l=50, r=150, t=80, b=50)
)

# add traces
fig1.add_trace(go.Scatter(x=x, y=y, name="input"))
fig1.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
fig1.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
fig1.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))
fig1.add_trace(go.Scatter(x=[-5,11], y=[arm,arm], mode="lines", name="arming thrs", line=dict(dash="dash")))
fig1.add_trace(go.Scatter(x=[zcross], y=[0], name="zero-crossing", mode="markers", marker_size=8))

fig2.add_trace(go.Scatter(x=x, y=cfd))

figProb.add_trace(go.Scatter(x=xP, y=probDist))
figProb.add_trace(go.Scatter(x=[mpvX], y=[mpvY], name="amplitude", mode="markers", marker_size=14, marker_symbol="x"))

# table for Sweep Graph
table = go.Figure(data=[go.Table(
    header=dict(values=['Trace', 'Amplitude', 'Delay', 'Attenuation', 'Zero-Crossing', 'Rise Time', 'Peak'],
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

app.layout = build_layout(fig1, fig2, figProb, nzOn, loc, scale, ampl, delay, att, sigma, sat, arm, table, amplStepSize)

register_callbacks(app, x, xP, probDist, amplStepSize)


if __name__ == "__main__":
    app.run(debug=True)