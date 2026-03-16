import numpy as np
from scipy.stats import landau
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, Patch

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


# generate figure
fig = go.Figure()

fig.add_trace(go.Scatter(x=x, y=y, name="signal"))
fig.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
fig.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
fig.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))
fig.add_trace(go.Scatter(x=[zcross, zcross], y=[-3, 3], mode="lines", name="zero crossing", line=dict(dash="dash")))

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

# web app layout
app = Dash(__name__)

app.layout = html.Div([

    html.Div([
         
        html.Div([
            dcc.Graph(figure=fig, id="cfd-plot", 
                style={
                    "flex": "3",
                    "marginBottom": "0px"
                }
            ),
            
            html.Div([
                html.Div([
                    html.H4(
                        "MPV:",
                        style={"margin": "2px"}
                    ),

                    html.Div(id="mpv",
                        style={
                            "fontSize": "22px",
                            "padding": "8px 14px",
                            "border": "2px solid #448",
                            "borderRadius": "6px",
                            # "backgroundColor": "#111",
                            # "color": "#00c55f",
                            "display": "inline-block",
                            "minWidth": "140px",
                            "textAlign": "center",
                            "fontFamily": "monospace",
                            # "boxShadow": "inset 6px 5px 4px rgba(0,70,110,0.6)"
                        }
                    ),
                ]),

                html.Div([
                    html.H4(
                        "Rise Time:",
                        style={"margin": "2px"}
                    ),

                    html.Div(id="rise-time",
                        style={
                            "fontSize": "22px",
                            "padding": "8px 14px",
                            "border": "2px solid #448",
                            "borderRadius": "6px",
                            # "backgroundColor": "#111",
                            # "color": "#00c55f",
                            "display": "inline-block",
                            "minWidth": "140px",
                            "textAlign": "center",
                            "fontFamily": "monospace",
                            # "boxShadow": "inset 6px 5px 4px rgba(0,70,110,0.6)"
                        }
                    ),
                ]),

                html.Div([
                    html.H4(
                        "Zero Crossing:",
                        style={"margin": "2px"}
                    ),

                    html.Div(id="zero-crossing-value",
                        style={
                            "fontSize": "22px",
                            "padding": "8px 14px",
                            "border": "2px solid #448",
                            "borderRadius": "6px",
                            # "backgroundColor": "#111",
                            # "color": "#00c55f",
                            "display": "inline-block",
                            "minWidth": "140px",
                            "textAlign": "center",
                            "fontFamily": "monospace",
                            # "boxShadow": "inset 6px 5px 4px rgba(0,70,110,0.6)"
                        }
                    ),
                ]),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "gap": "40px",
            })
        ],
        style={
            # "position": "relative",
            "padding": "20px",
            "display": "flex",
            "flexDirection": "column",
            "gap": "5px",
        })
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
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "10px"
            }
        ),

        html.Div([
            html.Label("loc"),
            dcc.Slider(id="loc", min=-2, max=5, step=0.05, value=loc, updatemode="drag"),
        ], id="locSlider"),

        html.Div([
            html.Label("scale"),
            dcc.Slider(id="scale", min=0.1, max=2, step=0.02, value=scale, updatemode="drag"),
        ], id="scaleSlider"),

        html.Div([
            html.Label("Saturation"),
            dcc.Slider(id="sat", min=0.3, max=1, step=0.01, value=sat, updatemode="drag"),
        ], id="satSlider"),

        html.Div([
            html.Label("Amplitude"),
            dcc.Slider(id="ampl", min=0.1, max=3, step=0.02, value=ampl, updatemode="drag"),
        ], id="amplSlider"),

        html.Div([
            html.Label("Delay"),
            dcc.Slider(id="delay", min=0, max=3.5, step=0.05, value=delay, updatemode="drag"),
        ], id="delaySlider"),

        html.Div([
            html.Label("Attenuation"),
            dcc.Slider(id="att", min=0, max=1, step=0.01, value=att, updatemode="drag"),
        ], id="attSlider"),

    ],
    style={
        "flex": "1",
        "padding": "20px",
        "display": "flex",
        "flexDirection": "column",
        "gap": "15px"
    })

],
style={
    "display": "flex",
    "flexDirection": "row",
    # "backgroundColor": "#0f172a",
    # "color": "white",
    # "minHeight": "100vh",
})       


@app.callback(
    Output("cfd-plot", "figure"),
    Output("zero-crossing-value", "children"),
    Output("rise-time", "children"),
    Output("mpv", "children"),
    Output("locSlider", "style"),
    Output("scaleSlider", "style"),
    Output("satSlider", "style"),
    Output("amplSlider", "style"),
    Output("delaySlider", "style"),
    Output("attSlider", "style"),
    Input("loc", "value"),
    Input("scale", "value"),
    Input("sat", "value"),
    Input("ampl", "value"),
    Input("delay", "value"),
    Input("att", "value"),
    Input("slider-toggle", "value")
    
)

def update_plot(loc, scale, sat, ampl, delay, att,  selected):
    f = lambda x: -ampl * landau.pdf(x, loc=loc, scale=scale)
    y = -f(x)
    # y = ampl * landau.pdf(x, loc=loc, scale=scale)

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

    loc_style = {"display": "block"} if "loc" in selected else {"display": "none"}
    scale_style = {"display": "block"} if "scale" in selected else {"display": "none"}
    sat_style = {"display": "block"} if "sat" in selected else {"display": "none"}
    ampl_style = {"display": "block"} if "ampl" in selected else {"display": "none"}
    delay_style = {"display": "block"} if "delay" in selected else {"display": "none"}
    att_style = {"display": "block"} if "att" in selected else {"display": "none"}


    return patch, f"{zcross:.3f}", f"{tr:.3f}", f"{mpv:.3f}", loc_style, scale_style, sat_style, ampl_style, delay_style, att_style 

if __name__ == "__main__":
    app.run(debug=True)