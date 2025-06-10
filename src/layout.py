from dash import html, dcc, page_container

def main_layout():
    return html.Div([
        html.H1("Neuroorthosis Dashboard", style={"textAlign": "center", "color": "#f2f3f5", "marginBottom": "40px"}),

        html.Div([
            dcc.Link(html.Button("ROM  ", style=button_style), href="/rom"),
            dcc.Link(html.Button("EMG Data ", style=button_style), href="/emg"),
            dcc.Link(html.Button("Force Data", style=button_style), href="/grasp-forces"),
            dcc.Link(html.Button("Assessments", style=button_style), href="/assessments"),
        ], style={"display": "flex", "justifyContent": "center", "gap": "2rem", "marginBottom": "50px"}),

        # 🧩 This is the container for routed pages
        page_container
    ], style={"backgroundColor": "#001f3f", "padding": "60px"})

# Shared button styling
button_style = {
    "padding": "20px 40px",
    "fontSize": "20px",
    "borderRadius": "10px",
    "backgroundColor": "#0074D9",
    "color": "white",
    "border": "none",
    "cursor": "pointer"
}
