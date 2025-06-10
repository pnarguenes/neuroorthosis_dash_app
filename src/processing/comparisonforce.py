import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_force_comparison_figure(df):
    time = df["Time (s)"]

    # Flexion data
    target_flex = df["Target Flexion(N)"]
    actual_flex = df["Actual Flexion(N)"]

    # Extension data
    target_ext = df["Target Extension(N)"]
    actual_ext = df["Actual Extension(N)"]

    # Create subplot
    fig = make_subplots(rows=1, cols=2, shared_xaxes=True, subplot_titles=["Flexion Side", "Extension Side"])

    # --- Flexion Plot ---
    fig.add_trace(go.Scatter(
        x=time, y=actual_flex,
        mode='lines',
        name='Actual Flexion',
        line=dict(color='red')
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=time, y=target_flex,
        mode='lines',
        name='Target Flexion',
        line=dict(color='darkred', dash='dash')
    ), row=1, col=1)

    # Error fill between actual and target flexion
    fig.add_trace(go.Scatter(
        x=list(time) + list(time[::-1]),
        y=list(actual_flex) + list(target_flex[::-1]),
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Flexion Error Area',
        showlegend=True
    ), row=1, col=1)

    # --- Extension Plot ---
    fig.add_trace(go.Scatter(
        x=time, y=actual_ext,
        mode='lines',
        name='Actual Extension',
        line=dict(color='deepskyblue')
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=time, y=target_ext,
        mode='lines',
        name='Target Extension',
        line=dict(color='blue', dash='dash')
    ), row=1, col=2)

    # Error fill between actual and target extension
    fig.add_trace(go.Scatter(
        x=list(time) + list(time[::-1]),
        y=list(actual_ext) + list(target_ext[::-1]),
        fill='toself',
        fillcolor='rgba(135, 206, 250, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Extension Error Area',
        showlegend=True
    ), row=1, col=2)

    fig.update_layout(
        title="Force Comparison",
        height=400,
        margin=dict(t=40),
        legend=dict(x=1.05, y=1),
    )

    return fig
