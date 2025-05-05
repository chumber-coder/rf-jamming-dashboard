import numpy as np
from rtlsdr import RtlSdr
import datetime
import os
from collections import defaultdict
import threading

# Threading lock to avoid concurrent SDR access
sdr_lock = threading.Lock()

# IQ capture settings
IQ_CAPTURE_DIR = os.path.expanduser("~/rf-dashboard/captures")
os.makedirs(IQ_CAPTURE_DIR, exist_ok=True)

def get_power(freq_mhz, sample_rate=2.4e6, num_samples=256*1024):
    if not sdr_lock.acquire(timeout=2):
        print("[WARNING] get_power: SDR in use, skipping.")
        return None

    sdr = None
    try:
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.center_freq = freq_mhz * 1e6
        sdr.gain = 'auto'
        samples = sdr.read_samples(num_samples)
        power_db = 10 * np.log10(np.mean(np.abs(samples)**2))
        return power_db
    except Exception as e:
        print(f"[get_power ERROR] {e}")
        return None
    finally:
        if sdr:
            sdr.close()
        sdr_lock.release()

def capture_iq(freq_mhz, sample_rate=2.4e6, num_samples=256*1024):
    if not sdr_lock.acquire(timeout=2):
        print("[WARNING] capture_iq: SDR in use, skipping.")
        return None

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"iq_{freq_mhz:.2f}MHz_{timestamp}.bin"
    filepath = os.path.join(IQ_CAPTURE_DIR, filename)

    sdr = None
    try:
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.center_freq = freq_mhz * 1e6
        sdr.gain = 'auto'
        samples = sdr.read_samples(num_samples)
        samples.astype('complex64').tofile(filepath)
        return filepath
    except Exception as e:
        print(f"[capture_iq ERROR] {e}")
        return None
    finally:
        if sdr:
            sdr.close()
        sdr_lock.release()

def scan_frequencies(freq_list, sample_rate=2.4e6, num_samples=256*1024):
    results = []
    if not sdr_lock.acquire(timeout=2):
        print("[WARNING] scan_frequencies: SDR in use, skipping.")
        return results

    sdr = None
    try:
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.gain = 'auto'

        for freq in freq_list:
            sdr.center_freq = freq * 1e6
            samples = sdr.read_samples(num_samples)

            power = 10 * np.log10(np.mean(np.abs(samples)**2))

            fft = np.fft.fftshift(np.fft.fft(samples))
            power_spectrum = 10 * np.log10(np.abs(fft)**2)
            freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), d=1/sample_rate))

            threshold = np.max(power_spectrum) - 20
            occupied = freqs[power_spectrum > threshold]
            bw_estimate = (occupied[-1] - occupied[0]) if len(occupied) > 0 else 0

            results.append({
                'freq': freq,
                'power': power,
                'bandwidth': bw_estimate,
            })

    except Exception as e:
        print(f"[scan_frequencies ERROR] {e}")
    finally:
        if sdr:
            sdr.close()
        sdr_lock.release()

    return results

# --- Baseline Noise Floor Tracker ---
baseline_power = defaultdict(lambda: (None, 0))

def update_baseline(freq, new_power, alpha=0.1):
    current_avg, count = baseline_power[freq]
    if current_avg is None:
        baseline_power[freq] = (new_power, 1)
    else:
        updated_avg = (1 - alpha) * current_avg + alpha * new_power
        baseline_power[freq] = (updated_avg, count + 1)

def get_baseline(freq):
    avg, _ = baseline_power[freq]
    return avg

# --- Updated Scoring Logic ---
def compute_jamming_score(freq, power, bandwidth, min_margin_db=3.0, bw_factor=0.25):
    """
    Computes a composite score [0.0–1.0] based on:
    - Power spike above baseline
    - Bandwidth expansion above typical FM width
    """

    baseline = get_baseline(freq)
    if baseline is None:
        return 0.0

    power_delta = power - baseline
    margin = max(min_margin_db, 0.1 * abs(baseline))  # Adaptive margin
    power_score = min(max(power_delta / margin, 0), 1)

    nominal_bw = 200e3  # Hz
    bw_score = min(max((bandwidth - nominal_bw) / (nominal_bw * bw_factor), 0), 1)

    score = round(0.7 * power_score + 0.3 * bw_score, 2)

    print(f"[SCORE DEBUG] Freq: {freq:.2f} MHz | Power: {power:.2f} dB | Δ: {power_delta:.2f} | BW: {bandwidth:.1f} Hz | Score: {score:.2f}")
    return score
