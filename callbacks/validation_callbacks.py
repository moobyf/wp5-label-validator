"""Main validation callbacks."""
import os
import sys
import pandas as pd
from io import StringIO
from datetime import datetime
from dash import html, ctx, dcc, Input, Output, State, ALL
import dash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from config import DEFAULT_LABELS, save_labels_to_file
from utils import load_csv_from_path, get_cached_image, prefetch_images, load_session
from layouts import create_validation_ui


@app.callback(
    [Output('main-content', 'children'), Output('image-list-store', 'data'), Output('root-dir-store', 'data'),
     Output('output-path-store', 'data'), Output('videos-root-store', 'data'), Output('current-index', 'data'),
     Output('df-store', 'data'), Output('load-status', 'children'), Output('labels-store', 'data', allow_duplicate=True),
     Output('config-page', 'style'), Output('validation-page', 'style'), Output('current-file-info', 'children')],
    Input('start-btn', 'n_clicks'),
    [State('csv-path-input', 'value'), State('images-root-input', 'value'), State('output-path-input', 'value'),
     State('videos-root-input', 'value'), State('labels-store', 'data'), State('confidence-threshold', 'value')],
    prevent_initial_call=True
)
def start_validation(n_clicks, csv_path, img_root, out_path, vid_root, labels, conf_threshold):
    if not n_clicks:
        return [dash.no_update] * 12
    
    session = load_session()
    saved_index = 0
    if session and session.get('output_path'):
        # Check if resuming same session
        if out_path and session.get('output_path') == out_path:
            saved_index = session.get('current_index', 0)
        elif not out_path and os.path.exists(session.get('output_path', '')):
            # Auto-resume if output exists
            out_path = session.get('output_path')
            saved_index = session.get('current_index', 0)   
    
    if not csv_path or not img_root:
        return (dash.no_update, [], '', '', '', 0, None, 
                html.Div("❌ Please specify CSV file and images directory", style={'color': 'red', 'fontWeight': 'bold'}),
                labels, dash.no_update, dash.no_update, dash.no_update)
    
    # Determine source file
    source_file = csv_path
    if out_path and out_path.endswith('.csv') and os.path.exists(out_path):
        try:
            temp_df = pd.read_csv(out_path)
            if 'validated' in temp_df.columns:
                source_file = out_path
        except: pass
    
    # Pass img_root as crops_root to resolve relative paths
    df_json, error = load_csv_from_path(source_file, crops_root=img_root)
    if error:
        return (dash.no_update, [], '', '', '', 0, None,
                html.Div(f"❌ {error}", style={'color': 'red'}), labels, dash.no_update, dash.no_update, dash.no_update)
    
    df = pd.read_json(StringIO(df_json), orient='split') 
    img_root = img_root.rstrip('/') + '/'
    
    # Handle output path
    if not out_path:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = os.path.splitext(os.path.basename(csv_path))[0]
        out_path = os.path.join(img_root, f'{base}_validated_{ts}.csv')
    elif os.path.isdir(out_path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = os.path.splitext(os.path.basename(csv_path))[0]
        out_path = os.path.join(out_path, f'{base}_validated_{ts}.csv')
    elif not out_path.endswith('.csv'):
        out_path = out_path + '.csv'
    
    # Filter
    filtered_df = df[df['validated'] == 'No'].copy()
    if conf_threshold is not None:
        if 'YOLO_Confidence' in df.columns and 'DINO_Confidence' in df.columns:
            filtered_df = filtered_df[(filtered_df['YOLO_Confidence'] < conf_threshold) | (filtered_df['DINO_Confidence'] < conf_threshold)]
        elif 'YOLO_Confidence' in df.columns:
            filtered_df = filtered_df[filtered_df['YOLO_Confidence'] < conf_threshold]
    
    image_list = filtered_df['image_path'].tolist()
    validated_count = len(df[df['validated'] == 'Yes'])
    
    if not image_list:
        return (html.Div("No images to validate"), [], img_root, out_path, vid_root or '', 0, df_json,
                html.Span("✅ All images validated!", style={'color': 'green'}), labels,
                {'display': 'none'}, {'display': 'block'}, f"📄 {os.path.basename(out_path)}")
    
    if saved_index >= len(image_list):
        saved_index = 0
    
    file_info = html.Div([
        html.Span("📄 ", style={'fontWeight': 'bold'}),
        html.Span(os.path.basename(out_path), style={'marginRight': '20px'}),
        html.Span(f"📊 {validated_count} done / {len(image_list)} pending", style={'color': '#17a2b8'})
    ])
    
    return (create_validation_ui(), image_list, img_root, out_path, vid_root or '', saved_index, df_json,
            html.Span(f"✅ Loaded {len(df)} rows", style={'color': 'green'}), labels,
            {'display': 'none'}, {'display': 'block'}, file_info)


@app.callback(Output('label-buttons', 'children'), Input('labels-store', 'data'))
def update_label_buttons(labels):
    if not labels: return []
    return [html.Button(label, id={'type': 'label-btn', 'label': label}, n_clicks=0,
                        style={'display': 'block', 'width': '100%', 'padding': '8px', 'marginBottom': '5px',
                               'textAlign': 'left', 'backgroundColor': 'white', 'border': '1px solid #dee2e6',
                               'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '14px'}) for label in labels]


@app.callback([Output('selected-label', 'data'), Output('selected-display', 'children'), Output('validation-source', 'data')],
              [Input({'type': 'label-btn', 'label': ALL}, 'n_clicks'),
               Input('accept-yolo-btn', 'n_clicks'), Input('accept-dino-btn', 'n_clicks'),
               Input({'type': 'dino-top-btn', 'index': ALL}, 'n_clicks')],
              [State('df-store', 'data'), State('current-index', 'data'), State('image-list-store', 'data'), State('labels-store', 'data')],
              prevent_initial_call=True)
def select_label(label_clicks, yolo_click, dino_click, dino_top_clicks, df_json, index, image_list, labels):
    if not ctx.triggered or not df_json or not image_list: return dash.no_update, dash.no_update, dash.no_update
    trigger = ctx.triggered_id
    df = pd.read_json(StringIO(df_json), orient='split') 
    row = df[df['image_path'] == image_list[index]].iloc[0]
    
    if trigger == 'accept-yolo-btn':
        label = str(row.get('YOLO_Prediction', ''))
        source = 'YOLO'
    elif trigger == 'accept-dino-btn':
        label = str(row.get('DINO_Prediction', ''))
        source = 'DINO'
    elif isinstance(trigger, dict) and trigger.get('type') == 'dino-top-btn':
        # Handle DINO top3 buttons
        dino_idx = trigger.get('index')
        label = str(row.get(f'dino_top{dino_idx}_class', ''))
        source = f'DINO_top{dino_idx}'
    elif isinstance(trigger, dict) and trigger.get('type') == 'label-btn':
        label = trigger.get('label', '')
        # Check if it's a manual label (not from predictions)
        yolo_pred = str(row.get('YOLO_Prediction', ''))
        dino_pred = str(row.get('DINO_Prediction', ''))
        if label == yolo_pred:
            source = 'YOLO'
        elif label == dino_pred:
            source = 'DINO'
        else:
            source = 'manual'
    else:
        return dash.no_update, dash.no_update, dash.no_update
    return label, label, source


@app.callback([Output('labels-store', 'data', allow_duplicate=True), Output('new-label-input', 'value')],
              Input('add-label-btn', 'n_clicks'),
              [State('new-label-input', 'value'), State('labels-store', 'data')], prevent_initial_call=True)
def add_new_label(n, new_label, labels):
    if n and new_label and new_label.strip():
        new_label = new_label.strip()
        if new_label not in labels:
            labels = labels + [new_label]
            save_labels_to_file(labels)
        return labels, ''  # Clear input
    return labels, dash.no_update


@app.callback(Output('delete-label-dropdown', 'options'),
              Input('labels-store', 'data'))
def update_delete_dropdown(labels):
    if not labels:
        return []
    return [{'label': lbl, 'value': lbl} for lbl in sorted(labels)]


@app.callback([Output('labels-store', 'data', allow_duplicate=True), Output('delete-label-dropdown', 'value')],
              Input('delete-label-btn', 'n_clicks'),
              [State('delete-label-dropdown', 'value'), State('labels-store', 'data')], prevent_initial_call=True)
def delete_label(n, label_to_delete, labels):
    if n and label_to_delete and label_to_delete in labels:
        labels = [lbl for lbl in labels if lbl != label_to_delete]
        save_labels_to_file(labels)
        return labels, None  # Clear dropdown
    return dash.no_update, dash.no_update


@app.callback([Output('config-page', 'style', allow_duplicate=True), Output('validation-page', 'style', allow_duplicate=True)],
              Input('load-different-btn', 'n_clicks'), prevent_initial_call=True)
def load_different_file(n):
    return ({'display': 'block'}, {'display': 'none'}) if n else (dash.no_update, dash.no_update)


@app.callback([Output('image-list-store', 'data', allow_duplicate=True), Output('current-index', 'data', allow_duplicate=True)],
              [Input('filter-mode', 'value'), Input('species-filter', 'value'), Input('search-input', 'value')],
              State('df-store', 'data'), prevent_initial_call=True)
def apply_filters(filter_mode, species_filter, search_text, df_json):
    if not df_json: return dash.no_update, dash.no_update
    df = pd.read_json(StringIO(df_json), orient='split') 
    mask = pd.Series([True] * len(df))
    
    if filter_mode == 'validated': mask &= (df['validated'] == 'Yes')
    elif filter_mode == 'unvalidated': mask &= (df['validated'] == 'No')
    
    if species_filter and species_filter != 'all':
        sp_mask = pd.Series([False] * len(df))
        if 'YOLO_Prediction' in df.columns: sp_mask |= (df['YOLO_Prediction'] == species_filter)
        if 'DINO_Prediction' in df.columns: sp_mask |= (df['DINO_Prediction'] == species_filter)
        mask &= sp_mask
    
    if search_text:
        mask &= df['image_path'].str.lower().str.contains(search_text.lower(), na=False)
    
    return df[mask]['image_path'].tolist(), 0
