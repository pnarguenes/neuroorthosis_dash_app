import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pickle
import numpy as np
import base64
import io

from src.processing.butterworth_filter import process_with_butterworth
from src.processing.notch_filter import process_with_notch
from src.processing.rectification import process_with_rectification
from src.processing.smoothing import apply_smoothing
from src.processing.normalize import apply_normalization
from src.processing.feature_extraction import sliding_window_features
from src.processing.threshold import get_threshold
from src.processing.grasp_detection import get_myocontrol_grasp
from scipy.interpolate import interp1d

# page routing
dash.register_page(__name__, path="/emg")

# Global cache for uploaded files
uploaded_data_cache = {}

# Layout for EMG Data Analysis Page
layout = html.Div(
    style={'backgroundColor': '#001f3f', 'padding': '20px'},
    children=[
        html.Div([
            dcc.Link(html.Button("🏠", style={
                "fontSize": "30px",
                "backgroundColor": "transparent",
                "color": "white",
                "padding": "8px 16px",
                "border": "2px solid white",
                "borderRadius": "10px",
                "cursor": "pointer",
                "marginBottom": "10px"
            }), href="/")
        ]),
        html.H1("EMG Data Analysis", style={'textAlign': 'center', 'color': '#f2f3f5'}),
        html.Div(
            style={'display': 'flex', 'justify-content': 'space-between'},
            children=[
                # Left Sidebar Controls
                html.Div(
                    style={'width': '15%', 'padding': '20px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'},
                    children=[
                        html.Label("Upload .pkl File:", style={'fontWeight': 'bold'}),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                            style={
                                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                'borderWidth': '1px', 'borderStyle': 'dashed',
                                'borderRadius': '5px', 'textAlign': 'center', 'marginBottom': '20px'
                            },
                            multiple=False
                        ),
                        html.Label("Select Data:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='data-dropdown',
                            options=[
                                {'label': 'Myocontrol Data 1', 'value': 'data/myocontrol_data_1.pkl'},
                                {'label': 'Myocontrol Data 2', 'value': 'data/myocontrol_data.pkl'},
                            ],
                            value='data/myocontrol_data_1.pkl',
                            style={'margin-bottom': '40px'}
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
                            value=[],
                            style={'margin-bottom': '40px'}
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
                            style={'margin-bottom': '40px'}
                        ),
                        html.Label("Apply Normalization:", style={'fontWeight': 'bold'}),
                        dcc.RadioItems(
                            id='normalize-radio',
                            options=[
                                {'label': 'Yes', 'value': 'yes'},
                                {'label': 'No', 'value': 'no'}
                            ],
                            value='no',
                            style={'margin-bottom': '40px'}
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
                                {'label': 'Mean Power (MYOP)', 'value': 'MYOP'},
                            ],
                            placeholder="Select Feature",
                            style={'margin-bottom': '10px'}
                        ),

                        html.Label("Overlay Options:", style={'fontWeight': 'bold'}),
                        dcc.Checklist(
                            id='overlay-checklist',
                            options=[
                                {'label': 'Threshold', 'value': 'threshold'},
                                {'label': 'Grasp Detection (from threshold)', 'value': 'grasp_threshold'},
                                {'label': 'Grasp Detection (from myocontrol)', 'value': 'grasp_myocontrol'}
                            ],
                            value=[],
                            style={'margin-bottom': '40px'}
                        ),
                        html.Label("Threshold Method:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='threshold-method-dropdown',
                            options=[
                                {'label': 'Fixed', 'value': 'fixed'},
                                {'label': 'Mean + 0.5*STD', 'value': 'mean_std'},
                                {'label': '85th Percentile', 'value': 'percentile'}
                            ],
                            value='fixed',
                            style={'margin-bottom': '20px'}
                        ),
                        html.Label("Myocontrol:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='myocontrol-column-dropdown',
                            options=[{'label': f'Column {i+1}', 'value': i} for i in range(9)],
                            value=1,
                            style={'margin-bottom': '40px'}
                        ),
                    ]
                ),
                # Right Side Plots
                html.Div(
                    style={'width': '80%', 'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'},
                    children=[
                        dcc.Graph(id='raw-signal-plot', style={'height': '350px'}),
                        dcc.Graph(id='processed-signal-plot', style={'height': '350px'}),
                        dcc.Graph(id='features-plot', style={'height': '350px'})
                    ]
                )
            ]
        )
    ]
)

