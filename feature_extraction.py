import numpy as np
import pandas as pd
import math
import pywt


# Individual Feature Calculation Functions
def calculate_var(signal):
    """9.1 VAR: Calculate the variance of the signal."""
    return np.var(signal)


def calculate_rms(signal):
    """9.2 RMS: Calculate the root mean square of the signal."""
    return np.sqrt(np.mean(signal ** 2))


def calculate_integral_emg(signal):
    """9.3 Integral EMG: Calculate the integral of the signal."""
    return np.sum(np.abs(signal))


def calculate_mav(signal):
    """9.4 MAV: Calculate the mean absolute value of the signal."""
    return np.mean(np.abs(signal))


def calculate_log_energy(signal):
    """9.5 LOG: Calculate the logarithmic energy of the signal."""
    energy = np.sum(signal ** 2)
    return np.log(energy + 1e-10)  # Avoid log(0) issues


def calculate_wave_length(signal):
    """9.6 Wave Length: Calculate the wave length of the signal."""
    return np.sum(np.abs(np.diff(signal)))


def calculate_aac(signal):
    """9.7 AAC: Average Amplitude Change."""
    return np.mean(np.abs(np.diff(signal)))


def calculate_dasd(signal):
    """9.8 DASDV: Difference Absolute Standard Deviation Value."""
    return np.sqrt(np.mean(np.diff(signal) ** 2))


def calculate_zero_crossing(signal, threshold=0):
    """9.9 Zero Crossing: Count zero crossings."""
    zero_crosses = np.where(np.diff(np.sign(signal - threshold)))[0]
    return len(zero_crosses)


def calculate_wamp(signal, threshold=0.01):
    """9.10 WAMP: Count Willison Amplitude crossings above a threshold."""
    return np.sum(np.abs(np.diff(signal)) > threshold)


def calculate_myop(signal, threshold=0.01):
    """9.11 MYOP: Mean power of the signal."""
    return np.mean((np.abs(signal) > threshold).astype(int))


# Combine all features into one function
def extract_features(signal, selected_features):
    """
    Extract selected features from the signal.

    Parameters:
        signal (numpy.ndarray): Input EMG signal.
        selected_features (list): List of feature names to extract.

    Returns:
        dict: Dictionary of extracted feature names and values.
    """
    features = {}
    if "VAR" in selected_features:
        features["VAR"] = calculate_var(signal)
    if "RMS" in selected_features:
        features["RMS"] = calculate_rms(signal)
    if "Integral EMG" in selected_features:
        features["Integral EMG"] = calculate_integral_emg(signal)
    if "MAV" in selected_features:
        features["MAV"] = calculate_mav(signal)
    if "LOG" in selected_features:
        features["LOG"] = calculate_log_energy(signal)
    if "Wave Length" in selected_features:
        features["Wave Length"] = calculate_wave_length(signal)
    if "AAC" in selected_features:
        features["AAC"] = calculate_aac(signal)
    if "DASDV" in selected_features:
        features["DASDV"] = calculate_dasd(signal)
    if "Zero Crossing" in selected_features:
        features["Zero Crossing"] = calculate_zero_crossing(signal)
    if "WAMP" in selected_features:
        features["WAMP"] = calculate_wamp(signal)
    if "MYOP" in selected_features:
        features["MYOP"] = calculate_myop(signal)

    return features


# Sliding Window Feature Extraction for Signals
def sliding_window_features(signal, frame=200, step=50, selected_features=None):
    """
    Apply sliding window to compute features at each segment of the signal.

    Parameters:
        signal (numpy.ndarray): Input EMG signal.
        frame (int): Window size.
        step (int): Step size.
        selected_features (list): List of features to compute. Defaults to all features.

    Returns:
        pd.DataFrame: A DataFrame containing features over each window.
    """
    if selected_features is None:
        selected_features = ["VAR", "RMS", "Integral EMG", "MAV", "LOG", "Wave Length", "AAC", "DASDV",
                             "Zero Crossing", "WAMP", "MYOP"]

    # Check if the signal length is sufficient
    if len(signal) < frame:
        raise ValueError("Signal length is smaller than the window size.")

    windows = [signal[i:i + frame] for i in range(0, len(signal) - frame + 1, step)]
    feature_list = []

    for window in windows:
        feature_values = extract_features(window, selected_features)
        feature_list.append(feature_values)

    return pd.DataFrame(feature_list)


# Test function to print and verify feature extraction
if __name__ == "__main__":
    # Test signal
    signal = np.sin(2 * np.pi * 5 * np.linspace(0, 1, 1000)) + 0.5 * np.random.randn(1000)

    # Selected features
    selected_features = ["VAR", "RMS", "MAV", "LOG", "Zero Crossing", "Wave Length"]

    # Feature extraction over sliding window
    try:
        features_df = sliding_window_features(signal, frame=200, step=50, selected_features=selected_features)
        print("Extracted Features:")
        print(features_df)
    except ValueError as e:
        print(f"Error: {e}")
