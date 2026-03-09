import numpy as np
from scipy.stats import landau
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, Patch

x = np.linspace(-5, 20, 1000)
y = landau.pdf(x)

delay = 1
att = 0.2

delsig = np.interp(x-delay, x, y, left=0, right=0)
attsig = -att * y
cfd = delsig + attsig

# # Incoming signal
# sig = go.Scatter(x=x, y=y, name='sig')

# # Delayed signal
# delay = 1
# delsig_y = np.interp(x - delay, x, y, left=0, right=0)
# delsig = go.Scatter(x=x, y=delsig_y, name='delsig')

# # Attenuated and flipped signal
# att = 0.2
# attsig_y = -att * y
# attsig = go.Scatter(x=x, y=attsig_y, name='attsig')

# # CFD trigger sig (addition of delsig and attsig)
# CFDsig_y = delsig_y + attsig_y
# CFDsig = go.Scatter(x=x, y=CFDsig_y, name='CFDsig')

# fig = go.FigureWidget(
#     data=[sig, delsig, attsig, CFDsig],
#     layout=go.Layout(title="CFD Simulation", xaxis_range=(-5, 10), yaxis_range=(-0.7,0.7), width=600, height=400)
# )

fig = go.Figure()

fig.add_trace(go.Scatter(x=x, y=y, name="signal"))
fig.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
fig.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
fig.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))

fig.update_layout(
    title="CFD Simulation",
    # xaxis_title="",
    # yaxis_title="",
    # plot_bgcolor="",
    xaxis_range=(-5, 10), 
    yaxis_range=(-0.7,0.7), 
    width=1000, 
    height=600
)

app = Dash(__name__)

app.layout = html.Div([

    dcc.Graph(figure=fig, id="cfd-plot"),

    html.Label("loc"),
    dcc.Slider(id="loc", min=-2, max=5, step=0.1, value=0, updatemode="drag"),

    html.Label("scale"),
    dcc.Slider(id="scale", min=0.5, max=3, step=0.1, value=1, updatemode="drag"),

    html.Label("Delay"),
    dcc.Slider(id="delay", min=0, max=5, step=0.1, value=1, updatemode="drag"),

    html.Label("Attenuation"),
    dcc.Slider(id="att", min=0, max=1, step=0.05, value=0.2, updatemode="drag"),
])


@app.callback(
    Output("cfd-plot", "figure"),
    Input("delay", "value"),
    Input("att", "value"),
    Input("loc", "value"),
    Input("scale", "value"),
)

# def update_plot(delay, att, loc, scale):

#     y = landau.pdf(x, loc=loc, scale=scale)

#     delsig = np.interp(x-delay, x, y, left=0, right=0)
#     attsig = -att * y
#     cfd = delsig + attsig

#     fig = go.Figure()

#     fig.add_trace(go.Scatter(x=x, y=y, name="signal"))
#     fig.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
#     fig.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
#     fig.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))

#     return fig

def update_plot(delay, att, loc, scale):

    y = landau.pdf(x, loc=loc, scale=scale)

    delsig = np.interp(x-delay, x, y, left=0, right=0)
    attsig = -att * y
    cfd = delsig + attsig

    patch = Patch()
    patch["data"][0]["y"] = y
    patch["data"][1]["y"] = delsig
    patch["data"][2]["y"] = attsig
    patch["data"][3]["y"] = cfd

    return patch
    

if __name__ == "__main__":
    app.run(debug=True)