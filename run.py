# run.py

from dash import Dash, html, dcc
from layouts.live_monitor_layout import get_live_monitor_layout
from callbacks.callbacks_monitor import register_monitor_callbacks

# Import your existing waterfall tab layout + callbacks
from layouts.waterfall_layout import get_waterfall_layout
from callbacks.callbacks_waterfall import register_waterfall_callbacks

app = Dash(__name__)
server = app.server  # For deployment with Flask

# Define the tab-based layout
app.layout = html.Div([
    html.H1("RF Dashboard", style={"textAlign": "center", "color": "#eee", "backgroundColor": "#222", "padding": "1rem"}),

    dcc.Tabs(id="tabs", value="live-monitor", children=[
        dcc.Tab(label="Live Monitor", value="live-monitor", children=get_live_monitor_layout()),
        dcc.Tab(label="Waterfall", value="waterfall", children=get_waterfall_layout()),
    ])
])

# Register callbacks for each tab
register_monitor_callbacks(app)
register_waterfall_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
