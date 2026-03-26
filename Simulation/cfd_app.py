import numpy as np
from scipy.stats import landau
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, State, Patch, no_update, ctx

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

# Function to calculate component signals
def signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn):
    f = lambda x: -ampl * landau.pdf(x, loc=loc, scale=scale)
    y = -f(x)

    if nzOn:
        noise = np.random.normal(loc=0, scale=sigma, size=len(x))
        y = y + noise

    for i in range(len(x)):
            if (y[i] > sat):
                y[i] = sat

    delsig = np.interp(x-delay, x, y, left=0, right=0)
    attsig = -att * y
    cfd = delsig + attsig

    return f, y, delsig, attsig, cfd

f, y, delsig, attsig, cfd = signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn)

# Function to calculate interpolation
# Used in zero crossing and rise time calculations
def lin_interp_x(x,y,i,crossing):
    x1, x2 = x[i], x[i+1]
    y1, y2 = y[i], y[i+1]
    
    x_interp = x1 + (crossing - y1)*(x2-x1)/(y2-y1)
    
    return x_interp


# Function to calculate zero crossing
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

# Function to calculate rise time
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
        x=1.02,    # slightly outside the figure
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
        x=1.02,    # slightly outside the figure
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

app.layout = html.Div([
    dcc.Store(id="active-graph", data="graph1"),
    dcc.Store(id="graph1-store", data=fig1),
    dcc.Store(id="graph2-store", data=fig2),
    dcc.Store(id="table-data", data=[]),
    dcc.Store(id="visibility", data=[[],[]]),
    dcc.Store(id="noise-toggle", data=nzOn),

    html.Div([
         
        html.Div([
            html.Div([
                html.Button('Mode: Signal Components', id='show-graph-1', n_clicks=0, className="mode-button"),
                # html.Button('Sweep', id='show-graph-2', n_clicks=0, className="mode-button"),
            ],
            className="mode-button-container"),
            

            dcc.Graph(figure=fig1, id="cfd-plot", className="graph-container"),
            
            html.Div([
                html.Div([
                    html.H4("Zero Crossing:", className="display-label"),
                    html.Div(id="zero-crossing-value", className="display"),
                ]),

                html.Div([
                    html.H4("Rise Time:", className="display-label"),
                    html.Div(id="rise-time", className="display"),
                ]),

                html.Div([
                    html.H4("MPV:", className="display-label"),
                    html.Div(id="mpv", className="display"),
                ]), 
            ],
            className="display-container"
            ),
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
                {"label": "Noise", "value": "nz"}
                
            ],
            value=["ampl", "delay", "att"],
            className="checklist"
        ),

        html.Div([
            html.Label("Location"),
            dcc.Slider(id="loc", min=-2, max=5, step=0.05, value=loc, updatemode="drag"),
        ], id="locSlider", className="slider-container"),

        html.Div([
            html.Label("Scale"),
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

        html.Div([
            html.Label("Noise"),
            dcc.Slider(id="nz", min=0, max=0.05, step=0.001, value=sigma, updatemode="drag"),
        ], id="nzSlider", className="slider-container"),

        html.Div([
            html.Button("Add Trace", id="add-trace", n_clicks=0, className="trace-button"),

            html.Button("Clear", id="clear", n_clicks=0, className="trace-button"),
        ],
        className="trace-buttons-container"),

        dcc.Graph(
            id='sweep-table', figure=table, className="table") 

    ],
    className="right-column"
    )

],
className="whole-container"
)       


#---------------------------------------------------------------------------------------------------
# Function to show the correct graph
# -> Takes the figure data from respective stores.
# -> Prevents multiple functions from having "cfd-plot" as output.
#---------------------------------------------------------------------------------------------------
@app.callback(
        Output("cfd-plot", "figure"),
        Output("sweep-table", "style"),
        Output("add-trace", "style"),
        Output("clear", "style"),
        Input("active-graph", "data"),
        Input("graph1-store", "data"),
        Input("graph2-store", "data"),
        Input("visibility", "data"),
)
def update_graph(activeGraph, fig1, fig2, visibility):
    if activeGraph == "graph2":
        if visibility[1]:
            for i, trace in enumerate(fig2["data"]):
                trace["visible"] = visibility[1][i]

        return fig2, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
    else:   
        if visibility[0]:
            for i, trace in enumerate(fig1["data"]):
                trace["visible"] = visibility[0][i]

        return fig1, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    

#---------------------------------------------------------------------------------------------------
# Function to change graphs with the graph buttons
#---------------------------------------------------------------------------------------------------
@app.callback(
    Output("active-graph", "data"),
    Output("show-graph-1", "children"),
    Input("show-graph-1", "n_clicks"),
    State("active-graph", "data"),
    # Input("show-graph-2", "n_clicks")
)
def switch_graph(graph1Clicks, activeGraph):
    # button_id = ctx.triggered_id

    # if button_id == "show-graph-2":
    #     activeGraph = "graph2"
    # else:
    #     activeGraph = "graph1"

    if activeGraph == "graph2":
        return "graph1", "Mode: Signal Components"
    else:
        return "graph2", "Mode: Output Trace"

    # return activeGraph


#---------------------------------------------------------------------------------------------------
# Function to update the Signal Components Graph
# -> Update traces of graph with slider inputs.
# -> Also displays MPV, Rise Time, and Zero Crossing values.
#---------------------------------------------------------------------------------------------------
@app.callback(
    Output("graph1-store", "data"),
    Output("zero-crossing-value", "children", allow_duplicate=True),
    Output("rise-time", "children", allow_duplicate=True),
    Output("mpv", "children", allow_duplicate=True),
    Input("loc", "value"),
    Input("scale", "value"),
    Input("sat", "value"),
    Input("ampl", "value"),
    Input("delay", "value"),
    Input("att", "value"),
    Input("nz", "value"),
    Input("active-graph", "data"),
    Input("noise-toggle", "data"),
    prevent_initial_call=True,
)
def update_graph1(loc, scale, sat, ampl, delay, att, sigma, activeGraph, nzOn):
    if activeGraph == "graph2":
        return no_update, no_update, no_update, no_update
    
    else: 

        f, y, delsig, attsig, cfd = signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn)
            
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
    

#---------------------------------------------------------------------------------------------------
# Function to update the Sweep Graph
# -> If function triggered by "Add Trace" button, current position of moveable trace is saved.
# -> Otherwise, update the moveable trace based on inputs.
#---------------------------------------------------------------------------------------------------
@app.callback(
    Output("graph2-store", "data"),
    Output("sweep-table", "figure"),
    Output("zero-crossing-value", "children", allow_duplicate=True),
    Output("rise-time", "children", allow_duplicate=True),
    Output("mpv", "children", allow_duplicate=True),
    Output('table-data', 'data'),
    Input("loc", "value"),
    Input("scale", "value"),
    Input("sat", "value"),
    Input("ampl", "value"),
    Input("delay", "value"),
    Input("att", "value"),
    Input("nz", "value"),
    Input("active-graph", "data"),
    Input("add-trace", "n_clicks"),
    Input("clear", "n_clicks"),
    Input("noise-toggle", "data"),
    State("graph2-store", "data"),
    State("zero-crossing-value", "children"),
    State("rise-time", "children"),
    State("mpv", "children"),
    State('table-data', 'data'),
    
    prevent_initial_call=True,
)
def updateGraph2(loc, scale, sat, ampl, delay, att, sigma, activeGraph, n_clicks, n_clicksC, nzOn, fig2, zcross, tr, mpv, tableData,):
    if activeGraph == "graph1":
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    
    else: 
        button_id = ctx.triggered_id

        f, y, delsig, attsig, cfd = signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn)

        if button_id == "add-trace" or button_id == "clear":

            if button_id == "add-trace":
                # capture trace
                s = "trace %d"
                traceName = s % n_clicks
                new_trace = go.Scatter(x=x, y=cfd, name=traceName)
                fig2["data"].append(new_trace)

                # update table
                # new_row = [n_clicks, mpv, tr, zcross]
                new_row = {
                    "trace": n_clicks,
                    "ampl": ampl,
                    "delay": delay,
                    "att": att, 
                    "zcross": zcross,
                    "tr": tr,
                    "mpv": mpv,
                }

                tableData.append(new_row)
     
            else:
                fig2["data"] = fig2["data"][:1]
                tableData = []
                print("here!")


            values = [
                [row["trace"] for row in tableData],
                [row["ampl"] for row in tableData],
                [row["delay"] for row in tableData],
                [row["att"] for row in tableData],
                [row["zcross"] for row in tableData],
                [row["tr"] for row in tableData],
                [row["mpv"] for row in tableData],
            ] 
            
            table = go.Figure(data=[go.Table(
                header=dict(values=['Trace', 'Amplitude', 'Delay', 'Attenuation', 'Zero Crossing', 'Rise Time', 'MPV'],
                            align='left'),
                cells=dict(values=values,
                        align='left'))
            ])

            table.update_layout(
                width=650,
                height=2000,
                margin=dict(l=0, r=0, t=0, b=0),
            )

            return fig2, table, no_update, no_update, no_update, tableData

        else:
            zcross = zero_crossing(x, cfd)
            tr = rise_time(x,y)
            mpv = minimize_scalar(f).x

            patch = Patch()
            patch["data"][0]["y"] = cfd
            
            return patch, no_update, f"{zcross:.3f}", f"{tr:.3f}", f"{mpv:.3f}", no_update



