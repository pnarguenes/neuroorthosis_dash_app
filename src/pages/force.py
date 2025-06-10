import dash
from dash import dcc, html, Input, Output, State, callback
import base64
import io
import pandas as pd
import plotly.graph_objs as go
import os

from src.processing.smoothing import apply_smoothing
from src.processing.comparisonforce import generate_force_comparison_figure

dash.register_page(__name__, path="/force")

def get_base64_image(image_filename):
    image_path = os.path.join("assets", image_filename)
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded_image}"

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
        html.H1("Force Data Analysis", style={'textAlign': 'center', 'color': '#f2f3f5'}),

        html.Div(style={'display': 'flex'}, children=[

            # LEFT CONTROLS
            html.Div(
                style={
                    'width': '15%',
                    'padding': '20px',
                    'backgroundColor': '#ffffff',
                    'borderRadius': '10px'
                },
                children=[
                    html.Label("Upload Force Data (.xlsx)", style={'fontWeight': 'bold'}),
                    dcc.Upload(
                        id='upload-force-data',
                        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'marginBottom': '20px'
                        },
                        multiple=False
                    ),
                    html.Label("Select Signal to View:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        id='force-signal-checklist',
                        options=[
                            {'label': 'Actual Flexion', 'value': 'Actual Flexion(N)'},
                            {'label': 'Actual Extension', 'value': 'Actual Extension(N)'},
                            {'label': 'Input Value', 'value': 'Input Value'},
                            {'label': 'MCP (α)', 'value': 'MCP (α)'},
                            {'label': 'PIP (β)', 'value': 'PIP (β)'},
                            {'label': 'DIP (γ)', 'value': 'DIP (γ)'}
                        ],
                        value=['Actual Flexion(N)'],
                        style={'marginBottom': '20px'},
                        labelStyle={'display': 'block'}
                    ),
                    html.Label("Select Image to View:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        id="image-checklist",
                        options=[
                            {"label": "Flexion", "value": "flexion"},
                            {"label": "Extension", "value": "extension"}
                        ],
                        value=[],
                        labelStyle={"display": "block"},
                        style={"marginBottom": "20px"}
                    ),
                    html.Label("Smoothing Method:", style={'fontWeight': 'bold'}),
                    dcc.RadioItems(
                        id='force-smoothing-radio',
                        options=[
                            {'label': 'None', 'value': 'none'},
                            {'label': 'Gaussian', 'value': 'gaussian'}
                        ],
                        value='none',
                        labelStyle={'display': 'block'},
                        style={'marginBottom': '20px'}
                    ),
                    html.Label("Show Input Zones:", style={'fontWeight': 'bold'}),
                    dcc.RadioItems(
                        id='zone-highlight-radio',
                        options=[
                            {'label': 'None', 'value': 'none'},
                            {'label': 'Flexion/Extension Zones', 'value': 'zones'}
                        ],
                        value='none',
                        labelStyle={'display': 'block'},
                        style={'marginBottom': '20px'}
                    ),
                ]
            ),
            # SPACER
            html.Div(style={'width': '2%'}),
            # RIGHT GRAPHS

            html.Div(
                style={
                    'width': '78%',
                    'padding': '0',
                    'backgroundColor': '#001f3f',
                    'borderRadius': '10px',
                    'display': 'flex',
                    'flexDirection': 'column'

                },
                children=[
                dcc.Graph(id='force-graph-raw' ,style={'height': '350px'}),
                html.Div(id="selected-images-center", style={"display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "gap": "20px",
                                        "marginTop": "20px",
                                        "marginBottom": "20px"}),
                dcc.Graph(id='force-graph-smoothed',style={'height': '350px'}),
                dcc.Graph(id='force-graph-comparison',style={'height': '350px'}),
            ])
        ])
    ]
)

@callback(
    Output('force-graph-raw', 'figure'),
    Output('force-graph-smoothed', 'figure'),
    Output('force-graph-comparison', 'figure'),
    Input('upload-force-data', 'contents'),
    State('upload-force-data', 'filename'),
    Input('force-signal-checklist', 'value'),
    Input('force-smoothing-radio', 'value'),
    Input('zone-highlight-radio', 'value')
)

