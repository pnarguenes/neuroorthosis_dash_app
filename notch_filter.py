import numpy as np
from scipy.signal import iirnotch, filtfilt


def notch_filter(signal, notch_freq, fs, quality_factor=30):
    """
    Apply a Notch filter to remove specific frequency noise.

    Parameters:
    - signal: Input EMG signal
    - notch_freq: Notch frequency (e.g., 50 Hz)
    - fs: Sampling frequency
    - quality_factor: Quality factor for the notch filter
    """
    nyquist = 0.5 * fs
    w0 = notch_freq / nyquist
    b, a = iirnotch(w0, quality_factor)
    return filtfilt(b, a, signal)


def apply_notch_filter(emg_data, notch_freq=50, fs=1000):
    """Apply notch filter to all EMG channels."""
    filtered_data = [notch_filter(channel, notch_freq, fs) for channel in emg_data]
    return np.array(filtered_data)


# Exportable function
def process_with_notch(emg_data, fs, notch_freq):
    return apply_notch_filter(emg_data, notch_freq, fs)
