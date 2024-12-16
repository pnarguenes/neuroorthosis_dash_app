import pickle
import matplotlib.pyplot as plt

def load_data(file_path):
    """Load raw EMG data from a .pkl file."""
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data

def plot_raw_emg(emg_data, channel_index=0):
    """Plot raw EMG signal for the selected channel."""
    plt.figure(figsize=(15, 6))
    plt.plot(emg_data[channel_index, :], label=f"Channel {channel_index + 1}", color='blue')
    plt.title("Raw EMG Signal")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    # File path to the .pkl file
    file_path = "data/myocontrol_data_1.pkl"

    # Load data
    data = load_data(file_path)
    emg_data = data['emg']

    # Plot raw data for Channel 1
    plot_raw_emg(emg_data, channel_index=0)