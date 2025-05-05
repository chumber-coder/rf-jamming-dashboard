from dash import dcc, html
import dash_bootstrap_components as dbc

# Match the same frequency list used in scan_frequencies()
SCAN_FREQS = [30.0, 32.5, 35.0, 136.0, 138.5, 141.0, 225.0, 243.0, 260.0]

def get_waterfall_layout():
    return dbc.Container([
        html.H2("RF Jamming Detection", className="text-center mt-4"),

        dcc.Tabs([
            dcc.Tab(label='Waterfall Monitor', children=[
                html.Div([
                    dcc.Graph(id='waterfall-graph'),
                    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
                    dcc.Store(id='heatmap-buffer', data={
                        "z": [],
                        "x": [],
                        "y": SCAN_FREQS
                    })
                ])
            ])
            # Future Tabs Go Here
            # dcc.Tab(label='Live Power Plot', children=[...]),
            # dcc.Tab(label='Event Table', children=[...]),
        ])
    ], fluid=True)
