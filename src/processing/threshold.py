import numpy as np

# Default fixed thresholds per feature
THRESHOLDS = {
    "RMS": 0.22,
    "MAV": 0.22,
    "VAR": 0.01,
    "LOG": -5,
    "Integral EMG": 50,
    "Wave Length": 3,
    "AAC": 0.01,
    "DASDV": 0.01,
    "Zero Crossing": 10,
    "WAMP": 10,
    "MYOP": 0.01
}


def get_threshold(feature_name, values=None, method="fixed"):
    """
    Compute threshold for the given feature and method.

    Parameters:
        feature_name (str): Name of the EMG feature.
        values (np.ndarray or list): Extracted feature values (required for dynamic methods).
        method (str): 'fixed', 'mean_std', or 'percentile'.

    Returns:
        float: Computed threshold value.
    """
    method = method.lower()

    if method == "fixed":
        return THRESHOLDS.get(feature_name, 0.1)

    if values is None or len(values) == 0:
        return 0.1  # fallback

    values = np.array(values)

    if method == "mean_std":
        return np.mean(values) + 0.5 * np.std(values)
    elif method == "percentile":
        return np.percentile(values, 85)

    # Fallback
    return THRESHOLDS.get(feature_name, 0.1)
