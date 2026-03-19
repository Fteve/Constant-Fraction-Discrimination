import numpy as np
from scipy.stats import landau
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, State, Patch, no_update

# initial parameters
loc = 0
scale = 0.5
sat = 0.6
ampl = 1
delay = 1
att = 0.2

# initial signal values
x = np.linspace(-5, 20, 1000)
f = lambda x: -ampl * landau.pdf(x, loc=loc, scale=scale) # lambda function for mpv calculation
y = -f(x)

# y = ampl * landau.pdf(x, loc=loc, scale=scale)

# calculated signals
delsig = np.interp(x-delay, x, y, left=0, right=0)
attsig = -att * y
cfd = delsig + attsig


def lin_interp_x(x,y,i,crossing):
    # points around crossing
    x1, x2 = x[i], x[i+1]
    y1, y2 = y[i], y[i+1]
    
    # linear interpolation
    x_interp = x1 + (crossing - y1)*(x2-x1)/(y2-y1)
    
    return x_interp

# define zero crossing
def zero_crossing(x, y):

    # indices where sign changes
    sign_change = np.where(np.diff(np.sign(y)))[0]

    if len(sign_change) == 0:
        return None  # no zero crossing
    elif len(sign_change) == 2:
        i = sign_change[1]
    else:
        i = sign_change[0]

    x_zero = lin_interp_x(x,y,i,0)

    return x_zero

def rise_time(x,y):
    maximum = max(y)

    # indices of *near 10% and 90% of amplitude
    h_index = np.where(np.diff(np.sign(y - 0.9*maximum)))[0][0]
    l_index = np.where(np.diff(np.sign(y- 0.1*maximum )))[0][0]
    
    hi = lin_interp_x(x, y, h_index, 0.9*maximum)
    lo = lin_interp_x(x, y, l_index, 0.1*maximum)

    tr = hi - lo
    
    return tr

zcross = zero_crossing(x, cfd)
tr = rise_time(x,y)
# Looks for mpv including non-sampled points
mpv = minimize_scalar(f).x


# generate figures
fig1 = go.Figure()

fig1.update_layout(
    title="CFD Simulation",
    # xaxis_title="",
    # yaxis_title="",
    # plot_bgcolor="",
    xaxis_range=(-5, 10), 
    yaxis_range=(-0.7,0.7), 
    width=1000, 
    height=600
)

# fig 2 with identical format
fig2 = go.Figure()

fig1.update_layout(
    title="CFD Simulation",
    # xaxis_title="",
    # yaxis_title="",
    # plot_bgcolor="",
    xaxis_range=(-5, 10), 
    yaxis_range=(-0.7,0.7), 
    width=1000, 
    height=600
)

# add traces
fig1.add_trace(go.Scatter(x=x, y=y, name="signal"))
fig1.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
fig1.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
fig1.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))
fig1.add_trace(go.Scatter(x=[zcross, zcross], y=[-3, 3], mode="lines", name="zero crossing", line=dict(dash="dash")))

fig2.add_trace(go.Scatter(x=x, y=cfd, name="sweep 1"))


# web app layout
app = Dash(__name__)

app.layout = html.Div([
    dcc.Store(id="active-graph", data="graph1"),
    dcc.Store(id="graph1-store", data=fig1),
    dcc.Store(id="graph2-store", data=fig2),

    html.Div([
         
        html.Div([
            html.Button('Graph 1', id='show-graph-1', n_clicks=0),
            html.Button('Graph 2', id='show-graph-2', n_clicks=0),

            dcc.Graph(figure=fig1, id="cfd-plot", className="graph-container"),
            
            html.Div([
                html.Div([
                    html.H4("MPV:", className="slider-label"),
                    html.Div(id="mpv", className="display"),
                ]),

                html.Div([
                    html.H4("Rise Time:", className="slider-label"),
                    html.Div(id="rise-time", className="display"),
                ]),

                html.Div([
                    html.H4("Zero Crossing:", className="slider-label"),
                    html.Div(id="zero-crossing-value", className="display"),
                ]),
            ],
            className="display-container"
            ),

            html.Button("Add Trace", id="add-trace", n_clicks=0)
        ],
        className="left-column"
        )
    ]),


    html.Div([
        dcc.Checklist(
            id="slider-toggle",
            options=[
                {"label": "Location", "value": "loc"},
                {"label": "Scale", "value": "scale"},
                {"label": "Saturation", "value": "sat"},
                {"label": "Amplitude", "value": "ampl"},
                {"label": "Delay", "value": "delay"},
                {"label": "Attenuation", "value": "att"},
                
            ],
            value=["ampl", "delay", "att"],
            className="checklist"
        ),

        html.Div([
            html.Label("loc"),
            dcc.Slider(id="loc", min=-2, max=5, step=0.05, value=loc, updatemode="drag"),
        ], id="locSlider", className="slider-container"),

        html.Div([
            html.Label("scale"),
            dcc.Slider(id="scale", min=0.1, max=2, step=0.02, value=scale, updatemode="drag"),
        ], id="scaleSlider", className="slider-container"),

        html.Div([
            html.Label("Saturation"),
            dcc.Slider(id="sat", min=0.3, max=1, step=0.01, value=sat, updatemode="drag"),
        ], id="satSlider", className="slider-container"),

        html.Div([
            html.Label("Amplitude"),
            dcc.Slider(id="ampl", min=0.1, max=3, step=0.02, value=ampl, updatemode="drag"),
        ], id="amplSlider", className="slider-container"),

        html.Div([
            html.Label("Delay"),
            dcc.Slider(id="delay", min=0, max=3.5, step=0.05, value=delay, updatemode="drag"),
        ], id="delaySlider", className="slider-container"),

        html.Div([
            html.Label("Attenuation"),
            dcc.Slider(id="att", min=0, max=1, step=0.01, value=att, updatemode="drag"),
        ], id="attSlider", className="slider-container"),

    ],
    className="right-column"
    )

],
className="whole-container"
)       


