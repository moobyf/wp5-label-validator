"""File browser callbacks."""
import os
import sys
from dash import html, ctx, Input, Output, State, ALL
import dash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils import get_directory_contents, get_parent_directory
from components.file_browser import create_browser_item


@app.callback(
    [Output('browser-modal', 'style'), Output('browser-type', 'data'), Output('browser-dir', 'data'),
     Output('browser-title', 'children'), Output('browser-selected', 'data'), Output('browser-selection', 'children')],
    [Input('open-csv-browser', 'n_clicks'), Input('open-img-browser', 'n_clicks'),
     Input('open-out-browser', 'n_clicks'), Input('open-vid-browser', 'n_clicks')],
    prevent_initial_call=True
)
def open_browser(csv_clicks, img_clicks, out_clicks, vid_clicks):
    trigger = ctx.triggered_id
    home = os.path.expanduser('~')
    types = {
        'open-csv-browser': ('csv', 'Select CSV File', 'No file selected'),
        'open-img-browser': ('img', 'Select Images Directory', home),
        'open-out-browser': ('out', 'Select Output Directory', home),
        'open-vid-browser': ('vid', 'Select Videos Directory', home)
    }
    btype, title, sel = types.get(trigger, ('', '', ''))
    return {'display': 'block'}, btype, home, title, '', sel


@app.callback(Output('browser-modal', 'style', allow_duplicate=True),
              [Input('browser-cancel-btn', 'n_clicks'), Input('browser-backdrop', 'n_clicks')], prevent_initial_call=True)
def close_browser(cancel, backdrop):
    return {'display': 'none'} if cancel or backdrop else dash.no_update


@app.callback([Output('browser-dir', 'data', allow_duplicate=True), Output('browser-selection', 'children', allow_duplicate=True)],
              Input('browser-up-btn', 'n_clicks'), [State('browser-dir', 'data'), State('browser-type', 'data')], prevent_initial_call=True)
def navigate_up(n, current_dir, btype):
    if not n: return dash.no_update, dash.no_update
    new_dir = get_parent_directory(current_dir)
    return (new_dir, new_dir) if btype != 'csv' else (new_dir, 'No file selected')


@app.callback([Output('browser-dir', 'data', allow_duplicate=True), Output('browser-selection', 'children', allow_duplicate=True)],
              Input('browser-home-btn', 'n_clicks'), State('browser-type', 'data'), prevent_initial_call=True)
def navigate_home(n, btype):
    if not n: return dash.no_update, dash.no_update
    home = os.path.expanduser('~')
    return (home, home) if btype != 'csv' else (home, 'No file selected')


@app.callback([Output('browser-contents', 'children'), Output('browser-path', 'children')],
              Input('browser-dir', 'data'), State('browser-type', 'data'))
def update_contents(current_dir, btype):
    if not current_dir: current_dir = os.path.expanduser('~')
    folders, files = get_directory_contents(current_dir, show_videos=(btype == 'vid'))
    items = [create_browser_item(f) for f in folders] + [create_browser_item(f) for f in files]
    if not items: items = [html.Div("No items found", style={'color': '#666', 'padding': '20px', 'textAlign': 'center'})]
    return items, current_dir


@app.callback([Output('browser-dir', 'data', allow_duplicate=True), Output('browser-selected', 'data', allow_duplicate=True),
               Output('browser-selection', 'children', allow_duplicate=True)],
              Input({'type': 'browser-item', 'path': ALL, 'itemtype': ALL}, 'n_clicks'),
              [State('browser-type', 'data'), State('browser-dir', 'data')], prevent_initial_call=True)
def handle_click(n_clicks_list, btype, current_dir):
    if not ctx.triggered or not any(n_clicks_list): return dash.no_update, dash.no_update, dash.no_update
    trig = ctx.triggered_id
    path, itemtype = trig['path'], trig['itemtype']
    if itemtype == 'folder':
        return (path, '', path) if btype != 'csv' else (path, '', 'No file selected')
    return dash.no_update, path, os.path.basename(path)


@app.callback([Output('csv-path-input', 'value', allow_duplicate=True), Output('images-root-input', 'value', allow_duplicate=True),
               Output('output-path-input', 'value', allow_duplicate=True), Output('videos-root-input', 'value', allow_duplicate=True),
               Output('browser-modal', 'style', allow_duplicate=True)],
              Input('browser-select-btn', 'n_clicks'),
              [State('browser-type', 'data'), State('browser-selected', 'data'), State('browser-dir', 'data')], prevent_initial_call=True)
def apply_selection(n, btype, selected, current_dir):
    if not n: return [dash.no_update] * 5
    if btype == 'csv':
        if not selected: return [dash.no_update] * 5
        value = selected
    else:
        value = current_dir
    outputs = [dash.no_update] * 4
    idx = {'csv': 0, 'img': 1, 'out': 2, 'vid': 3}.get(btype)
    if idx is not None: outputs[idx] = value
    return outputs + [{'display': 'none'}]