def update_force_graph(contents, filename, selected_signals, smoothing_method, zone_option):
    if contents is None or not selected_signals:
        return go.Figure(), go.Figure(), go.Figure()

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    time = df["Time (s)"]
    input_val_raw = df["Input Value"]
    rom_cols = ["MCP (α)", "PIP (β)", "DIP (γ)"]

    # === RAW FIGURE ===
    fig_raw = go.Figure()
    for sig in selected_signals:
        y = df[sig]
        if sig == 'Input Value':
            y = y * df["Actual Flexion(N)"].max()

        if sig in rom_cols:
            fig_raw.add_trace(go.Scatter(
                x=time, y=y, mode='lines', name=f"{sig}", yaxis='y2', line=dict(dash='dot', width=4)
            ))
        else:
            fig_raw.add_trace(go.Scatter(x=time, y=y, mode='lines', name=sig, line=dict(width=4)))

    fig_raw.update_layout(
        title="Raw Signal",
        xaxis=dict(title="Time (s)"),
        yaxis=dict(title="Force (N)"),
        yaxis2=dict(title="Angle (°)", overlaying="y", side="right"),

    )

    # === SMOOTHED FIGURE ===
    fig_smoothed = go.Figure()
    for sig in selected_signals:
        y = df[sig]
        if sig == 'Input Value':
            y = df["Input Value"]
        if smoothing_method != "none":
            y = apply_smoothing(y, method=smoothing_method)
            name = f"{sig} "
        else:
            name = sig

        if sig in rom_cols:
            fig_smoothed.add_trace(go.Scatter(x=time, y=y, mode='lines', name=name, yaxis='y2', line=dict(dash='dot', width=4)))
        else:
            fig_smoothed.add_trace(go.Scatter(x=time, y=y, mode='lines', name=name, line=dict(width=4)))

    fig_smoothed.update_layout(
        title=f"{smoothing_method.capitalize()} Smoothing Applied",
        xaxis=dict(title="Time (s)"),
        yaxis=dict(title="Force (N)"),
        yaxis2=dict(title="Angle (°)", overlaying="y", side="right"),

    )

    # === COMPARISON FIGURE ===
    fig_comparison = generate_force_comparison_figure(df)

    # === FLEXION / EXTENSION ZONES ===
    if zone_option == 'zones':
        # Binarize the Input Value signal for zone logic
        thresholded_input_val = (input_val_raw > 0.5).astype(int)
        current_val = thresholded_input_val.iloc[0]
        start_time = time.iloc[0]

        # Compute ymax for shaded region height
        force_cols = ['Actual Flexion(N)', 'Actual Extension(N)', 'Input Value']
        all_force_cols = [col for col in selected_signals if col in force_cols and col in df.columns]

        if all_force_cols:
            ymax = df[all_force_cols].max().max()
        else:
            ymax = 1  # fallback default

        for i in range(1, len(thresholded_input_val)):
            val = thresholded_input_val.iloc[i]
            if val != current_val:
                end_time = time.iloc[i]
                color = "#ffe6e6" if current_val == 1 else "#d6e0ff"
                fig_smoothed.add_shape(
                    type="rect",
                    x0=start_time,
                    x1=end_time,
                    y0=0,
                    y1=ymax,
                    xref="x",
                    yref="y",
                    fillcolor=color,
                    line=dict(width=0),
                    layer="below"
                )
                current_val = val
                start_time = end_time

        # Close the last zone
        end_time = time.iloc[-1]
        color = "#ffe6e6" if current_val == 1 else "#d6e0ff"
        fig_smoothed.add_shape(
            type="rect",
            x0=start_time,
            x1=end_time,
            y0=0,
            y1=ymax,
            xref="x",
            yref="y",
            fillcolor=color,
            line=dict(width=0),
            layer="below"
        )
        # for Flexion and Extension zones
        fig_smoothed.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='lines',
            line=dict(color="#ffe6e6", width=10),
            name='Flexion Zone'
        ))

        fig_smoothed.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='lines',
            line=dict(color="#d6e0ff", width=10),
            name='Extension Zone'
        ))

    return fig_raw, fig_smoothed, fig_comparison



@callback(
    Output("selected-images-center", "children"),
    Input("image-checklist", "value")
)
def display_selected_image(image_types):
    if not image_types:
        return None

    images = []
    for image_type in image_types:
        if image_type == "flexion":
            images.append(html.Div([
                html.Img(src=get_base64_image("flexion.png"), style={"height": "250px"}),
                html.P("Flexion", style={"color": "white", "textAlign": "center"})
            ], style={"marginRight": "800px"}))

        elif image_type == "extension":
            images.append(html.Div([
                html.Img(src=get_base64_image("extension.png"), style={"height": "250px"}),
                html.P("Extension", style={"color": "white", "textAlign": "center"})
            ], style={"marginRight": "180px"}))

    return html.Div(
        images,
        style={"display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "10px","marginBottom": "10px"}
    )