# Upload file and update dropdown
@dash.callback(
    Output('data-dropdown', 'options'),
    Output('data-dropdown', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('data-dropdown', 'options')
)
def handle_file_upload(contents, filename, existing_options):
    if contents is None:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        buffer = io.BytesIO(decoded)
        data = pickle.load(buffer)
        uploaded_data_cache[filename] = data
        new_option = {'label': f'Uploaded: {filename}', 'value': filename}
        updated_options = existing_options + [new_option]
        return updated_options, filename
    except Exception as e:
        print("Failed to load file:", e)
        raise dash.exceptions.PreventUpdate

# Update channel options based on selected data
@dash.callback(
    Output('channel-dropdown', 'options'),
    Input('data-dropdown', 'value')
)
def update_channel_options(data_path):
    data = load_data(data_path)
    return [{'label': f'Channel {i + 1}', 'value': i} for i in range(data['emg'].shape[0])]

# Plot all graphs
@dash.callback(
    Output('raw-signal-plot', 'figure'),
    Output('processed-signal-plot', 'figure'),
    Output('features-plot', 'figure'),
    Input('data-dropdown', 'value'),
    Input('channel-dropdown', 'value'),
    Input('filters-checklist', 'value'),
    Input('smoothing-method', 'value'),
    Input('normalize-radio', 'value'),
    Input('feature-extraction-dropdown', 'value'),
    Input('overlay-checklist', 'value'),
    Input('myocontrol-column-dropdown', 'value'),
    Input('threshold-method-dropdown', 'value'),

)
def update_plots(data_path, channel_idx, filters, smoothing_method, normalize_option, feature_method, overlays, myocontrol_col, threshold_method):
    if data_path and channel_idx is not None:
        data = load_data(data_path)
        raw_signal = data['emg'][channel_idx]
        signal = raw_signal.copy()

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

        fs = 2000

        time_raw = np.arange(len(raw_signal)) / fs
        time_processed = np.arange(len(signal)) / fs


        # Raw EMG plot
        raw_fig = go.Figure()
        raw_fig.add_trace(go.Scatter(x=time_raw, y=raw_signal, mode='lines', name="Raw", line=dict(color='red')))
        raw_fig.update_layout(title="Raw EMG Signal", plot_bgcolor='#ffffff', paper_bgcolor='#001f3f', font={'color': 'white'}, xaxis={'title': 'Time (s)', 'gridcolor': '#003366', 'color': 'white'}, yaxis={'title': 'Amplitude', 'gridcolor': '#003366', 'color': 'white'})

        # Processed EMG plot
        processed_fig = go.Figure()
        processed_fig.add_trace(go.Scatter(x=time_processed, y=signal, mode='lines', name="Processed", line=dict(color='green')))
        processed_fig.update_layout(title="Processed EMG Signal", plot_bgcolor='#ffffff', paper_bgcolor='#001f3f', font={'color': 'white'}, xaxis={'title': 'Time (s)', 'gridcolor': '#003366', 'color': 'white'}, yaxis={'title': 'Amplitude', 'gridcolor': '#003366', 'color': 'white'})

        # Feature extraction
        feature_fig = go.Figure()
        if feature_method:
            feature_values = sliding_window_features(signal, frame=200, step=50, selected_features=[feature_method])
            y_vals = feature_values[feature_method]
            x_axis = np.arange(len(y_vals)) * (50 / fs)
            feature_fig.add_trace(go.Scatter(x=x_axis, y=y_vals, mode='lines', name=feature_method, line=dict(color='blue')))

            if 'threshold' in overlays:
                threshold_val = get_threshold(feature_method, y_vals, method=threshold_method)
                feature_fig.add_trace(go.Scatter(x=x_axis, y=[threshold_val]*len(x_axis), mode='lines', name='Threshold', line=dict(color='red', dash='dash')))

            if 'grasp_threshold' in overlays:
                threshold_val = get_threshold(feature_method, y_vals, method=threshold_method)
                grasp_mask = (np.array(y_vals) > threshold_val).astype(int)
                def enforce_min_duration(mask, fs, min_duration_sec=0.3):
                    min_samples = int(min_duration_sec * fs)
                    filtered = np.zeros_like(mask)
                    in_segment = False
                    start = 0
                    for i, val in enumerate(mask):
                        if val and not in_segment:
                            start = i
                            in_segment = True
                        elif not val and in_segment:
                            if i - start >= min_samples:
                                filtered[start:i] = 1
                            in_segment = False

                        # If ended with a grasp
                    if in_segment and len(mask) - start >= min_samples:
                        filtered[start:] = 1

                    return filtered

                    # Feature signal is sampled at fs_feature = fs / step
                fs_feature = fs / 50
                grasp_mask = enforce_min_duration(grasp_mask, fs=fs_feature)
                feature_fig.add_trace(go.Scatter(x=x_axis, y=grasp_mask, mode='lines', name='Grasp (threshold)', line=dict(color='yellow'), fill='tozeroy', opacity=0.2))

            if 'grasp_myocontrol' in overlays and 'myocontrol' in data and myocontrol_col is not None:
                grasp_mask = get_myocontrol_grasp(data['myocontrol'], myocontrol_col)
                if len(grasp_mask) != len(x_axis):

                    interp = interp1d(np.linspace(0, 1, len(grasp_mask)), grasp_mask, kind='nearest')
                    4
                    grasp_mask = interp(np.linspace(0, 1, len(x_axis)))
                feature_fig.add_trace(go.Scatter(x=x_axis, y=np.where(grasp_mask > 0.5, 1, 0), mode='lines', name='Grasp (myocontrol)', line=dict(color='#ffab91', dash='dot'), fill='tozeroy', opacity=0.3))

            feature_fig.update_layout(
                title=f"Feature: {feature_method}",
                plot_bgcolor='#ffffff',
                paper_bgcolor='#001f3f',
                font={'color': 'white'},
                xaxis={
                    'title': 'Time (s)',
                    'gridcolor': '#003366',
                    'color': 'white'
                },
                yaxis={
                    'title': 'Value',
                    'gridcolor': '#003366',
                    'color': 'white'
                },
                legend=dict(
                    x=0.01,
                    y=0.99,
                    bgcolor='rgba(255, 255, 255, 0.7)',
                    bordercolor='black',
                    borderwidth=1,
                    font=dict(
                        color='black',
                        size=12
                    ),
                    orientation="v"
                )
            )

        return raw_fig, processed_fig, feature_fig

    return go.Figure(), go.Figure(), go.Figure()

def load_data(file_path):
    if file_path in uploaded_data_cache:
        return uploaded_data_cache[file_path]
    with open(file_path, 'rb') as file:
        return pickle.load(file)
