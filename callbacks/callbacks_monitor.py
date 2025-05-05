import numpy as np
from dash import Input, Output, State, html
import plotly.graph_objs as go
from datetime import datetime
from rtlsdr import RtlSdr
import os

event_log = []

def calculate_score(power, threshold_db):
    mean_power = np.mean(power)
    std_power = np.std(power)
    score = (mean_power + 2 * std_power)
    triggered = score > threshold_db
    return score, triggered

def register_monitor_callbacks(app):
    @app.callback(
        Output("power-graph", "figure"),
        Output("event-log", "children"),
        Input("monitor-interval", "n_intervals"),
        State("input-center-freq", "value"),
        State("input-threshold", "value")
    )
    def update_power_plot(n, center_freq_mhz, threshold_db):
        sdr = RtlSdr()
        sdr.sample_rate = 2.4e6
        sdr.center_freq = center_freq_mhz * 1e6
        sdr.gain = 'auto'

        samples = sdr.read_samples(256*1024)
        sdr.close()

        power = 20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples))))
        freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/sdr.sample_rate)) + center_freq_mhz * 1e6
        freqs_mhz = freqs / 1e6

        score, triggered = calculate_score(power, threshold_db)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if triggered:
            event_msg = f"[{timestamp}] Detected event — Score: {score:.2f} dB"
            event_log.append(html.Div(event_msg))

            # Trigger IQ recording
            os.system(f"rtl_sdr -f {int(center_freq_mhz*1e6)} -s 2400000 -n 2560000 iq_record_{timestamp.replace(':', '-')}.bin")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=freqs_mhz, y=power, mode="lines", name="Power"))
        fig.update_layout(
            title=f"Power Spectrum - Centered at {center_freq_mhz:.2f} MHz",
            xaxis_title="Frequency (MHz)",
            yaxis_title="Power (dB)",
            template="plotly_dark",
            margin={"l": 40, "r": 20, "t": 40, "b": 40},
            height=400,
        )

        return fig, event_log[-10:]
