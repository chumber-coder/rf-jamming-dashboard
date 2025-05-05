from dash import Output, Input, State
from core.sdr_control import scan_frequencies, update_baseline, compute_jamming_score
import plotly.graph_objs as go
import datetime
import traceback
import numpy as np

SCAN_FREQS = [30.0, 32.5, 35.0, 136.0, 138.5, 141.0, 225.0, 243.0, 260.0]

def register_waterfall_callbacks(app):
    @app.callback(
        Output('heatmap-buffer', 'data'),
        Input('interval-component', 'n_intervals'),
        State('heatmap-buffer', 'data'),
        prevent_initial_call=True
    )
    def update_graph_data(n, buffer):
        try:
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            scan_results = scan_frequencies(SCAN_FREQS)
            result_map = {r['freq']: r for r in scan_results if r['power'] is not None}

            row = []
            for freq in SCAN_FREQS:
                result = result_map.get(freq)
                if result:
                    power = result['power']
                    bandwidth = result['bandwidth']
                    update_baseline(freq, power)
                    score = compute_jamming_score(freq, power, bandwidth)
                    delta = round(power - (update_baseline(freq, power) or power), 2)
                    print(f"[SCORE DEBUG] Freq: {freq:.2f} MHz | Power: {power:.2f} dB | Δ: {delta:.2f} | BW: {bandwidth:.1f} Hz | Score: {score:.2f}")
                    print(f"[{timestamp}] {freq:.2f} MHz - Power: {power:.2f} dB | BW: {int(bandwidth)} Hz | Score: {score:.2f}")
                    row.append(power)
                else:
                    row.append(np.nan)

            buffer = buffer or {"x": [], "y": SCAN_FREQS.copy(), "z": []}
            if buffer['y'] != SCAN_FREQS:
                print("[WARNING] Frequency list mismatch. Resetting waterfall buffer.")
                buffer = {"x": [], "y": SCAN_FREQS.copy(), "z": []}

            buffer['x'].append(timestamp)
            buffer['z'].append(row)

            buffer['x'] = buffer['x'][-60:]
            buffer['z'] = buffer['z'][-60:]

            print(f"[DEBUG] Appended row. z shape: {len(buffer['z'])} rows × {len(row)} cols")

            return buffer

        except Exception:
            print("[Graph Data Callback ERROR]")
            traceback.print_exc()
            return buffer

    @app.callback(
        Output('waterfall-graph', 'figure'),
        Input('heatmap-buffer', 'data')
    )
    def render_waterfall(buffer):
        try:
            z = np.array(buffer.get('z', []), dtype='float32')
            x = buffer.get('x', [])
            y = buffer.get('y', [])

            if z.size == 0 or len(x) == 0 or len(y) == 0:
                return go.Figure()

            if z.shape[1] != len(y):
                print(f"[ERROR] z cols ({z.shape[1]}) != y length ({len(y)}). Skipping render.")
                return go.Figure()

            fig = go.Figure(data=go.Heatmap(
                z=z.T,
                x=x,
                y=y,
                colorscale='Viridis',
                zmin=-30,
                zmax=0,
                colorbar=dict(
                    title=dict(text="Power (dB)", font=dict(color="#c2f542")),
                    tickfont=dict(color="#c2f542")
                )
            ))

            fig.update_layout(
                title="Waterfall View: Power Over Time",
                plot_bgcolor="#1e1e1e",
                paper_bgcolor="#1e1e1e",
                font=dict(color="#e0e0e0"),
                xaxis=dict(
                    title="Time",
                    color="#c2f542",
                    showgrid=False,
                    zeroline=False
                ),
                yaxis=dict(
                    title="Frequency (MHz)",
                    type='category',
                    color="#c2f542",
                    showgrid=False,
                    zeroline=False
                ),
                margin=dict(l=50, r=20, t=40, b=40),
                height=500
            )

            return fig

        except Exception:
            print("[Render Callback ERROR]")
            traceback.print_exc()
            return go.Figure()
