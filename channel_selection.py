def select_channel(emg_data, channel_index=0):
    """Select a specific channel from EMG data."""
    return emg_data[channel_index, :]

if __name__ == "__main__":
    from raw_data import load_data

    # File path to the .pkl file
    file_path = "data/myocontrol_data_2.pkl"

    # Load data
    data = load_data(file_path)
    emg_data = data['emg']

    # Select Channel 1
    selected_channel = select_channel(emg_data, channel_index=0)
    print("Selected Channel Shape:", selected_channel.shape)
