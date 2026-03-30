from dash import Input, Output, State, Patch, no_update, ctx
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go
from functions import signalCalcs, lin_interp_x, zero_crossing, rise_time

def register_callbacks(app, x):
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
        Output("show-graph", "children"),
        Input("show-graph", "n_clicks"),
        State("active-graph", "data"),
    )
    def switch_graph(graph1Clicks, activeGraph):
        if activeGraph == "graph2":
            return "graph1", "Mode: Signal Components"
        else:
            return "graph2", "Mode: CFD Output Trace"


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
        Input("arm", "value"),
        Input("active-graph", "data"),
        Input("noise-toggle", "data"),
        prevent_initial_call=True,
    )
    def update_graph1(loc, scale, sat, ampl, delay, att, sigma, arm, activeGraph, nzOn):
        if activeGraph == "graph2":
            return no_update, no_update, no_update, no_update
        
        else: 

            f, y, delsig, attsig, cfd = signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn)
                
            zcross = zero_crossing(x, y, cfd, arm)
            if zcross is None:
                    zcross = "None"
            else:
                zcross = f"{zcross:.3f}"

            tr = rise_time(x,y)
            mpv = minimize_scalar(f).x

            patch = Patch()
            patch["data"][0]["y"] = y
            patch["data"][1]["y"] = delsig
            patch["data"][2]["y"] = attsig
            patch["data"][3]["y"] = cfd
            patch["data"][4]["x"] = [zcross]
            patch["data"][5]["y"] = [arm,arm]

            return patch, zcross, f"{tr:.3f}", f"{mpv:.3f}"
        

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
        Input("arm", "value"),
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
    def updateGraph2(loc, scale, sat, ampl, delay, att, sigma, arm, activeGraph, n_clicks, n_clicksC, nzOn, fig2, zcross, tr, mpv, tableData,):
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
                zcross = zero_crossing(x, y, cfd, arm)
                if zcross is None:
                    zcross = "None"
                else:
                    zcross = f"{zcross:.3f}"

                tr = rise_time(x,y)
                mpv = minimize_scalar(f).x

                patch = Patch()
                patch["data"][0]["y"] = cfd
                return patch, no_update, zcross, f"{tr:.3f}", f"{mpv:.3f}", no_update



    #---------------------------------------------------------------------------------------------------
    # Function to show/hide individual sliders
    #---------------------------------------------------------------------------------------------------
    @app.callback(
        Output("noise-toggle", "data"),
        Input("slider-toggle", "value"),
        
    )
    def toggling(selected):
        if "nz" in selected:
            nzOn = 1
        else:
            nzOn = 0

        return nzOn

    #---------------------------------------------------------------------------------------------------
    # Function to maintain visibility of specific traces
    #---------------------------------------------------------------------------------------------------
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