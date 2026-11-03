"""Session management callbacks."""
import os
import sys
from dash import html, Input, Output, State
import dash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils import save_session, clear_session


@app.callback(Output('start-btn', 'n_clicks'), Input('resume-session-btn', 'n_clicks'), prevent_initial_call=True)
def resume_session(n):
    return 1 if n else dash.no_update


@app.callback([Output('session-restore-banner', 'style'), Output('csv-path-input', 'value', allow_duplicate=True),
               Output('images-root-input', 'value', allow_duplicate=True), Output('output-path-input', 'value', allow_duplicate=True),
               Output('videos-root-input', 'value', allow_duplicate=True)],
              Input('clear-session-btn', 'n_clicks'), prevent_initial_call=True)
def clear_session_callback(n):
    if n:
        clear_session()
        return {'display': 'none'}, '', '', '', ''
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(Output('session-save-status', 'data'),
              [Input('current-index', 'data'), Input('df-store', 'data')],
              [State('csv-path-input', 'value'), State('images-root-input', 'value'),
               State('output-path-store', 'data'), State('videos-root-store', 'data')],
              prevent_initial_call=True)
def auto_save_session(index, df_json, csv_path, img_root, out_path, vid_root):
    if out_path and df_json:
        save_session({
            'csv_path': csv_path or '', 'images_root': img_root or '',
            'output_path': out_path, 'videos_root': vid_root or '', 'current_index': index or 0
        })
        return True
    return dash.no_update
