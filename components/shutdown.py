"""Shutdown button and modal components."""
from dash import html


def create_shutdown_button():
    return html.Button('⏻ Shutdown', id='shutdown-btn', n_clicks=0,
                       style={'position': 'fixed', 'top': '10px', 'right': '10px', 'padding': '8px 15px',
                              'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'borderRadius': '5px',
                              'cursor': 'pointer', 'zIndex': 100, 'fontSize': '14px'})


def create_shutdown_modal():
    return html.Div(id='shutdown-modal', style={'display': 'none'}, children=[
        html.Div(style={'position': 'fixed', 'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
                        'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': 2000}),
        html.Div(style={'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)',
                        'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '30px', 'textAlign': 'center',
                        'zIndex': 2001, 'boxShadow': '0 10px 40px rgba(0,0,0,0.3)'}, children=[
            html.H2("⚠️ Shutdown Server?", style={'color': '#dc3545', 'fontSize': '20px'}),
            html.P("This will stop the application.", style={'fontSize': '15px'}),
            html.P("Make sure your work is saved!", style={'fontWeight': 'bold', 'fontSize': '15px'}),
            html.Div(style={'marginTop': '20px', 'display': 'flex', 'justifyContent': 'center', 'gap': '15px'}, children=[
                html.Button('Cancel', id='shutdown-cancel-btn', n_clicks=0,
                            style={'padding': '12px 30px', 'backgroundColor': '#6c757d', 'color': 'white',
                                   'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '15px'}),
                html.Button('Shutdown', id='shutdown-confirm-btn', n_clicks=0,
                            style={'padding': '12px 30px', 'backgroundColor': '#dc3545', 'color': 'white',
                                   'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '15px'}),
            ])
        ])
    ])
