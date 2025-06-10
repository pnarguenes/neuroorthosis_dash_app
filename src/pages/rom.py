import base64
import io
import numpy as np
import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table
import plotly.graph_objs as go
from PIL import Image
import os
from urllib.request import urlopen

dash.register_page(__name__, path="/rom", name="ROM Analysis")

def get_assets_image_options():
    assets_dir = "assets"
    image_files = [f for f in os.listdir(assets_dir) if f.endswith(".png")]
    return [{"label": f, "value": f"/assets/{f}"} for f in image_files]

def angle(a, b, c):
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

def blank_fig():
    return go.Figure(go.Image(z=np.ones((250, 250, 3)))).update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )


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

        html.H1("Range of Motion Analysis", style={'textAlign': 'center', 'color': '#f2f3f5'}),

        html.Div([
            html.Div([
                html.H4("Flexion Image", style={"color": "white"}),
                dcc.Upload(
                    id="upload-flexion",
                    children=html.Div(['Drag and Drop or ', html.A('Select Flexion File')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed',
                        'borderRadius': '5px', 'textAlign': 'center', 'marginBottom': '10px',
                        'backgroundColor': '#ffffff', 'color': '#001f3f'
                    },
                    multiple=False
                ),
                dcc.Dropdown(
                    id='flexion-dropdown',
                    options=get_assets_image_options(),
                    placeholder="Select Flexion Image",
                    style={'marginBottom': '10px'}
                ),
                html.Button("Undo ", id="undo-flexion", n_clicks=0, style={"marginBottom": "5px"}),
                html.Button("Reset ", id="reset-flexion", n_clicks=0),
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"}),

            html.Div([
                html.H4("Extension Image", style={"color": "white"}),
                dcc.Upload(
                    id="upload-extension",
                    children=html.Div(['Drag and Drop or ', html.A('Select Extension File')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed',
                        'borderRadius': '5px', 'textAlign': 'center', 'marginBottom': '10px',
                        'backgroundColor': '#ffffff', 'color': '#001f3f'
                    },
                    multiple=False
                ),
                dcc.Dropdown(
                    id='extension-dropdown',
                    options=get_assets_image_options(),
                    placeholder="Select Extension Image",
                    style={'marginBottom': '10px'}
                ),
                html.Button("Undo ", id="undo-extension", n_clicks=0, style={"marginBottom": "5px"}),
                html.Button("Reset ", id="reset-extension", n_clicks=0),
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"})
        ], style={"marginBottom": "30px"}),

        html.Div([
            html.Div([
                html.H4("Flexion View", style={"color": "white"}),
                dcc.Graph(
                    id="flexion-graph",
                    figure=blank_fig(),
                    config={
                        "modeBarButtonsToRemove": [ "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"],
                        "modeBarButtonsToAdd": ["zoom2d", "toImage"],
                        "displaylogo": False,
                        "displayModeBar": True
                    },
                    style={"height": "400px"}
                ),
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.H4("Extension View", style={"color": "white"}),
                dcc.Graph(
                    id="extension-graph",
                    figure=blank_fig(),
                    config={
                        "modeBarButtonsToRemove": [ "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"],
                        "modeBarButtonsToAdd": ["zoom2d", "toImage"],
                        "displaylogo": False,
                        "displayModeBar": True
                    },
                    style={"height": "400px"}
                ),
            ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"})
        ]),

        html.Div(id="angle-table", style={"marginTop": "30px"})
    ]
)
# Global point storage
flexion_points = []
extension_points = []

def pil_image_to_fig(pil_img, points=None, angles=None, label_prefix=""):
    img_array = np.array(pil_img)
    fig = go.Figure(go.Image(z=img_array))

    if points:
        point_labels = ["Wrist", "MCP", "PIP", "DIP", "Tip"]
        for idx, pt in enumerate(points):
            fig.add_trace(go.Scatter(
                x=[pt[0]], y=[pt[1]],
                mode='markers',
                marker=dict(color='red', size=9),
                showlegend=False
            ))

        # Yellow joint lines
        for i in range(len(points) - 1):
            fig.add_trace(go.Scatter(
                x=[points[i][0], points[i+1][0]],
                y=[points[i][1], points[i+1][1]],
                mode="lines",
                line=dict(color="#ffcb00", width=2),
                showlegend=False
            ))

        # Green dashed extension lines
        for i in range(len(points) - 1):
            start = np.array(points[i])
            end = np.array(points[i+1])
            direction = end - start
            norm = np.linalg.norm(direction)
            if norm > 0:
                unit_vector = direction / norm
                extended = end + unit_vector * 80
                fig.add_trace(go.Scatter(
                    x=[end[0], extended[0]],
                    y=[end[1], extended[1]],
                    mode="lines",
                    line=dict(color="#00a86b", dash="dash", width=2),
                    showlegend=False
                ))
        for idx, pt in enumerate(points):
            fig.add_trace(go.Scatter(
                x=[pt[0]], y=[pt[1] + 10],
                mode='text',
                text=[point_labels[idx]],
                textposition="bottom center",
                textfont=dict(size=12, color="black"),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x = [pt[0] ], y = [pt[1] + 10],
                mode = 'text',
                text = [point_labels[idx]],
                textposition = "bottom center",
                textfont = dict(size=10, color="white"),
                showlegend = False
            ))

        # Vertical angle annotations on the left
        if angles:
            annotations = [
                dict(
                    x=0, y=1 - 0.1 * i, xref="paper", yref="paper",
                    text=f"{label}: {angle:.1f}°",
                    showarrow=False,
                    font=dict(size=14, color="white", family="Arial"),
                    align="left",
                    xanchor="left"
                )
                for i, (label, angle) in enumerate(zip(
                    ["MCP (α)", "PIP (β)", "DIP (γ)"], angles
                ))
            ]
            fig.update_layout(annotations=annotations)

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=350,
        paper_bgcolor='#001f3f',
        plot_bgcolor='#001f3f'
    )
    return fig

def calculate_angles(points):
    a1 = angle(np.array(points[0]), np.array(points[1]), np.array(points[2]))
    a2 = angle(np.array(points[1]), np.array(points[2]), np.array(points[3]))
    a3 = angle(np.array(points[2]), np.array(points[3]), np.array(points[4]))
    return a1, a2, a3

@dash.callback(
    Output("flexion-graph", "figure"),
    Input("upload-flexion", "contents"),
    Input("flexion-dropdown", "value"),
    prevent_initial_call=True
)
def update_flexion_image(uploaded_content, dropdown_path):
    flexion_points.clear()
    if uploaded_content:
        content_type, content_string = uploaded_content.split(',')
        decoded = base64.b64decode(content_string)
        pil_img = Image.open(io.BytesIO(decoded)).convert("RGB")
        return pil_image_to_fig(pil_img, points=[], angles=None)
    elif dropdown_path:
        local_path = "assets" + dropdown_path.replace("/assets", "")
        pil_img = Image.open(local_path).convert("RGB")
        return pil_image_to_fig(pil_img, points=[], angles=None)
    return dash.no_update

@dash.callback(
    Output("extension-graph", "figure"),
    Input("upload-extension", "contents"),
    Input("extension-dropdown", "value"),
    prevent_initial_call=True
)
def update_extension_image(uploaded_content, dropdown_path):
    extension_points.clear()
    if uploaded_content:
        content_type, content_string = uploaded_content.split(',')
        decoded = base64.b64decode(content_string)
        pil_img = Image.open(io.BytesIO(decoded)).convert("RGB")

        return pil_image_to_fig(pil_img)
    elif dropdown_path:
        local_path = "assets" + dropdown_path.replace("/assets", "")
        pil_img = Image.open(local_path).convert("RGB")

        return pil_image_to_fig(pil_img)
    return dash.no_update
@dash.callback(
    Output("flexion-graph", "figure", allow_duplicate=True),
    Input("flexion-graph", "clickData"),
    State("flexion-graph", "figure"),
    prevent_initial_call=True
)
def handle_flexion_click(clickData, fig):
    if clickData and len(flexion_points) < 5:
        x = clickData["points"][0]["x"]
        y = clickData["points"][0]["y"]
        flexion_points.append((x, y))

    img_array = np.array(fig["data"][0]["z"], dtype=np.uint8)
    pil_img = Image.fromarray(img_array)
    angles = calculate_angles(flexion_points) if len(flexion_points) == 5 else None
    return pil_image_to_fig(pil_img, flexion_points, angles)


@dash.callback(
    Output("extension-graph", "figure", allow_duplicate=True),
    Input("extension-graph", "clickData"),
    State("extension-graph", "figure"),
    prevent_initial_call=True
)
def handle_extension_click(clickData, fig):
    if clickData and len(extension_points) < 5:
        x, y = clickData["points"][0]["x"], clickData["points"][0]["y"]
        extension_points.append((x, y))

    img_array = np.array(fig["data"][0]["z"], dtype=np.uint8)
    pil_img = Image.fromarray(img_array)
    angles = calculate_angles(extension_points) if len(extension_points) == 5 else None
    return pil_image_to_fig(pil_img, extension_points, angles)
@dash.callback(
    Output("angle-table", "children"),
    Input("flexion-graph", "figure"),
    Input("extension-graph", "figure")
)
def update_table(flexion_fig, extension_fig):
    if len(flexion_points) == 5 and len(extension_points) == 5:
        flexion_angles = calculate_angles(flexion_points)
        extension_angles = calculate_angles(extension_points)
        roms = [e - f for e, f in zip(extension_angles, flexion_angles)]

        columns = ["Joint", "Flexion (°)", "Extension (°)", "ROM (°)"]
        rows = [
            ["MCP (α)", f"{flexion_angles[0]:.1f}", f"{extension_angles[0]:.1f}", f"{roms[0]:.1f}"],
            ["PIP (β)", f"{flexion_angles[1]:.1f}", f"{extension_angles[1]:.1f}", f"{roms[1]:.1f}"],
            ["DIP (γ)", f"{flexion_angles[2]:.1f}", f"{extension_angles[2]:.1f}", f"{roms[2]:.1f}"],
        ]

        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in columns],
            data=[dict(zip(columns, row)) for row in rows],
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': '#003366', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': '#ffffff', 'color': '#001f3f'}
        )
    return None

@dash.callback(
    Output("flexion-graph", "figure", allow_duplicate=True),
    Input("reset-flexion", "n_clicks"),
    prevent_initial_call=True
)
def reset_flexion(n):
    flexion_points.clear()
    return blank_fig()

@dash.callback(
    Output("extension-graph", "figure", allow_duplicate=True),
    Input("reset-extension", "n_clicks"),
    prevent_initial_call=True
)
def reset_extension(n):
    extension_points.clear()
    return blank_fig()

@dash.callback(
    Output("flexion-graph", "figure", allow_duplicate=True),
    Input("undo-flexion", "n_clicks"),
    State("flexion-graph", "figure"),
    prevent_initial_call=True
)
def undo_flexion(n, fig):
    if flexion_points:
        flexion_points.pop()
        img_array = np.array(fig["data"][0]["z"], dtype=np.uint8)
        pil_img = Image.fromarray(img_array)
        return pil_image_to_fig(pil_img, flexion_points)
    return dash.no_update

@dash.callback(
    Output("extension-graph", "figure", allow_duplicate=True),
    Input("undo-extension", "n_clicks"),
    State("extension-graph", "figure"),
    prevent_initial_call=True
)
def undo_extension(n, fig):
    if extension_points:
        extension_points.pop()
        img_array = np.array(fig["data"][0]["z"], dtype=np.uint8)
        pil_img = Image.fromarray(img_array)
        return pil_image_to_fig(pil_img, extension_points)
    return dash.no_update
