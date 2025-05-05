from dash import html, dcc

def get_live_monitor_layout():
    return html.Div([
        html.H3("Live RF Monitor"),
        
        html.Div([
            html.Label("Center Frequency (MHz):"),
            dcc.Input(id="input-center-freq", type="number", value=30.0, step=0.5),
            html.Label("Detection Threshold (dB):"),
            dcc.Input(id="input-threshold", type="number", value=-25.0, step=0.5),
        ], style={"display": "flex", "gap": "1rem", "margin-bottom": "1rem"}),

        dcc.Graph(id="power-graph"),

        dcc.Interval(id="monitor-interval", interval=5000, n_intervals=0),

        html.Div([
            html.H4("Event Log"),
            html.Div(id="event-log", style={"overflowY": "scroll", "height": "200px", "backgroundColor": "#111", "padding": "0.5rem", "color": "#eee", "border": "1px solid #333"}),
        ], style={"marginTop": "1rem"}),
    ])
