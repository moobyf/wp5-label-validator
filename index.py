#!/usr/bin/env python3
"""Label Validator - Main entry point."""
import os
import sys

os.environ['DASH_DISABLE_JUPYTER'] = '1'

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from dash import html, dcc
from app import app
from config import HEARTBEAT_INTERVAL, load_labels_from_file
from layouts import create_config_page, create_validation_page, create_frame_viewer_modal
from components import create_file_browser_modal, create_shutdown_button, create_shutdown_modal

from callbacks import browser_callbacks, validation_callbacks, navigation_callbacks
from callbacks import save_callbacks, shutdown_callbacks, frame_callbacks, session_callbacks

# Load saved labels from file
saved_labels = load_labels_from_file()

app.layout = html.Div(style={'padding': '20px', 'maxWidth': '1600px', 'margin': '0 auto'}, children=[
    html.H1("🔍 Interactive Label Validator", style={'textAlign': 'center', 'color': '#2c3e50'}),
    dcc.Interval(id='heartbeat-interval', interval=HEARTBEAT_INTERVAL * 1000, n_intervals=0),
    html.Div(id='heartbeat-response', style={'display': 'none'}),
    dcc.Store(id='df-store'), dcc.Store(id='image-list-store', data=[]), dcc.Store(id='current-index', data=0),
    dcc.Store(id='root-dir-store', data=''), dcc.Store(id='output-path-store', data=''), dcc.Store(id='videos-root-store', data=''),
    dcc.Store(id='labels-store', data=saved_labels), dcc.Store(id='zoom-level', data=25),
    dcc.Store(id='selected-label', data=''), dcc.Store(id='validation-source', data=''),
    dcc.Store(id='image-refresh-trigger', data=0), dcc.Store(id='session-save-status', data=False),
    dcc.Store(id='browser-open', data=False), dcc.Store(id='browser-type', data=''),
    dcc.Store(id='browser-dir', data=os.path.expanduser('~')), dcc.Store(id='browser-selected', data=''),
    create_shutdown_button(), create_file_browser_modal(), create_shutdown_modal(), create_frame_viewer_modal(),
    create_config_page(), create_validation_page(),
])


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Label Validator')
    parser.add_argument('--port', type=int, default=8050)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔍 Interactive Label Validator")
    print(f"Server: http://{args.host}:{args.port}")
    print("=" * 60 + "\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
