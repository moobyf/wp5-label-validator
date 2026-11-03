"""Configuration page layout."""
import os
os.environ.setdefault('DASH_DISABLE_JUPYTER', '1')

from dash import html, dcc
from utils import load_session


def create_config_page():
    session = load_session()
    banner_style = {'display': 'none'}
    session_info = ""
    csv_val, img_val, out_val, vid_val = "", "", "", ""
    
    if session and session.get('output_path'):
        out_path = session.get('output_path', '')
        if os.path.exists(out_path):
            banner_style = {'display': 'block'}
            session_info = html.Div([
                html.P([html.Strong("Output: "), os.path.basename(out_path)], style={'fontSize': '15px'}),
                html.P([html.Strong("Position: "), f"Image #{session.get('current_index', 0) + 1}"], style={'fontSize': '15px'}),
            ])
            csv_val = session.get('csv_path', '')
            img_val = session.get('images_root', '')
            out_val = out_path
            vid_val = session.get('videos_root', '')
    
    return html.Div(id='config-page', children=[
        # Session restore banner
        html.Div(id='session-restore-banner', style=banner_style, children=[
            html.Div(style={'backgroundColor': '#d4edda', 'border': '1px solid #c3e6cb', 'borderRadius': '8px',
                           'padding': '15px', 'marginBottom': '20px'}, children=[
                html.H4("🔄 Previous session found!", style={'marginTop': '0', 'color': '#155724', 'fontSize': '18px'}),
                html.Div(id='session-info', children=session_info),
                html.Div(style={'display': 'flex', 'gap': '10px', 'marginTop': '10px'}, children=[
                    html.Button('✅ Resume Session', id='resume-session-btn', n_clicks=0,
                                style={'padding': '10px 20px', 'backgroundColor': '#28a745', 'color': 'white',
                                       'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontWeight': 'bold', 'fontSize': '15px'}),
                    html.Button('🗑️ Start Fresh', id='clear-session-btn', n_clicks=0,
                                style={'padding': '10px 20px', 'backgroundColor': '#dc3545', 'color': 'white',
                                       'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '15px'})
                ])
            ])
        ]),
        
        # CSV Path
        html.Div(style={'marginBottom': '20px'}, children=[
            html.Label("CSV File Path (with predictions):", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '8px', 'fontSize': '15px'}),
            html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
                dcc.Input(id='csv-path-input', type='text', value=csv_val, placeholder="Select CSV file...",
                          style={'flex': 1, 'padding': '10px', 'borderRadius': '4px', 'border': '1px solid #ccc', 'fontSize': '14px'}),
                html.Button('📂 Browse', id='open-csv-browser', n_clicks=0,
                            style={'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'})
            ])
        ]),
        
        # Images Path
        html.Div(style={'marginBottom': '20px'}, children=[
            html.Label("Images Root Directory:", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '8px', 'fontSize': '15px'}),
            html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
                dcc.Input(id='images-root-input', type='text', value=img_val, placeholder="Select images folder...",
                          style={'flex': 1, 'padding': '10px', 'borderRadius': '4px', 'border': '1px solid #ccc', 'fontSize': '14px'}),
                html.Button('📂 Browse', id='open-img-browser', n_clicks=0,
                            style={'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'})
            ]),
            html.P("💡 Base path for relative image paths in CSV", style={'fontSize': '14px', 'color': '#666', 'marginTop': '5px'})
        ]),
        
        # Output Path
        html.Div(style={'marginBottom': '20px'}, children=[
            html.Label("Output Directory (optional):", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '8px', 'fontSize': '15px'}),
            html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
                dcc.Input(id='output-path-input', type='text', value=out_val, placeholder="Select output folder...",
                          style={'flex': 1, 'padding': '10px', 'borderRadius': '4px', 'border': '1px solid #ccc', 'fontSize': '14px'}),
                html.Button('📂 Browse', id='open-out-browser', n_clicks=0,
                            style={'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'})
            ]),
            html.P("💡 Leave empty to save in images directory", style={'fontSize': '14px', 'color': '#666', 'marginTop': '5px'})
        ]),
        
        # Videos Path
        html.Div(style={'marginBottom': '20px'}, children=[
            html.Label("Videos Directory (optional - for viewing full frames):", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '8px', 'fontSize': '15px'}),
            html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
                dcc.Input(id='videos-root-input', type='text', value=vid_val, placeholder="Select videos folder...",
                          style={'flex': 1, 'padding': '10px', 'borderRadius': '4px', 'border': '1px solid #ccc', 'fontSize': '14px'}),
                html.Button('📂 Browse', id='open-vid-browser', n_clicks=0,
                            style={'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white',
                                   'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'})
            ])
        ]),
        
        html.Div(id='load-status', style={'marginBottom': '15px', 'fontSize': '15px'}),
        
        # Confidence threshold
        html.Div(style={'marginBottom': '20px'}, children=[
            html.Label("Confidence Threshold (optional):", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '8px', 'fontSize': '15px'}),
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '15px'}, children=[
                dcc.Input(id='confidence-threshold', type='number', min=0, max=1, step=0.05, 
                          placeholder='e.g. 0.5',
                          style={'width': '100px', 'padding': '10px', 'borderRadius': '4px', 'border': '1px solid #ccc', 'fontSize': '14px'}),
                html.Span("(0.0 - 1.0)", style={'color': '#666', 'fontSize': '14px'})
            ]),
            html.P("💡 Only show images where confidence is below this threshold", style={'fontSize': '14px', 'color': '#666', 'marginTop': '5px'})
        ]),
        
        # Start button
        html.Button('🚀 Start Validation', id='start-btn', n_clicks=0,
                    style={'width': '100%', 'padding': '15px', 'fontSize': '18px', 'backgroundColor': '#28a745',
                           'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'})
    ])
