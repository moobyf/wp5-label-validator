"""Navigation callbacks."""
import os
import sys
import pandas as pd
from io import StringIO
from dash import html, ctx, Input, Output, State
import dash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils import get_cached_image, prefetch_images


@app.callback(Output('current-index', 'data', allow_duplicate=True),
              [Input('prev-btn', 'n_clicks'), Input('next-btn', 'n_clicks'),
               Input('first-btn', 'n_clicks'), Input('last-btn', 'n_clicks')],
              [State('current-index', 'data'), State('image-list-store', 'data')], prevent_initial_call=True)
def navigate(prev, next_, first, last, index, image_list):
    if not image_list: return 0
    trigger = ctx.triggered_id
    if trigger == 'prev-btn': return max(0, index - 1)
    elif trigger == 'next-btn': return min(len(image_list) - 1, index + 1)
    elif trigger == 'first-btn': return 0
    elif trigger == 'last-btn': return len(image_list) - 1
    return index


@app.callback(Output('current-index', 'data', allow_duplicate=True), Input('goto-btn', 'n_clicks'),
              [State('goto-input', 'value'), State('image-list-store', 'data')], prevent_initial_call=True)
def goto_image(n, val, image_list):
    if n and val and image_list:
        return max(0, min(int(val) - 1, len(image_list) - 1))
    return dash.no_update


@app.callback(Output('zoom-level', 'data'),
              [Input('zoom-25', 'n_clicks'), Input('zoom-50', 'n_clicks'),
               Input('zoom-100', 'n_clicks'), Input('zoom-150', 'n_clicks')],
              State('zoom-level', 'data'), prevent_initial_call=True)
def change_zoom(z25, z50, z100, z150, current):
    return {'zoom-25': 25, 'zoom-50': 50, 'zoom-100': 100, 'zoom-150': 150}.get(ctx.triggered_id, current)


@app.callback(Output('zoom-display', 'children'), Input('zoom-level', 'data'))
def update_zoom_display(zoom):
    return f'{zoom}%'


@app.callback([Output('image-container', 'children'), Output('predictions-with-buttons', 'children'),
               Output('progress', 'children'), Output('species-filter', 'options')],
              [Input('current-index', 'data'), Input('zoom-level', 'data'), Input('image-refresh-trigger', 'data')],
              [State('image-list-store', 'data'), State('root-dir-store', 'data'), State('df-store', 'data')])
