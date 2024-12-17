import numpy as np
from scipy.signal import savgol_filter

def smooth_with_sg(signal, window_length=101, polyorder=2):
    """
    Smooth signal using Savitzky-Golay filter.
    - window_length: Odd integer specifying the smoothing window length.
    - polyorder: Order of the polynomial used in smoothing.
    """
    return savgol_filter(signal, window_length=window_length, polyorder=polyorder)

def smooth_with_mav(signal, window_size=100):
    """Smooth signal using Mean Absolute Value (MAV) with a sliding window."""
    return np.convolve(np.abs(signal), np.ones(window_size) / window_size, mode='same')

def smooth_with_rms(signal, window_size=100):
    """Smooth signal using Root Mean Square (RMS) with a sliding window."""
    squared_signal = np.power(signal, 2)
    rms_signal = np.sqrt(np.convolve(squared_signal, np.ones(window_size) / window_size, mode='same'))
    return rms_signal

# Exportable function
def apply_smoothing(signal, method, **kwargs):
    """
    Apply a smoothing method to the signal.
    - method: 'sg' (Savitzky-Golay), 'mav' (MAV), or 'rms'.
    - kwargs: Additional parameters like window_length, polyorder, window_size.
    """
    if method == 'sg':
        return smooth_with_sg(signal, window_length=kwargs.get('window_length', 101), polyorder=kwargs.get('polyorder', 2))
    elif method == 'mav':
        return smooth_with_mav(signal, window_size=kwargs.get('window_size', 100))
    elif method == 'rms':
        return smooth_with_rms(signal, window_size=kwargs.get('window_size', 100))
    return signal  # Default: return original signal

