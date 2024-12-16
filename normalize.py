import numpy as np

def normalize_signal(signal):
    """Normalize the signal using Min-Max Scaling."""
    return (signal - np.min(signal)) / (np.max(signal) - np.min(signal))

# Exportable function
def apply_normalization(signal, normalize=True):
    """
    Apply normalization to the signal.
    - normalize: Boolean, if True apply Min-Max Scaling.
    """
    if normalize:
        return normalize_signal(signal)
    return signal
