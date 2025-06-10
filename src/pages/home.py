import dash
from dash import html, dcc

dash.register_page(__name__, path="/")  # Home page

# 👉 Define style first
button_style = {
    "padding": "20px 40px",
    "fontSize": "20px",
    "borderRadius": "10px",
    "backgroundColor": "#0074D9",
    "color": "white",
    "border": "none",
    "cursor": "pointer"
}

# 👉 Then layout
layout = html.Div([
    html.H1("Hand Neuroorthosis Dashboard", style={"textAlign": "center", "color": "#f2f3f5", "marginBottom": "60px"}),

    html.Div([
        dcc.Link(html.Button("ROM ", style=button_style), href="/rom"),
        dcc.Link(html.Button("EMG Data ", style=button_style), href="/emg"),
        dcc.Link(html.Button("Force Data ", style=button_style), href="/force")

    ], style={"display": "flex", "justifyContent": "center", "gap": "2rem"})
], style={"backgroundColor": "#001f3f", "padding": "160px"})
