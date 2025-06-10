import dash
from dash import html, dcc, page_container
import dash_bootstrap_components as dbc

# ✅ Add suppress_callback_exceptions=True
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

server = app.server

app.layout = html.Div([
    page_container
], style={"backgroundColor": "#001f3f", "padding": "60px"})

if __name__ == "__main__":
    app.run_server(debug=True)
