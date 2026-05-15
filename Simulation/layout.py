from dash import html, dcc

def build_layout(fig1, fig2, figProb, nzOn, loc, scale, ampl, delay, att, sigma, sat, arm, table, amplStepSize):
    return html.Div([
        dcc.Store(id="active-graph", data="graph1"),
        dcc.Store(id="graph1-store", data=fig1),
        dcc.Store(id="graph2-store", data=fig2),
        dcc.Store(id="graphProb-store", data=figProb),
        dcc.Store(id="table-data", data=[]),
        dcc.Store(id="visibility", data=[[True, True, True, True, True, True],[True]]),
        dcc.Store(id="noise-toggle", data=nzOn),

        html.Div([
            html.Div([
                
                

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
                        html.H4("Peak:", className="display-label"),
                        html.Div(id="peak", className="display"),
                    ]), 
                ],
                className="display-container"
                ),
                
                dcc.Tabs(
                    id="tabs",
                    value="tab-1",
                    children=[
                        dcc.Tab(label="CFD Parameters", value="tab-1", children=[
                            html.Div([
                                html.Label("Amplitude"),
                                dcc.Slider(id="ampl", min=0.1, max=4.09, step=amplStepSize, value=ampl, updatemode="drag"),
                            ], id="amplSlider", className="slider-container"),

                            html.Div([
                                html.Label("Delay"),
                                dcc.Slider(id="delay", min=-3, max=3.5, step=0.05, value=delay, updatemode="drag"),
                            ], id="delaySlider", className="slider-container"),

                            html.Div([
                                html.Label("Attenuation"),
                                dcc.Slider(id="att", min=0, max=2, step=0.01, value=att, updatemode="drag"),
                            ], id="attSlider", className="slider-container"),
                        ]),

                        dcc.Tab(label="Noise & Saturation", value="tab-2", children=[
                            dcc.Checklist(
                                id="slider-toggle",
                                options=[
                                    {"label": "Noise", "value": "nz"}
                                ],
                                value=[],
                                className="checklist"
                            ),
                            
                            html.Div([
                                html.Label("Noise"),
                                dcc.Slider(id="nz", min=0, max=0.05, step=0.001, value=sigma, updatemode="drag"),
                            ], id="nzSlider", className="slider-container"),

                            html.Div([
                                html.Label("Saturation"),
                                dcc.Slider(id="sat", min=0.3, max=1.5, step=0.01, value=sat, updatemode="drag"),
                            ], id="satSlider", className="slider-container"),

                            html.Div([
                                html.Label("Arming Comparator Reference"),
                                dcc.Slider(id="arm", min=0, max=0.5, step=0.01, value=arm, updatemode="drag"),
                            ], id="armSlider", className="slider-container"),
                        ]),

                        dcc.Tab(label="Incoming Signal", value="tab-3", children=[
                            html.Div([
                                html.Label("Timing"),
                                dcc.Slider(id="loc", min=-2, max=5, step=0.05, value=loc, updatemode="drag"),
                            ], id="locSlider", className="slider-container"),

                            html.Div([
                                html.Label("Shape"),
                                dcc.Slider(id="scale", min=0.1, max=2, step=0.02, value=scale, updatemode="drag"),
                            ], id="scaleSlider", className="slider-container"),  
                        ]),
                    ],
                className="tab-container"
                ),

            ],
            className="left-column"
            )
        ]),


        html.Div([
            dcc.Graph(figure=figProb, id="prob-plot", className="graph-container"),

             html.Div([
                html.Button('Mode: Signal Components', id='show-graph', n_clicks=0, className="mode-button"), 

                html.Button("Add Trace", id="add-trace", n_clicks=0, className="trace-button"),

                html.Button("Clear", id="clear", n_clicks=0, className="trace-button"),
            ],
            className="trace-buttons-container"),

            dcc.Graph(
                id='sweep-table', figure=table, className="table"),

        ],
        className="right-column"
        )

    ],
    className="whole-container"
    )       