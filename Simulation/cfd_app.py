import numpy as np
from scipy.stats import landau
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, Patch

x = np.linspace(-5, 20, 1000)

loc = 0
scale = 0.5
ampl = 1

y = ampl * landau.pdf(x, loc=loc, scale=scale)

delay = 1
att = 0.2

delsig = np.interp(x-delay, x, y, left=0, right=0)
attsig = -att * y
cfd = delsig + attsig


def zero_crossing(x, y):

    # indices where sign changes
    sign_change = np.where(np.diff(np.sign(y)))[0]

    if len(sign_change) == 0:
        return None  # no zero crossing
    elif len(sign_change) == 2:
        i = sign_change[1]
    else:
        i = sign_change[0] 

    

    # points around crossing
    x1, x2 = x[i], x[i+1]
    y1, y2 = y[i], y[i+1]

    # linear interpolation
    x_zero = x1 - y1*(x2-x1)/(y2-y1)

    return x_zero

zcross = zero_crossing(x, cfd)
print(zcross)


fig = go.Figure()

fig.add_trace(go.Scatter(x=x, y=y, name="signal"))
fig.add_trace(go.Scatter(x=x, y=delsig, name="delayed"))
fig.add_trace(go.Scatter(x=x, y=attsig, name="attenuated"))
fig.add_trace(go.Scatter(x=x, y=cfd, name="CFD"))
fig.add_trace(go.Scatter(x=[zcross, zcross], y=[-100, 100], mode="lines", name="zero crossing", line=dict(dash="dash")))

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

    html.Div([
        dcc.Graph(figure=fig, id="cfd-plot", style={"flex": "3"}),

        html.Div([
            html.H4(
                "Zero Crossing Time:",
                style={"marginBottom": "2px"}
            ),

            html.Div(id="zero-crossing-value",
                style={
                    "fontSize": "20px",
                    "marginTop": "0px",
                    "marginBottom": "0px"
                }
            ),
        
            dcc.Checklist(
                id="slider-toggle",
                options=[
                    {"label": "Location", "value": "loc"},
                    {"label": "Scale", "value": "scale"},
                    {"label": "Amplitude", "value": "ampl"},
                    {"label": "Delay", "value": "delay"},
                    {"label": "Attenuation", "value": "att"},
                ],
                value=["ampl", "delay", "att"],
                # style={
                #     "position": "absolute",
                #     "bottom": "200px",
                #     "right": "270px",
                #     "background": "white",
                #     "padding": "5px"
                # }
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "10px"
                }
            ),

            html.Div([
                html.Label("loc"),
                dcc.Slider(id="loc", min=-2, max=5, step=0.1, value=0, updatemode="drag"),
            ], id="locSlider"),

            html.Div([
                html.Label("scale"),
                dcc.Slider(id="scale", min=0, max=2, step=0.1, value=0.5, updatemode="drag"),
            ], id="scaleSlider"),

            html.Div([
                html.Label("Amplitude"),
                dcc.Slider(id="ampl", min=0.1, max=10, step=0.1, value=1, updatemode="drag"),
            ], id="amplSlider"),

            html.Div([
                html.Label("Delay"),
                dcc.Slider(id="delay", min=0, max=5, step=0.1, value=1, updatemode="drag"),
            ], id="delaySlider"),

            html.Div([
                html.Label("Attenuation"),
                dcc.Slider(id="att", min=0, max=1, step=0.05, value=0.2, updatemode="drag")
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
    style={"display": "flex",
           "flexDirection": "row"
    })
        
])


@app.callback(
    Output("cfd-plot", "figure"),
    Output("zero-crossing-value", "children"),
    Output("locSlider", "style"),
    Output("scaleSlider", "style"),
    Output("amplSlider", "style"),
    Output("delaySlider", "style"),
    Output("attSlider", "style"),
    Input("loc", "value"),
    Input("scale", "value"),
    Input("ampl", "value"),
    Input("delay", "value"),
    Input("att", "value"),
    Input("slider-toggle", "value")
    
)

def update_plot(loc, scale, ampl, delay, att, selected):

    y = ampl * landau.pdf(x, loc=loc, scale=scale)

    delsig = np.interp(x-delay, x, y, left=0, right=0)
    attsig = -att * y
    cfd = delsig + attsig

    zcross = zero_crossing(x, cfd)

    patch = Patch()
    patch["data"][0]["y"] = y
    patch["data"][1]["y"] = delsig
    patch["data"][2]["y"] = attsig
    patch["data"][3]["y"] = cfd
    patch["data"][4]["x"] = [zcross,zcross]

    loc_style = {"display": "block"} if "loc" in selected else {"display": "none"}
    scale_style = {"display": "block"} if "scale" in selected else {"display": "none"}
    ampl_style = {"display": "block"} if "ampl" in selected else {"display": "none"}
    delay_style = {"display": "block"} if "delay" in selected else {"display": "none"}
    att_style = {"display": "block"} if "att" in selected else {"display": "none"}

    return patch, f"{zcross:.3f}", loc_style, scale_style, ampl_style, delay_style, att_style

# def toggle_sliders(selected):
    
#     loc_style = {"display": "block"} if "loc" in selected else {"display": "none"}
#     scale_style = {"display": "block"} if "scale" in selected else {"display": "none"}
#     ampl_style = {"display": "block"} if "ampl" in selected else {"display": "none"}
#     delay_style = {"display": "block"} if "delay" in selected else {"display": "none"}
#     att_style = {"display": "block"} if "att" in selected else {"display": "none"}

#     return loc_style, scale_style, ampl_style, delay_style, att_style

if __name__ == "__main__":
    app.run(debug=True)