@app.callback(
    # Output("cfd-plot", "figure"),
    Output("graph1-store", "data"),
    # Output("graph2-store", "data"),
    Output("zero-crossing-value", "children"),
    Output("rise-time", "children"),
    Output("mpv", "children"),
    Input("loc", "value"),
    Input("scale", "value"),
    Input("sat", "value"),
    Input("ampl", "value"),
    Input("delay", "value"),
    Input("att", "value"),
    Input("active-graph", "data"),
    # State("graph1-store", "data"),
    # State("graph2-store", "data")
)
def update_traces(loc, scale, sat, ampl, delay, att, activeGraph):
    if activeGraph == "graph2":
        
        return no_update, no_update, no_update, no_update
    
    
    else: 
        f = lambda x: -ampl * landau.pdf(x, loc=loc, scale=scale)
        y = -f(x)

        for i in range(len(x)):
                if (y[i] > sat):
                    y[i] = sat

        delsig = np.interp(x-delay, x, y, left=0, right=0)
        attsig = -att * y
        cfd = delsig + attsig

        zcross = zero_crossing(x, cfd)
        tr = rise_time(x,y)
        mpv = minimize_scalar(f).x

        patch = Patch()
        patch["data"][0]["y"] = y
        patch["data"][1]["y"] = delsig
        patch["data"][2]["y"] = attsig
        patch["data"][3]["y"] = cfd
        patch["data"][4]["x"] = [zcross,zcross]

        return patch, f"{zcross:.3f}", f"{tr:.3f}", f"{mpv:.3f}"
    


@app.callback(
        Output("cfd-plot", "figure"),
        Input("active-graph", "data"),
        Input("graph1-store", "data"),
        Input("graph2-store", "data"),
)
def update_graph(activeGraph, fig1, fig2):
    if activeGraph == "graph2":
        return fig2
    else:
        return fig1




@app.callback(
    Output("active-graph", "data"),
    Input("show-graph-1", "n_clicks"),
    Input("show-graph-2", "n_clicks")
)
def switch_graph(graph1Clicks, graph2Clicks):
    if graph2Clicks > graph1Clicks:
        activeGraph = "graph2"
    else:
        activeGraph = "graph1"

    return activeGraph

@app.callback(
    Output("graph2-store", "data"),
    Input("add-trace", "n_clicks"),
    State("active-graph", "data"),
    State("graph2-store", "data"),
    State("loc", "value"),
    State("scale", "value"),
    State("sat", "value"),
    State("ampl", "value"),
    State("delay", "value"),
    State("att", "value"),
)
def addTrace(n_clicks, activeGraph, fig2, loc, scale, sat, ampl, delay, att):
    if activeGraph == "graph2":

        f = lambda x: -ampl * landau.pdf(x, loc=loc, scale=scale)
        y = -f(x)

        for i in range(len(x)):
                if (y[i] > sat):
                    y[i] = sat

        delsig = np.interp(x-delay, x, y, left=0, right=0)
        attsig = -att * y
        cfd = delsig + attsig
        
        s = "trace %d"
        traceName = s % n_clicks
        new_trace = go.Scatter(x=x, y=cfd, name=traceName)

        fig2["data"].append(new_trace)
        return fig2

    return no_update


@app.callback(
    Output("locSlider", "style"),
    Output("scaleSlider", "style"),
    Output("satSlider", "style"),
    Output("amplSlider", "style"),
    Output("delaySlider", "style"),
    Output("attSlider", "style"), 
    Input("slider-toggle", "value"),
)
def toggling(selected):
    loc_style = {"display": "block"} if "loc" in selected else {"display": "none"}
    scale_style = {"display": "block"} if "scale" in selected else {"display": "none"}
    sat_style = {"display": "block"} if "sat" in selected else {"display": "none"}
    ampl_style = {"display": "block"} if "ampl" in selected else {"display": "none"}
    delay_style = {"display": "block"} if "delay" in selected else {"display": "none"}
    att_style = {"display": "block"} if "att" in selected else {"display": "none"}

    return loc_style, scale_style, sat_style, ampl_style, delay_style, att_style

if __name__ == "__main__":
    app.run(debug=True)