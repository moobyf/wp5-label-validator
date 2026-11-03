"""File browser modal component."""
from dash import html, dcc


def create_file_browser_modal():
    return html.Div(id='browser-modal', style={'display': 'none'}, children=[
        html.Div(style={'position': 'fixed', 'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
                        'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': 1000}, id='browser-backdrop'),
        html.Div(style={'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)',
                        'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '20px', 'width': '600px',
                        'maxHeight': '80vh', 'overflow': 'hidden', 'zIndex': 1001, 'boxShadow': '0 10px 40px rgba(0,0,0,0.3)',
                        'display': 'flex', 'flexDirection': 'column'}, children=[
            html.H3(id='browser-title', style={'marginTop': 0, 'fontSize': '18px'}),
            html.Div(style={'marginBottom': '10px'}, children=[
                html.Strong("Path: ", style={'fontSize': '14px'}),
                html.Span(id='browser-path', style={'fontFamily': 'monospace', 'fontSize': '13px'})
            ]),
            html.Div(style={'marginBottom': '10px', 'display': 'flex', 'gap': '10px'}, children=[
                html.Button('⬆️ Up', id='browser-up-btn', n_clicks=0, style={'padding': '8px 15px', 'fontSize': '14px'}),
                html.Button('🏠 Home', id='browser-home-btn', n_clicks=0, style={'padding': '8px 15px', 'fontSize': '14px'}),
            ]),
            html.Div(id='browser-contents', style={'flex': '1', 'border': '1px solid #dee2e6', 'borderRadius': '5px',
                                                    'padding': '10px', 'overflowY': 'auto', 'maxHeight': '400px', 'minHeight': '200px'}),
            html.Div(style={'marginTop': '10px'}, children=[
                html.Strong("Selected: ", style={'fontSize': '14px'}),
                html.Span(id='browser-selection', style={'fontFamily': 'monospace', 'fontSize': '14px'})
            ]),
            html.Div(style={'marginTop': '15px', 'display': 'flex', 'justifyContent': 'flex-end', 'gap': '10px'}, children=[
                html.Button('Cancel', id='browser-cancel-btn', n_clicks=0,
                            style={'padding': '10px 20px', 'backgroundColor': '#6c757d', 'color': 'white',
                                   'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '14px'}),
                html.Button('Select', id='browser-select-btn', n_clicks=0,
                            style={'padding': '10px 20px', 'backgroundColor': '#28a745', 'color': 'white',
                                   'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '14px'}),
            ])
        ])
    ])


def create_browser_item(item):
    icons = {'folder': '📁', 'csv': '📄', 'video': '🎬'}
    colors = {'folder': '#fff3cd', 'csv': '#d4edda', 'video': '#e2d5f1'}
    return html.Div(
        children=[html.Span(icons.get(item['type'], '📄'), style={'marginRight': '10px'}), html.Span(item['name'])],
        style={'padding': '8px 12px', 'cursor': 'pointer', 'borderRadius': '4px', 'marginBottom': '4px',
               'backgroundColor': colors.get(item['type'], '#f8f9fa'), 'border': '1px solid transparent', 'fontSize': '14px'},
        id={'type': 'browser-item', 'path': item['path'], 'itemtype': item['type']}, className='browser-item'
    )
