# EMG Data Analysis

This project provides a **Dash** interface for analyzing EMG data. The application supports filtering, normalization, and feature extraction of EMG signals.

## Project Structure

- **data/**: Directory containing EMG data files.
- **src/**: Source code for the project.
   - `app.py`: The main Dash application.
   - `processing/`: Signal processing modules (Butterworth filter, Notch filter, etc.).
- **requirements.txt**: List of required dependencies.
- **README.md**: Documentation for the project.
- **venv/**: Virtual environment (excluded from Git).

## Installation Steps

Clone the repository:
   ```bash
   git clone <repository-url>
   cd emg-data-analysis

   
Install the dependencies:
    pip install -r requirements.txt


Run the application:
    python src/app.py


---

## Usage

Once the application is running, use the Dash interface to:

1. **Select Data**: Choose different EMG data files.  
2. **Select Channel**: Choose different channels.  
3. **Apply Filters**: Use Butterworth and Notch filters to clean the signal.  
4. **Feature Extraction**: Extract features such as RMS, MAV, Zero Crossing, and more.  
5. **Visualize**: View raw signals, processed signals, and extracted features.  

---

## Contact

If you have any questions or suggestions, feel free to contact:  

- **Name**: Pinar Gunes  
- **Email**: pnar.guenes@fau.de  













