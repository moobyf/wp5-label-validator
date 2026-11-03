"""Validation page layout."""
from dash import html, dcc


def create_validation_page():
    return html.Div(id='validation-page', style={'display': 'none'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                        'padding': '10px 15px', 'backgroundColor': '#e9ecef', 'borderRadius': '8px', 'marginBottom': '15px'}, children=[
            html.Div(id='current-file-info', style={'fontSize': '14px', 'color': '#495057'}),
            html.Button('📂 Load Different File', id='load-different-btn', n_clicks=0,
                        style={'padding': '8px 15px', 'backgroundColor': '#6c757d', 'color': 'white',
                               'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'})
        ]),
        html.Div(id='main-content')
    ])


def create_validation_ui():
    return html.Div([
        # Top controls bar
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                        'padding': '10px 15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'marginBottom': '10px'}, children=[
            html.Div([
                html.Button('⏮️', id='first-btn', n_clicks=0, title='First', style={'marginRight': '3px', 'padding': '8px 12px', 'fontSize': '14px'}),
                html.Button('◀️', id='prev-btn', n_clicks=0, title='Previous', style={'marginRight': '3px', 'padding': '8px 12px', 'fontSize': '14px'}),
                html.Button('▶️', id='next-btn', n_clicks=0, title='Next', style={'marginRight': '3px', 'padding': '8px 12px', 'fontSize': '14px'}),
                html.Button('⏭️', id='last-btn', n_clicks=0, title='Last', style={'padding': '8px 12px', 'fontSize': '14px'}),
            ]),
            html.Div([
                html.Label("Go #", style={'marginRight': '5px', 'fontSize': '14px'}),
                dcc.Input(id='goto-input', type='number', min=1, style={'width': '60px', 'marginRight': '5px', 'padding': '5px', 'fontSize': '14px'}),
                html.Button('Go', id='goto-btn', n_clicks=0, style={'padding': '5px 10px', 'fontSize': '14px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div(id='progress', style={'fontWeight': 'bold', 'fontSize': '15px'}),
        ]),
        
        # Zoom and frame controls
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'padding': '8px 15px',
                        'backgroundColor': '#f0f0f0', 'borderRadius': '8px', 'marginBottom': '10px'}, children=[
            html.Label("🔍", style={'fontWeight': 'bold'}),
            html.Button('25%', id='zoom-25', n_clicks=0, style={'padding': '4px 10px', 'fontSize': '14px'}),
            html.Button('50%', id='zoom-50', n_clicks=0, style={'padding': '4px 10px', 'fontSize': '14px'}),
            html.Button('100%', id='zoom-100', n_clicks=0, style={'padding': '4px 10px', 'fontSize': '14px'}),
            html.Button('150%', id='zoom-150', n_clicks=0, style={'padding': '4px 10px', 'fontSize': '14px'}),
            html.Span(id='zoom-display', style={'marginLeft': '5px', 'color': '#666', 'fontSize': '14px'}),
            html.Div(style={'flex': '1'}),
            html.Button('🎬 View Full Frame', id='view-frame-btn', n_clicks=0,
                        style={'padding': '8px 15px', 'backgroundColor': '#6f42c1', 'color': 'white',
                               'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'})
        ]),
        
        # Filter controls - simplified (no model filter)
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'padding': '8px 15px',
                        'backgroundColor': '#fff3cd', 'borderRadius': '8px', 'marginBottom': '10px', 'flexWrap': 'wrap'}, children=[
            html.Div([
                html.Label("Status:", style={'fontWeight': 'bold', 'marginRight': '5px', 'fontSize': '14px'}),
                dcc.RadioItems(id='filter-mode', options=[
                    {'label': ' All', 'value': 'all'},
                    {'label': ' Pending', 'value': 'unvalidated'},
                    {'label': ' Done', 'value': 'validated'}
                ], value='all', inline=True, style={'display': 'flex', 'gap': '8px', 'fontSize': '14px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Span("|", style={'color': '#ccc'}),
            html.Div([
                html.Label("Species:", style={'fontWeight': 'bold', 'marginRight': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(id='species-filter', options=[{'label': 'All', 'value': 'all'}], value='all',
                             clearable=False, style={'width': '180px', 'fontSize': '14px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div(style={'flex': '1'}),
            html.Div([
                html.Label("🔎", style={'marginRight': '3px'}),
                dcc.Input(id='search-input', type='text', placeholder='filename...', style={'width': '120px', 'padding': '4px', 'fontSize': '14px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ]),
        
        # Thumbnail gallery (shown when species filter is active)
        html.Div(id='thumbnail-gallery-container', style={'display': 'none', 'marginBottom': '15px'}, children=[
            html.Div(style={'backgroundColor': '#e9ecef', 'borderRadius': '8px', 'padding': '10px'}, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '10px'}, children=[
                    html.Span(id='gallery-title', style={'fontWeight': 'bold', 'fontSize': '14px'}),
                    html.Div([
                        html.Button('◀️', id='gallery-prev', n_clicks=0, style={'padding': '4px 8px', 'fontSize': '12px', 'marginRight': '5px'}),
                        html.Span(id='gallery-page-info', style={'fontSize': '13px', 'marginRight': '5px'}),
                        html.Button('▶️', id='gallery-next', n_clicks=0, style={'padding': '4px 8px', 'fontSize': '12px'}),
                    ])
                ]),
                html.Div(id='thumbnail-gallery', style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px', 'maxHeight': '200px', 'overflowY': 'auto'})
            ])
        ]),
        
        # Two column layout
        html.Div(style={'display': 'flex', 'gap': '15px'}, children=[
            # Left - Image
            html.Div(style={'flex': '1', 'minWidth': '0'}, children=[
                html.Div(id='image-container', style={'border': '2px solid #dee2e6', 'borderRadius': '8px',
                                                       'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                       'minHeight': '300px', 'maxHeight': '500px', 'overflow': 'auto'})
            ]),
            # Right - Labels
            html.Div(style={'width': '350px', 'flexShrink': '0'}, children=[
                # Predictions
                html.Div(style={'backgroundColor': '#e9ecef', 'borderRadius': '8px', 'padding': '10px', 'marginBottom': '10px'}, children=[
                    html.Div(id='predictions-with-buttons', style={'fontSize': '14px'})
                ]),
                # Label selection
                html.Div(style={'backgroundColor': '#fff', 'border': '2px solid #007bff', 'borderRadius': '8px', 'padding': '12px'}, children=[
                    html.H4("🏷️ Select Label", style={'marginTop': '0', 'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Div(id='label-buttons', style={'maxHeight': '200px', 'overflowY': 'auto', 'marginBottom': '10px'}),
                    html.Div([
                        dcc.Input(id='new-label-input', type='text', placeholder='New label...',
                                  style={'flex': '1', 'padding': '6px', 'marginRight': '5px', 'fontSize': '14px'}),
                        html.Button('➕', id='add-label-btn', n_clicks=0, title='Add label',
                                    style={'padding': '6px 10px', 'backgroundColor': '#28a745', 'color': 'white',
                                           'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'}),
                    ], style={'display': 'flex', 'marginBottom': '5px'}),
                    html.Div([
                        dcc.Dropdown(id='delete-label-dropdown', placeholder='Select to delete...',
                                     style={'flex': '1', 'fontSize': '13px'}),
                        html.Button('🗑️', id='delete-label-btn', n_clicks=0, title='Delete label',
                                    style={'padding': '6px 10px', 'backgroundColor': '#dc3545', 'color': 'white',
                                           'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px', 'marginLeft': '5px'}),
                    ], style={'display': 'flex', 'marginBottom': '10px'}),
                    html.Div([
                        html.Strong("Selected: ", style={'fontSize': '14px'}),
                        html.Span(id='selected-display', children='None', style={'color': '#007bff', 'fontSize': '16px', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '10px', 'padding': '8px', 'backgroundColor': '#e7f3ff', 'borderRadius': '4px'}),
                    html.Button('💾 SAVE & NEXT', id='save-btn', n_clicks=0,
                                style={'width': '100%', 'padding': '15px', 'backgroundColor': '#28a745', 'color': 'white',
                                       'border': 'none', 'borderRadius': '5px', 'fontSize': '18px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
                    html.Div(id='save-status', style={'marginTop': '8px', 'textAlign': 'center', 'fontSize': '14px'})
                ])
            ])
        ]),
        # Store for gallery pagination
        dcc.Store(id='gallery-page', data=0),
    ])


def create_frame_viewer_modal():
    return html.Div(id='frame-modal', style={'display': 'none'}, children=[
        html.Div(style={'position': 'fixed', 'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
                        'backgroundColor': 'rgba(0,0,0,0.8)', 'zIndex': 1500}, id='frame-modal-backdrop'),
        html.Div(style={'position': 'fixed', 'top': '2%', 'left': '2%', 'right': '2%', 'bottom': '2%',
                        'backgroundColor': 'white', 'borderRadius': '10px', 'zIndex': 1501,
                        'display': 'flex', 'flexDirection': 'column', 'overflow': 'hidden'}, children=[
            # Header
            html.Div(style={'padding': '15px 20px', 'backgroundColor': '#6f42c1', 'color': 'white',
                           'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                html.H3("🎬 Full Frame View", style={'margin': 0, 'fontSize': '18px'}),
                html.Div([
                    html.Button('◀️', id='prev-frame-btn', n_clicks=0, title='Previous Frame',
                                style={'padding': '8px 15px', 'backgroundColor': '#5a32a3', 'color': 'white',
                                       'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px', 'marginRight': '5px'}),
                    html.Span(id='frame-info', style={'fontSize': '14px', 'margin': '0 10px'}),
                    html.Button('▶️', id='next-frame-btn', n_clicks=0, title='Next Frame',
                                style={'padding': '8px 15px', 'backgroundColor': '#5a32a3', 'color': 'white',
                                       'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px'}),
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Button('✕ Close', id='close-frame-modal', n_clicks=0,
                            style={'padding': '8px 20px', 'backgroundColor': '#dc3545', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontWeight': 'bold', 'fontSize': '14px'})
            ]),
            # Instructions
            html.Div(style={'padding': '10px 20px', 'backgroundColor': '#fff3cd', 'borderBottom': '1px solid #ffc107'}, children=[
                html.Span("📐 ", style={'fontSize': '16px'}),
                html.Strong("Draw: ", style={'fontSize': '14px'}),
                html.Span("Green=Current | Cyan=Others | Orange=New bbox", style={'fontSize': '14px'})
            ]),
            # Frame image
            html.Div(id='frame-image-container', style={'flex': '1', 'overflow': 'hidden', 'backgroundColor': '#1a1a1a', 'padding': '10px'}),
            # BBox controls
            html.Div(style={'padding': '15px 20px', 'backgroundColor': '#e9ecef', 'borderTop': '1px solid #dee2e6',
                           'display': 'flex', 'gap': '15px', 'alignItems': 'center', 'flexWrap': 'wrap'}, children=[
                html.Span("📐 Original:", style={'fontWeight': 'bold', 'color': '#28a745', 'fontSize': '14px'}),
                html.Span(id='original-bbox-display', style={'fontFamily': 'monospace', 'marginRight': '20px', 'fontSize': '14px'}),
                html.Span("📐 New:", style={'fontWeight': 'bold', 'color': '#fd7e14', 'fontSize': '14px'}),
                html.Span(id='new-bbox-display', style={'fontFamily': 'monospace', 'color': '#fd7e14', 'fontSize': '14px'}),
                html.Div(style={'flex': '1'}),
                html.Button('↩️ Reset', id='reset-bbox-btn', n_clicks=0,
                            style={'padding': '8px 20px', 'backgroundColor': '#6c757d', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'}),
                html.Button('💾 Update BBox', id='save-bbox-btn', n_clicks=0,
                            style={'padding': '8px 20px', 'backgroundColor': '#28a745', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'}),
                html.Button('➕ Add New Detection', id='add-detection-btn', n_clicks=0,
                            style={'padding': '8px 20px', 'backgroundColor': '#17a2b8', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'}),
            ]),
            # Manual input
            html.Details([
                html.Summary("✏️ Manual coordinate entry", style={'cursor': 'pointer', 'padding': '10px 20px', 'backgroundColor': '#f8f9fa', 'fontSize': '14px'}),
                html.Div(style={'padding': '15px 20px', 'backgroundColor': '#f8f9fa', 'display': 'flex', 'gap': '15px', 'alignItems': 'center', 'flexWrap': 'wrap'}, children=[
                    html.Label("x_min:", style={'fontSize': '14px'}), dcc.Input(id='edit-x-min', type='number', value=0, style={'width': '80px', 'padding': '5px', 'fontSize': '14px'}),
                    html.Label("y_min:", style={'fontSize': '14px'}), dcc.Input(id='edit-y-min', type='number', value=0, style={'width': '80px', 'padding': '5px', 'fontSize': '14px'}),
                    html.Label("x_max:", style={'fontSize': '14px'}), dcc.Input(id='edit-x-max', type='number', value=0, style={'width': '80px', 'padding': '5px', 'fontSize': '14px'}),
                    html.Label("y_max:", style={'fontSize': '14px'}), dcc.Input(id='edit-y-max', type='number', value=0, style={'width': '80px', 'padding': '5px', 'fontSize': '14px'}),
                    html.Button('🔄 Apply', id='apply-manual-bbox-btn', n_clicks=0,
                                style={'padding': '8px 20px', 'backgroundColor': '#17a2b8', 'color': 'white',
                                       'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'marginLeft': '15px', 'fontSize': '14px'}),
                ])
            ]),
            # Footer
            html.Div(style={'padding': '10px 20px', 'backgroundColor': '#f8f9fa', 'borderTop': '1px solid #dee2e6',
                           'display': 'flex', 'justifyContent': 'space-between'}, children=[
                html.Div(id='bbox-save-status', style={'color': '#666', 'fontSize': '14px'}),
                html.Span(id='frame-status', style={'color': '#666', 'fontSize': '14px'})
            ]),
            dcc.Store(id='current-video-path', data=''),
            dcc.Store(id='current-frame-num', data=0),
            dcc.Store(id='original-bbox-store', data={'x_min': 0, 'y_min': 0, 'x_max': 0, 'y_max': 0}),
            dcc.Store(id='frame-dimensions', data={'width': 1920, 'height': 1080}),
            dcc.Store(id='frame-navigating', data=False),
        ])
    ])
