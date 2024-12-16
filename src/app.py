import dash
from dash import dcc, html
import plotly.graph_objects as go
import pickle
import numpy as np

# Import processing modules
from butterworth_filter import process_with_butterworth
from notch_filter import process_with_notch
from rectification import process_with_rectification
from smoothing import apply_smoothing
from normalize import apply_normalization
from feature_extraction import sliding_window_features

# Helper function
def load_data(file_path):
    """Load data from a .pkl file."""
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data


# Dash App Initialization
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div(
    style={'backgroundColor': '#042b69', 'padding': '20px'},
    children=[
        html.H1("EMG Data Analysis ", style={'textAlign': 'center', 'color': '#f2f3f5'}),

        html.Div(
            style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'},
            children=[
                # Left-Side Controls
                html.Div(
                    style={'width': '25%', 'padding': '15px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'},
                    children=[
                        html.Label("Select Data:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='data-dropdown',
                            options=[
                                {'label': 'Myocontrol Data 1', 'value': "data/myocontrol_data_1.pkl"},
                                {'label': 'Myocontrol Data 2', 'value': "data/myocontrol_data_2.pkl"},
                                {'label': 'Myocontrol Data 3', 'value': "data/myocontrol_data_3.pkl"}
                            ],
                            value="data/myocontrol_data_1.pkl",
                            style={'margin-bottom': '10px'}
                        ),
                        html.Label("Select Channel:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(id='channel-dropdown', options=[], style={'margin-bottom': '10px'}),

                        html.Label("Apply Filters:", style={'fontWeight': 'bold'}),
                        dcc.Checklist(
                            id='filters-checklist',
                            options=[
                                {'label': 'Butterworth Filter', 'value': 'butterworth'},
                                {'label': 'Notch Filter (50Hz)', 'value': 'notch'},
                                {'label': 'Rectification', 'value': 'rectify'}
                            ],
                            value=[]
                        ),
                        html.Label("Smoothing Options:", style={'fontWeight': 'bold'}),
                        dcc.RadioItems(
                            id='smoothing-method',
                            options=[
                                {'label': 'No Smoothing', 'value': 'none'},
                                {'label': 'Savitzky-Golay', 'value': 'sg'},
                                {'label': 'MAV', 'value': 'mav'},
                                {'label': 'RMS', 'value': 'rms'}
                            ],
                            value='none',
                            style={'margin-bottom': '10px'}
                        ),
                        html.Label("Apply Normalization:", style={'fontWeight': 'bold'}),
                        dcc.RadioItems(
                            id='normalize-radio',
                            options=[
                                {'label': 'Yes', 'value': 'yes'},
                                {'label': 'No', 'value': 'no'}
                            ],
                            value='no'
                        ),
                        html.Label("Feature Extraction:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='feature-extraction-dropdown',
                            options=[
                                {'label': 'Variance (VAR)', 'value': 'VAR'},
                                {'label': 'Root Mean Square (RMS)', 'value': 'RMS'},
                                {'label': 'Integral EMG', 'value': 'Integral EMG'},
                                {'label': 'Mean Absolute Value (MAV)', 'value': 'MAV'},
                                {'label': 'Logarithmic Energy (LOG)', 'value': 'LOG'},
                                {'label': 'Wave Length', 'value': 'Wave Length'},
                                {'label': 'Average Amplitude Change (AAC)', 'value': 'AAC'},
                                {'label': 'Difference Absolute Standard Deviation (DASDV)', 'value': 'DASDV'},
                                {'label': 'Zero Crossing', 'value': 'Zero Crossing'},
                                {'label': 'Willison Amplitude (WAMP)', 'value': 'WAMP'},
                                {'label': 'Mean Power (MYOP)', 'value': 'MYOP'}
                            ],
                            placeholder="Select Feature",
                            style={'margin-bottom': '10px'}
                        )

                    ]
                ),
                # Right-Side Plots
                html.Div(
                    style={'width': '70%', 'padding': '15px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'},
                    children=[
                        dcc.Graph(id='raw-signal-plot', style={'height': '300px'}),
                        dcc.Graph(id='processed-signal-plot', style={'height': '300px'}),
                        dcc.Graph(id='features-plot', style={'height': '300px'})
                    ]
                )
            ]
        )
    ]
)

# Callbacks
@app.callback(
    dash.dependencies.Output('channel-dropdown', 'options'),
    [dash.dependencies.Input('data-dropdown', 'value')]
)
def update_channel_options(data_path):
    data = load_data(data_path)
    return [{'label': f'Channel {i + 1}', 'value': i} for i in range(data['emg'].shape[0])]


@app.callback(
    [
        dash.dependencies.Output('raw-signal-plot', 'figure'),
        dash.dependencies.Output('processed-signal-plot', 'figure'),
        dash.dependencies.Output('features-plot', 'figure'),
    ],
    [
        dash.dependencies.Input('data-dropdown', 'value'),
        dash.dependencies.Input('channel-dropdown', 'value'),
        dash.dependencies.Input('filters-checklist', 'value'),
        dash.dependencies.Input('smoothing-method', 'value'),
        dash.dependencies.Input('normalize-radio', 'value'),
        dash.dependencies.Input('feature-extraction-dropdown', 'value')
    ]
)
def update_plots(data_path, channel_idx, filters, smoothing_method, normalize_option, feature_method):
    if data_path and channel_idx is not None:
        # Load Data
        data = load_data(data_path)
        raw_signal = data['emg'][channel_idx]
        signal = raw_signal.copy()

        # Process Signal
        if 'butterworth' in filters:
            signal = process_with_butterworth([signal], 1000, 'low', 450)[0]
        if 'notch' in filters:
            signal = process_with_notch([signal], 1000, 50)[0]
        if 'rectify' in filters:
            signal = process_with_rectification([signal])[0]

        if smoothing_method != 'none':
            signal = apply_smoothing(signal, method=smoothing_method)

        if normalize_option == 'yes':
            signal = apply_normalization(signal)

        # Raw Signal Plot
        raw_fig = go.Figure()
        raw_fig.add_trace(go.Scatter(y=raw_signal, mode='lines', name="Raw Signal"))
        raw_fig.update_layout(title="Raw EMG Signal", xaxis_title="Samples", yaxis_title="Amplitude")

        # Processed Signal Plot
        processed_fig = go.Figure()
        processed_fig.add_trace(go.Scatter(y=signal, mode='lines', name="Processed Signal"))
        processed_fig.update_layout(title="Processed EMG Signal", xaxis_title="Samples", yaxis_title="Amplitude")

        # Feature Plot
        feature_fig = go.Figure()
        if feature_method:
            feature_values = sliding_window_features(signal, frame=200, step=50, selected_features=[feature_method])
            x_axis = np.arange(0, len(feature_values) * 50, 50)
            feature_fig.add_trace(go.Scatter(x=x_axis, y=feature_values[feature_method], mode='lines', name=feature_method))
            feature_fig.update_layout(title=f"Feature: {feature_method}", xaxis_title="Window Index", yaxis_title="Value")

        return raw_fig, processed_fig, feature_fig

    return go.Figure(), go.Figure(), go.Figure()


# Run App
if __name__ == '__main__':
    app.run_server(debug=True)
