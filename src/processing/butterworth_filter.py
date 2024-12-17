import numpy as np
from scipy.signal import butter, filtfilt


def butter_filter(signal, filter_type, cutoff, fs, order=4):
    """
    Apply a Butterworth filter to the signal.

    Parameters:
    - signal: Input EMG signal (numpy array)
    - filter_type: 'low', 'high', 'bandpass', etc.
    - cutoff: Cutoff frequency (single value for 'low'/'high', tuple for 'bandpass')
    - fs: Sampling frequency
    - order: Filter order (default=4)
    """
    nyquist = 0.5 * fs
    normal_cutoff = np.array(cutoff) / nyquist
    b, a = butter(order, normal_cutoff, btype=filter_type)
    return filtfilt(b, a, signal)


def apply_butterworth_filter(emg_data, filter_type, cutoff, fs=1000):
    """Apply Butterworth filter to all EMG channels."""
    filtered_data = [butter_filter(channel, filter_type, cutoff, fs) for channel in emg_data]
    return np.array(filtered_data)


# Exportable function
def process_with_butterworth(emg_data, fs, filter_type='bandpass', cutoff=(20, 450)):
    return apply_butterworth_filter(emg_data, filter_type, cutoff, fs)