#---------------------------------------------------------------------------------------------------
# Function to show/hide individual sliders
#---------------------------------------------------------------------------------------------------
@app.callback(
    Output("locSlider", "style"),
    Output("scaleSlider", "style"),
    Output("satSlider", "style"),
    Output("amplSlider", "style"),
    Output("delaySlider", "style"),
    Output("attSlider", "style"), 
    Output("nzSlider", "style"),
    Output("noise-toggle", "data"),
    Input("slider-toggle", "value"),
    
)
def toggling(selected):
    loc_style = {"display": "block"} if "loc" in selected else {"display": "none"}
    scale_style = {"display": "block"} if "scale" in selected else {"display": "none"}
    sat_style = {"display": "block"} if "sat" in selected else {"display": "none"}
    ampl_style = {"display": "block"} if "ampl" in selected else {"display": "none"}
    delay_style = {"display": "block"} if "delay" in selected else {"display": "none"}
    att_style = {"display": "block"} if "att" in selected else {"display": "none"}
    
    if "nz" in selected:
        nz_style = {"display": "block"}
        nzOn = 1
    else:
        nz_style = {"display": "none"}
        nzOn = 0



    return loc_style, scale_style, sat_style, ampl_style, delay_style, att_style, nz_style, nzOn

@app.callback(
    Output("visibility", "data"),
    Input("cfd-plot", "restyleData"),
    Input("add-trace", "n_clicks"),
    Input("clear", "n_clicks"),
    State("active-graph", "data"),
    State("cfd-plot", "figure"),
    State("visibility", "data"),
)
def store_visibility(restyleData, n_clicks, n_clicksC, activeGraph, current_fig, visibility):
    button_id = ctx.triggered_id

    vis = []
    for trace in current_fig["data"]:
        traceVis = trace.get("visible", True)
        vis.append(traceVis)

    if activeGraph == "graph2":
        if button_id == "add-trace":
            vis.append("True")
        if button_id == "clear":
            vis = ["True"]
        visibility[1] = vis
    else:
        visibility[0] = vis
        
    return visibility


if __name__ == "__main__":
    app.run(debug=True)