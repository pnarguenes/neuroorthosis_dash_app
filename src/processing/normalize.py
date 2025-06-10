import numpy as np

def normalize_signal(signal):
    """Normalize the signal using Min-Max Scaling."""
    #return (signal - np.min(signal)) / (np.max(signal) - np.min(signal))

    """Normalize the signal using Max-Abs Scaling."""
    return (signal / np.max(np.abs(signal)))

def apply_normalization(signal, normalize=True):
    """
    Apply normalization to the signal.
    """
    if normalize:
        return normalize_signal(signal)
    return signal
