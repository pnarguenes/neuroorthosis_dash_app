import numpy as np

def rectify_signal(emg_data):
    """Rectify the EMG signal (absolute value of each channel)."""
    rectified_data = [np.abs(channel) for channel in emg_data]
    return np.array(rectified_data)

# Exportable function
def process_with_rectification(emg_data):
    return rectify_signal(emg_data)