def update_image_display(index, zoom, refresh, image_list, root_dir, df_json): 
    if not image_list or not df_json or index >= len(image_list):
        return html.Div("No image"), html.Div(), "0 / 0", [{'label': 'All', 'value': 'all'}]
    
    current_path = image_list[index]
    df = pd.read_json(StringIO(df_json), orient='split') 
    row = df[df['image_path'] == current_path].iloc[0].to_dict()
    
    prefetch_images(image_list, index, root_dir)
    img_data = get_cached_image(current_path, root_dir)
    filename = os.path.basename(current_path)
    
    # Frame info
    frame_info_items = []
    if 'source_stem' in row or 'source_video' in row:
        video_name = row.get('source_stem', row.get('source_video', ''))
        if video_name:
            frame_info_items.append(html.Span([html.Strong("Video: "), str(video_name)], style={'marginRight': '15px'}))
    if 'frame_idx' in row:
        frame_info_items.append(html.Span([html.Strong("Frame: "), str(row.get('frame_idx', ''))], style={'marginRight': '15px'}))
    
    frame_info = html.Div(frame_info_items, style={'marginBottom': '8px', 'fontSize': '13px', 'color': '#666'}) if frame_info_items else None
    
    if img_data:
        img_content = html.Div([
            html.Div(f"📷 {filename}", style={'marginBottom': '8px', 'color': '#2c3e50', 'fontSize': '14px', 'fontWeight': 'bold'}),
            frame_info,
            html.Img(src=f"data:image/jpeg;base64,{img_data}", style={'width': f'{zoom}%', 'maxWidth': 'none'})
        ])
    else:
        img_content = html.Div([html.Div(f"📷 {filename}"), frame_info, html.Div("❌ Could not load image", style={'color': 'red'})])
    
    yolo_pred = row.get('YOLO_Prediction', 'N/A')
    yolo_conf = row.get('YOLO_Confidence', 0)
    dino_pred = row.get('DINO_Prediction', 'N/A')
    dino_conf = row.get('DINO_Confidence', 0)
    
    def conf_color(c):
        if c is None or (isinstance(c, float) and pd.isna(c)):
            return '#6c757d'
        return '#28a745' if c >= 0.8 else '#ffc107' if c >= 0.5 else '#dc3545'
    
    # YOLO button
    yolo_btn = html.Button(
        [html.Span("YOLO: ", style={'fontWeight': 'bold'}), html.Span(str(yolo_pred)),
         html.Span(f" ({yolo_conf:.2f})" if isinstance(yolo_conf, (int, float)) and not pd.isna(yolo_conf) else "", 
                   style={'color': conf_color(yolo_conf)})],
        id='accept-yolo-btn', n_clicks=0,
        style={'display': 'block', 'width': '100%', 'padding': '8px', 'marginBottom': '10px',
               'backgroundColor': '#e8f5e9', 'border': '2px solid #28a745', 'borderRadius': '4px',
               'cursor': 'pointer', 'textAlign': 'left', 'fontSize': '14px'}
    )
    
    # DINO section with Top 3
    dino_items = []
    
    # Check if we have top3 columns (new format)
    has_top3 = 'dino_top1_class' in row
    
    if has_top3:
        # New format: show top 3 DINO predictions
        dino_items.append(html.Div("🦕 DINO Top 3:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}))
        
        for i in range(1, 4):
            cls = row.get(f'dino_top{i}_class', '')
            conf = row.get(f'dino_top{i}_conf', 0)
            
            if cls and str(cls) not in ['nan', '', 'None']:
                conf_val = float(conf) if conf and not pd.isna(conf) else 0
                is_top1 = (i == 1)
                
                # Format confidence: show <0.001 for very small values
                if conf_val < 0.001:
                    conf_str = "<0.001"
                else:
                    conf_str = f"{conf_val:.3f}"
                
                btn_style = {
                    'display': 'flex', 'width': '100%', 'padding': '6px 10px', 'marginBottom': '4px',
                    'backgroundColor': '#e3f2fd' if is_top1 else '#f8f9fa',
                    'border': f'2px solid #17a2b8' if is_top1 else '1px solid #dee2e6',
                    'borderRadius': '4px', 'cursor': 'pointer', 'textAlign': 'left', 'fontSize': '13px',
                    'alignItems': 'center', 'justifyContent': 'space-between'
                }
                
                dino_items.append(
                    html.Button([
                        html.Span(f"#{i} ", style={'color': '#6c757d', 'marginRight': '5px'}),
                        html.Span(str(cls), style={'flex': '1', 'fontWeight': 'bold' if is_top1 else 'normal'}),
                        html.Span(conf_str, style={'color': conf_color(conf_val), 'fontWeight': 'bold'})
                    ],
                    id={'type': 'dino-top-btn', 'index': i}, n_clicks=0, style=btn_style)
                )
        
        # Add hidden placeholder for accept-dino-btn (required by callback)
        dino_items.append(html.Button(id='accept-dino-btn', n_clicks=0, style={'display': 'none'}))
    else:
        # Old format: single DINO prediction
        dino_items.append(
            html.Button(
                [html.Span("DINO: ", style={'fontWeight': 'bold'}), html.Span(str(dino_pred)),
                 html.Span(f" ({dino_conf:.2f})" if isinstance(dino_conf, (int, float)) and not pd.isna(dino_conf) else "",
                           style={'color': conf_color(dino_conf)})],
                id='accept-dino-btn', n_clicks=0,
                style={'display': 'block', 'width': '100%', 'padding': '8px',
                       'backgroundColor': '#e3f2fd', 'border': '2px solid #17a2b8', 'borderRadius': '4px',
                       'cursor': 'pointer', 'textAlign': 'left', 'fontSize': '14px'}
            )
        )
    
    predictions = html.Div([yolo_btn] + dino_items)
    
    total = len(image_list)
    validated_count = len(df[df['validated'] == 'Yes'])
    progress = html.Div([f"📍 {index + 1}/{total}", html.Span(f" | ✅ {validated_count}", style={'color': '#28a745', 'marginLeft': '10px'})])
    
    species_set = set()
    if 'YOLO_Prediction' in df.columns: species_set.update(df['YOLO_Prediction'].dropna().unique())
    if 'DINO_Prediction' in df.columns: species_set.update(df['DINO_Prediction'].dropna().unique())
    species_options = [{'label': 'All', 'value': 'all'}] + [{'label': s, 'value': s} for s in sorted(species_set) if s and s != 'nan']
    
    return img_content, predictions, progress, species_options


# Thumbnail gallery callbacks
THUMBNAILS_PER_PAGE = 20

@app.callback(
    [Output('thumbnail-gallery-container', 'style'), Output('thumbnail-gallery', 'children'),
     Output('gallery-title', 'children'), Output('gallery-page-info', 'children'), Output('gallery-page', 'data')],
    [Input('species-filter', 'value'), Input('image-list-store', 'data'), Input('gallery-prev', 'n_clicks'), Input('gallery-next', 'n_clicks')],
    [State('gallery-page', 'data'), State('root-dir-store', 'data'), State('df-store', 'data')]
)
def update_thumbnail_gallery(species, image_list, prev_click, next_click, page, root_dir, df_json):
    if not species or species == 'all' or not image_list or not df_json:
        return {'display': 'none'}, [], '', '', 0
    
    # Handle pagination
    trigger = dash.ctx.triggered_id
    if trigger == 'gallery-prev' and page > 0:
        page = page - 1
    elif trigger == 'gallery-next':
        page = page + 1
    elif trigger == 'species-filter' or trigger == 'image-list-store':
        page = 0  # Reset to first page on filter change or image list change
    
    total = len(image_list)
    total_pages = max(1, (total + THUMBNAILS_PER_PAGE - 1) // THUMBNAILS_PER_PAGE)
    page = min(page, total_pages - 1)
    
    start_idx = page * THUMBNAILS_PER_PAGE
    end_idx = min(start_idx + THUMBNAILS_PER_PAGE, total)
    
    thumbnails = []
    for i in range(start_idx, end_idx):
        path = image_list[i]
        img_data = get_cached_image(path, root_dir)
        if img_data:
            thumbnails.append(
                html.Div(
                    html.Img(src=f"data:image/jpeg;base64,{img_data}", 
                             style={'width': '60px', 'height': '60px', 'objectFit': 'cover', 'borderRadius': '4px'}),
                    id={'type': 'thumbnail-click', 'index': i},
                    style={'cursor': 'pointer', 'border': '2px solid transparent', 'borderRadius': '6px', 'padding': '2px'},
                    title=os.path.basename(path),
                    className='thumbnail-item'
                )
            )
    
    title = f"🖼️ {species}: {total} images"
    page_info = f"{page + 1}/{total_pages}"
    
    return {'display': 'block', 'marginBottom': '15px'}, thumbnails, title, page_info, page


@app.callback(
    Output('current-index', 'data', allow_duplicate=True),
    Input({'type': 'thumbnail-click', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def click_thumbnail(n_clicks_list):
    if not dash.ctx.triggered or not any(n_clicks_list):
        return dash.no_update
    trigger = dash.ctx.triggered_id
    if trigger and isinstance(trigger, dict):
        return trigger.get('index', 0)
    return dash.no_update
