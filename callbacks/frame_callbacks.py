"""Frame viewer callbacks with bbox editing."""
import os
import sys
import re
from io import StringIO
import pandas as pd
from dash import html, dcc, Input, Output, State, ctx
import dash
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils import extract_video_info_from_crop_path, find_video_file, invalidate_cache_entry
from utils.video_utils import extract_frame_from_video
from utils.csv_utils import save_csv


# Columns that may hold the frame number / detection index in the CSV.
# Only the ones that actually exist in the dataframe are used.
FRAME_COLS = ['frame_idx', 'Frame', 'frame', 'frame_num', 'frame_number', 'frame_id']
DET_COLS = ['det_idx', 'detection_idx', 'det_id', 'detection_id', 'Detection', 'det_num']
# Prediction-specific columns that must NOT be copied from the source detection
CONF_COLS = ['YOLO_Confidence', 'DINO_Confidence']
CROP_NAME_RE = re.compile(r'^F(\d+)_D(\d+)_')


def safe_get_number(row, col, default=0):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else int(float(val))
    except Exception:
        return default


def get_row_bbox(row):
    return (safe_get_number(row, 'x_min'), safe_get_number(row, 'y_min'),
            safe_get_number(row, 'x_max'), safe_get_number(row, 'y_max'))


def get_video_frame(row):
    """(video_name, frame_num) of a detection row.

    The CSV columns (source_stem / frame_idx) are used first: the crop filename
    ({video}_{frame}.jpg) is not reliable, because it has no detection index and
    gets a '_1' suffix when two crops collide in the same species folder.
    The filename is only a fallback.
    """
    video, frame = None, None
    for col in FRAME_COLS:
        if col in row and not pd.isna(row.get(col)):
            frame = safe_get_number(row, col, None)
            if frame is not None:
                break
    for col in ('source_stem', 'source_video'):
        val = row.get(col)
        if val is not None and not pd.isna(val) and str(val):
            video = os.path.splitext(os.path.basename(str(val)))[0]
            break
    if video is None or frame is None:
        p_video, p_frame = extract_video_info_from_crop_path(row.get('image_path', '') or '')
        video = video or p_video
        frame = frame if frame is not None else p_frame
    return video, frame


def collect_frame_bboxes(df, video_name, frame_num, exclude_path=None):
    """All bboxes of the dataframe that belong to (video_name, frame_num)."""
    bboxes = []
    for _, row in df.iterrows():
        if exclude_path is not None and row.get('image_path', '') == exclude_path:
            continue
        v, f = get_video_frame(row)
        if v == video_name and f == frame_num:
            bboxes.append(get_row_bbox(row))
    return bboxes


def create_plotly_figure_with_frame(video_path, frame_num, original_bbox, new_bbox=None, other_bboxes=None):
    """Create plotly figure with frame and bboxes. NO text labels."""
    import numpy as np
    frame_img = extract_frame_from_video(video_path, frame_num)
    if frame_img is None:
        return None, None, None

    width, height = frame_img.size
    img_array = np.array(frame_img)

    fig = go.Figure()
    fig.add_trace(go.Image(z=img_array))

    # Other bboxes (cyan)
    if other_bboxes:
        for bbox in other_bboxes:
            ox_min, oy_min, ox_max, oy_max = bbox
            if ox_max > 0 and oy_max > 0:
                fig.add_shape(type="rect", x0=ox_min, y0=oy_min, x1=ox_max, y1=oy_max,
                              line=dict(color="cyan", width=2), fillcolor="rgba(0,255,255,0.1)")

    # Current bbox (green)
    x_min, y_min, x_max, y_max = original_bbox
    if x_max > 0 and y_max > 0:
        fig.add_shape(type="rect", x0=x_min, y0=y_min, x1=x_max, y1=y_max,
                      line=dict(color="lime", width=3), fillcolor="rgba(0,255,0,0.15)")

    # New bbox (orange)
    if new_bbox:
        nx_min, ny_min, nx_max, ny_max = new_bbox
        if nx_max > 0 and ny_max > 0:
            fig.add_shape(type="rect", x0=nx_min, y0=ny_min, x1=nx_max, y1=ny_max,
                          line=dict(color="orange", width=3, dash="dash"), fillcolor="rgba(255,165,0,0.15)")

    fig.update_layout(
        dragmode="drawrect",
        newshape=dict(line=dict(color="orange", width=3), fillcolor="rgba(255,165,0,0.2)"),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, width]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", range=[height, 0]),
        height=650
    )

    config = {'modeBarButtonsToAdd': ['drawrect', 'eraseshape'], 'displayModeBar': True, 'displaylogo': False, 'scrollZoom': True}
    return fig, (width, height), config


def build_frame_view(df, video_path, frame_num, current_path, orig_bbox, new_bbox=None):
    """Graph + info texts for (video, frame).

    The green box is only drawn when the viewer is on the frame of the current crop;
    every other detection of that frame is drawn in cyan.
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    own_frame = None
    if current_path is not None:
        row = df[df['image_path'] == current_path]
        if len(row):
            _, own_frame = get_video_frame(row.iloc[0].to_dict())

    on_own_frame = own_frame is not None and own_frame == frame_num
    if on_own_frame:
        others = collect_frame_bboxes(df, video_name, frame_num, exclude_path=current_path)
        green = orig_bbox
    else:
        others = collect_frame_bboxes(df, video_name, frame_num)
        green = (0, 0, 0, 0)

    fig, dims, config = create_plotly_figure_with_frame(video_path, frame_num, green, new_bbox, others)
    if fig is None:
        return None, None, None, None

    width, height = dims
    n_total = len(others) + (1 if on_own_frame else 0)
    info = f"Video: {video_name} | Frame: {frame_num} | {width}x{height} | {n_total} detections"
    if on_own_frame:
        status = f"Green=Current | Cyan=Others ({len(others)}) | Draw orange for NEW"
    else:
        status = f"Cyan=Detections ({len(others)}) | Draw orange for NEW"
    graph = dcc.Graph(id='frame-graph', figure=fig, config=config, style={'width': '100%', 'height': '100%'})
    return graph, info, status, dims


def save_df(df, output_path, root_dir):
    """Save with the same function as save_callbacks (keeps paths / column names consistent)."""
    success, error = save_csv(df, output_path, root_dir)
    if not success:
        raise Exception(error)


@app.callback(
    [Output('frame-modal', 'style'), Output('frame-image-container', 'children'), Output('frame-info', 'children'),
     Output('frame-status', 'children'), Output('edit-x-min', 'value'), Output('edit-y-min', 'value'),
     Output('edit-x-max', 'value'), Output('edit-y-max', 'value'), Output('current-video-path', 'data'),
     Output('current-frame-num', 'data'), Output('bbox-save-status', 'children'), Output('original-bbox-store', 'data'),
     Output('original-bbox-display', 'children'), Output('new-bbox-display', 'children'), Output('frame-dimensions', 'data')],
    Input('view-frame-btn', 'n_clicks'),
    [State('current-index', 'data'), State('image-list-store', 'data'), State('df-store', 'data'), State('videos-root-store', 'data')],
    prevent_initial_call=True
)
def open_frame_viewer(n_clicks, index, image_list, df_json, videos_dir):
    empty_bbox = {'x_min': 0, 'y_min': 0, 'x_max': 0, 'y_max': 0}
    default_dims = {'width': 1920, 'height': 1080}

    if not n_clicks or not image_list or not df_json or index >= len(image_list):
        return ({'display': 'none'}, html.Div(), "", "", 0, 0, 0, 0, '', 0, "", empty_bbox, "", "", default_dims)

    def warn(msg, color='#ffc107'):
        return ({'display': 'block'}, html.Div(msg, style={'color': color, 'textAlign': 'center', 'padding': '40px'}),
                "", "", 0, 0, 0, 0, '', 0, "", empty_bbox, "", "", default_dims)

    current_path = image_list[index]
    df = pd.read_json(StringIO(df_json), orient='split')
    rows = df[df['image_path'] == current_path]
    if not len(rows):
        return warn(f"⚠️ Row not found: {os.path.basename(current_path)}")
    row = rows.iloc[0].to_dict()

    if not videos_dir:
        return warn("⚠️ Videos directory not configured")

    video_name, frame_num = get_video_frame(row)
    if not video_name or frame_num is None:
        return warn(f"⚠️ Cannot parse: {os.path.basename(current_path)}")

    video_path = find_video_file(video_name, videos_dir)
    if not video_path:
        return warn(f"⚠️ Video not found: {video_name}")

    x_min, y_min, x_max, y_max = get_row_bbox(row)
    orig = {'x_min': x_min, 'y_min': y_min, 'x_max': x_max, 'y_max': y_max}

    graph, info, status, dims = build_frame_view(df, video_path, frame_num, current_path, (x_min, y_min, x_max, y_max))
    if graph is None:
        return ({'display': 'block'}, html.Div("⚠️ Could not extract frame", style={'color': '#dc3545', 'textAlign': 'center', 'padding': '40px'}),
                "", "", x_min, y_min, x_max, y_max, video_path, frame_num, "", orig,
                f"({x_min}, {y_min}) - ({x_max}, {y_max})", "(draw)", default_dims)

    width, height = dims
    return ({'display': 'block'}, graph, info, status,
            x_min, y_min, x_max, y_max, video_path, frame_num, "", orig,
            f"({x_min}, {y_min}) - ({x_max}, {y_max})", "(draw on image)", {'width': width, 'height': height})


@app.callback(
    [Output('new-bbox-display', 'children', allow_duplicate=True), Output('edit-x-min', 'value', allow_duplicate=True),
     Output('edit-y-min', 'value', allow_duplicate=True), Output('edit-x-max', 'value', allow_duplicate=True),
     Output('edit-y-max', 'value', allow_duplicate=True)],
    Input('frame-graph', 'relayoutData'),
    [State('edit-x-min', 'value'), State('edit-y-min', 'value'), State('edit-x-max', 'value'), State('edit-y-max', 'value')],
    prevent_initial_call=True
)
def capture_drawn_bbox(relayout_data, cur_x0, cur_y0, cur_x1, cur_y1):
    if not relayout_data:
        return [dash.no_update] * 5

    coords = None
    # 1) A new rectangle was drawn: plotly sends the full list of shapes
    if 'shapes' in relayout_data and relayout_data['shapes']:
        last = relayout_data['shapes'][-1]
        if last.get('type') == 'rect':
            coords = (last.get('x0', 0), last.get('y0', 0), last.get('x1', 0), last.get('y1', 0))
    else:
        # 2) A drawn rectangle was moved / resized: plotly sends 'shapes[k].x0', ...
        edits = {}
        for key, val in relayout_data.items():
            m = re.match(r'^shapes\[(\d+)\]\.(x0|y0|x1|y1)$', key)
            if m:
                edits.setdefault(int(m.group(1)), {})[m.group(2)] = val
        if edits:
            shape = edits[max(edits)]
            coords = (shape.get('x0', cur_x0 or 0), shape.get('y0', cur_y0 or 0),
                      shape.get('x1', cur_x1 or 0), shape.get('y1', cur_y1 or 0))

    if coords is None:
        return [dash.no_update] * 5

    x0, y0, x1, y1 = (int(round(float(c))) for c in coords)
    x_min, x_max = max(0, min(x0, x1)), max(x0, x1)
    y_min, y_max = max(0, min(y0, y1)), max(y0, y1)
    return f"({x_min}, {y_min}) - ({x_max}, {y_max})", x_min, y_min, x_max, y_max


@app.callback(
    [Output('bbox-save-status', 'children', allow_duplicate=True), Output('df-store', 'data', allow_duplicate=True),
     Output('image-refresh-trigger', 'data')],
    Input('save-bbox-btn', 'n_clicks'),
    [State('edit-x-min', 'value'), State('edit-y-min', 'value'), State('edit-x-max', 'value'), State('edit-y-max', 'value'),
     State('current-index', 'data'), State('image-list-store', 'data'), State('df-store', 'data'),
     State('output-path-store', 'data'), State('current-video-path', 'data'), State('current-frame-num', 'data'),
     State('root-dir-store', 'data'), State('image-refresh-trigger', 'data')],
    prevent_initial_call=True
)
def save_bbox(n, x_min, y_min, x_max, y_max, index, image_list, df_json, output_path, video_path, frame_num, root_dir, trigger):
    if not n or not df_json:
        return dash.no_update, dash.no_update, dash.no_update

    x_min, y_min, x_max, y_max = int(x_min or 0), int(y_min or 0), int(x_max or 0), int(y_max or 0)
    if x_max <= x_min or y_max <= y_min:
        return html.Span("❌ Invalid bbox", style={'color': '#dc3545'}), dash.no_update, dash.no_update

    df = pd.read_json(StringIO(df_json), orient='split')
    current_path = image_list[index]
    rows = df[df['image_path'] == current_path]
    if not len(rows):
        return html.Span("❌ Row not found", style={'color': '#dc3545'}), dash.no_update, dash.no_update

    # The crop must be cut from ITS OWN frame, not from the frame the viewer navigated to
    _, own_frame = get_video_frame(rows.iloc[0].to_dict())
    if own_frame is not None and frame_num is not None and own_frame != frame_num:
        return (html.Span(f"⚠️ You are on frame {frame_num} but this detection belongs to frame {own_frame}. "
                          f"Use 'Add detection' to create a new bbox on this frame.", style={'color': '#ffc107'}),
                dash.no_update, dash.no_update)

    df.loc[df['image_path'] == current_path, ['x_min', 'y_min', 'x_max', 'y_max']] = [x_min, y_min, x_max, y_max]
    if 'bbox_edited' not in df.columns:
        df['bbox_edited'] = 'No'
    df.loc[df['image_path'] == current_path, 'bbox_edited'] = 'Yes'

    if video_path and frame_num is not None:
        try:
            frame_img = extract_frame_from_video(video_path, frame_num)
            if frame_img:
                crop = frame_img.crop((x_min, y_min, x_max, y_max))
                crop_path = current_path if os.path.isabs(current_path) else os.path.join(root_dir, current_path)
                os.makedirs(os.path.dirname(crop_path), exist_ok=True)
                crop.save(crop_path, 'JPEG', quality=95)
                invalidate_cache_entry(current_path)
        except Exception as e:
            print(f"Error saving crop: {e}")

    try:
        save_df(df, output_path, root_dir)
    except Exception as e:
        return html.Span(f"❌ Error saving CSV: {e}", style={'color': '#dc3545'}), df.to_json(orient='split'), (trigger or 0) + 1
    return html.Span("✅ BBox saved", style={'color': '#28a745', 'fontWeight': 'bold'}), df.to_json(orient='split'), (trigger or 0) + 1


@app.callback(
    [Output('bbox-save-status', 'children', allow_duplicate=True), Output('df-store', 'data', allow_duplicate=True),
     Output('image-list-store', 'data', allow_duplicate=True), Output('image-refresh-trigger', 'data', allow_duplicate=True),
     Output('frame-image-container', 'children', allow_duplicate=True), Output('frame-info', 'children', allow_duplicate=True),
     Output('frame-status', 'children', allow_duplicate=True), Output('new-bbox-display', 'children', allow_duplicate=True),
     Output('edit-x-min', 'value', allow_duplicate=True), Output('edit-y-min', 'value', allow_duplicate=True),
     Output('edit-x-max', 'value', allow_duplicate=True), Output('edit-y-max', 'value', allow_duplicate=True)],
    Input('add-detection-btn', 'n_clicks'),
    [State('edit-x-min', 'value'), State('edit-y-min', 'value'), State('edit-x-max', 'value'), State('edit-y-max', 'value'),
     State('current-index', 'data'), State('image-list-store', 'data'), State('df-store', 'data'),
     State('output-path-store', 'data'), State('current-video-path', 'data'), State('current-frame-num', 'data'),
     State('root-dir-store', 'data'), State('image-refresh-trigger', 'data'), State('original-bbox-store', 'data')],
    prevent_initial_call=True
)
def add_new_detection(n, x_min, y_min, x_max, y_max, index, image_list, df_json, output_path, video_path, frame_num,
                      root_dir, trigger, orig_bbox):
    NO = dash.no_update

    def fail(msg):
        return (html.Span(msg, style={'color': '#dc3545'}),) + (NO,) * 11

    if not n or not df_json or not video_path or frame_num is None:
        return (NO,) * 12

    x_min, y_min, x_max, y_max = int(x_min or 0), int(y_min or 0), int(x_max or 0), int(y_max or 0)
    if x_max <= x_min or y_max <= y_min:
        return fail("❌ Draw a rectangle first")

    df = pd.read_json(StringIO(df_json), orient='split')
    current_path = image_list[index]
    rows = df[df['image_path'] == current_path]
    if not len(rows):
        return fail("❌ Current row not found")
    current_row = rows.iloc[0].to_dict()

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    frame_num = int(frame_num)

    # Avoid adding twice the same box (double click on the button)
    if (x_min, y_min, x_max, y_max) in collect_frame_bboxes(df, video_name, frame_num):
        return fail("⚠️ This bbox already exists on this frame")

    current_dir = os.path.dirname(current_path)
    crop_dir = current_dir if os.path.isabs(current_path) else os.path.join(root_dir, current_dir)

    # Find a unique detection number for THIS frame (any folder, CSV + disk)
    frame_prefix = f"F{frame_num}_D"
    video_suffix = f"_{video_name}.jpg"
    max_det = -1

    def det_from_name(bn):
        if bn.startswith(frame_prefix) and video_name in bn:
            try:
                return int(bn[len(frame_prefix):].split('_')[0])
            except Exception:
                return None
        return None

    for p in df['image_path'].astype(str).tolist():
        d = det_from_name(os.path.basename(p))
        if d is not None:
            max_det = max(max_det, d)
    if os.path.isdir(crop_dir):
        for f in os.listdir(crop_dir):
            if f.endswith(video_suffix) or video_name in f:
                d = det_from_name(f)
                if d is not None:
                    max_det = max(max_det, d)
    # Detections of this frame whose filename does not follow the F*_D* pattern
    for _, r in df.iterrows():
        v, f = get_video_frame(r)
        if v == video_name and f == frame_num:
            for col in DET_COLS:
                if col in r and not pd.isna(r.get(col)):
                    max_det = max(max_det, safe_get_number(r, col, -1))

    new_det_num = max_det + 1

    def make_paths(det):
        fname = f"F{frame_num}_D{det}_{video_name}.jpg"
        rel = os.path.join(current_dir, fname)
        full = rel if os.path.isabs(rel) else os.path.join(root_dir, rel)
        return fname, rel, full

    new_filename, new_crop_path, crop_full_path = make_paths(new_det_num)
    existing_paths = set(df['image_path'].astype(str))
    while os.path.exists(crop_full_path) or new_crop_path in existing_paths:
        new_det_num += 1
        new_filename, new_crop_path, crop_full_path = make_paths(new_det_num)

    try:
        frame_img = extract_frame_from_video(video_path, frame_num)
        if not frame_img:
            return fail("❌ Could not extract frame")
        crop = frame_img.crop((x_min, y_min, x_max, y_max))
        os.makedirs(os.path.dirname(crop_full_path), exist_ok=True)
        crop.save(crop_full_path, 'JPEG', quality=95)
    except Exception as e:
        return fail(f"❌ Error: {e}")

    # New row: copy only the video-level metadata of the current detection,
    # then overwrite everything that is specific to this new bbox / frame.
    new_row = {col: current_row.get(col, '') for col in df.columns}
    new_row.update({'image_path': new_crop_path, 'x_min': x_min, 'y_min': y_min, 'x_max': x_max, 'y_max': y_max,
                    'validated': 'No', 'final_label': '', 'bbox_edited': 'Yes', 'manually_added': 'Yes'})
    for col in FRAME_COLS:
        if col in df.columns:
            new_row[col] = frame_num
    for col in DET_COLS:
        if col in df.columns:
            new_row[col] = new_det_num
    if 'YOLO_Prediction' in df.columns: new_row['YOLO_Prediction'] = 'manual_detection'
    if 'DINO_Prediction' in df.columns: new_row['DINO_Prediction'] = 'manual_detection'
    for col in CONF_COLS:
        if col in df.columns:
            new_row[col] = 0.0  # 0 so it still passes the "confidence < threshold" filter
    for i in range(1, 4):
        if f'dino_top{i}_class' in df.columns: new_row[f'dino_top{i}_class'] = ''
        if f'dino_top{i}_conf' in df.columns: new_row[f'dino_top{i}_conf'] = 0.0
    if 'validation_source' in df.columns: new_row['validation_source'] = ''
    if 'Crop_Path' in df.columns: new_row['Crop_Path'] = new_crop_path
    if 'crop_filename' in df.columns: new_row['crop_filename'] = new_filename
    if '_original_path' in df.columns: new_row['_original_path'] = new_crop_path

    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    new_image_list = image_list.copy()
    new_image_list.insert(index + 1, new_crop_path)

    try:
        save_df(new_df, output_path, root_dir)
    except Exception as e:
        return fail(f"❌ Crop created but CSV not saved: {e}")

    # Redraw the frame: the new bbox now appears (cyan) and the orange drawing is cleared,
    # so another bbox can be drawn and added on the same frame right away.
    orig = (orig_bbox['x_min'], orig_bbox['y_min'], orig_bbox['x_max'], orig_bbox['y_max']) if orig_bbox else (0, 0, 0, 0)
    graph, info, status, _ = build_frame_view(new_df, video_path, frame_num, current_path, orig)
    if graph is None:
        graph, info, status = NO, NO, NO

    return (html.Span(f"✅ Added: {new_filename} (frame {frame_num})", style={'color': '#28a745', 'fontWeight': 'bold'}),
            new_df.to_json(orient='split'), new_image_list, (trigger or 0) + 1,
            graph, info, status, "(draw on image)", 0, 0, 0, 0)


@app.callback(Output('frame-modal', 'style', allow_duplicate=True),
              [Input('close-frame-modal', 'n_clicks'), Input('frame-modal-backdrop', 'n_clicks')], prevent_initial_call=True)
def close_frame_viewer(close, backdrop):
    return {'display': 'none'} if close or backdrop else dash.no_update


@app.callback([Output('frame-image-container', 'children', allow_duplicate=True), Output('new-bbox-display', 'children', allow_duplicate=True)],
              Input('apply-manual-bbox-btn', 'n_clicks'),
              [State('edit-x-min', 'value'), State('edit-y-min', 'value'), State('edit-x-max', 'value'), State('edit-y-max', 'value'),
               State('current-video-path', 'data'), State('current-frame-num', 'data'), State('original-bbox-store', 'data'),
               State('df-store', 'data'), State('current-index', 'data'), State('image-list-store', 'data')],
              prevent_initial_call=True)
def apply_manual_bbox(n, x_min, y_min, x_max, y_max, video_path, frame_num, orig_bbox, df_json, index, image_list):
    if not n or not video_path or not df_json:
        return dash.no_update, dash.no_update
    df = pd.read_json(StringIO(df_json), orient='split')
    current_path = image_list[index] if image_list and index < len(image_list) else None
    orig = (orig_bbox['x_min'], orig_bbox['y_min'], orig_bbox['x_max'], orig_bbox['y_max'])
    new = (int(x_min or 0), int(y_min or 0), int(x_max or 0), int(y_max or 0))
    graph, _, _, _ = build_frame_view(df, video_path, frame_num, current_path, orig, new)
    if graph is not None:
        return graph, f"({new[0]}, {new[1]}) - ({new[2]}, {new[3]})"
    return dash.no_update, dash.no_update


@app.callback([Output('frame-image-container', 'children', allow_duplicate=True), Output('new-bbox-display', 'children', allow_duplicate=True),
               Output('edit-x-min', 'value', allow_duplicate=True), Output('edit-y-min', 'value', allow_duplicate=True),
               Output('edit-x-max', 'value', allow_duplicate=True), Output('edit-y-max', 'value', allow_duplicate=True)],
              Input('reset-bbox-btn', 'n_clicks'),
              [State('current-video-path', 'data'), State('current-frame-num', 'data'), State('original-bbox-store', 'data'),
               State('df-store', 'data'), State('current-index', 'data'), State('image-list-store', 'data')],
              prevent_initial_call=True)
def reset_bbox(n, video_path, frame_num, orig_bbox, df_json, index, image_list):
    if not n or not video_path or not df_json:
        return [dash.no_update] * 6
    df = pd.read_json(StringIO(df_json), orient='split')
    current_path = image_list[index] if image_list and index < len(image_list) else None
    orig = (orig_bbox['x_min'], orig_bbox['y_min'], orig_bbox['x_max'], orig_bbox['y_max'])
    graph, _, _, _ = build_frame_view(df, video_path, frame_num, current_path, orig)
    if graph is not None:
        return (graph, "(draw on image)", orig_bbox['x_min'], orig_bbox['y_min'], orig_bbox['x_max'], orig_bbox['y_max'])
    return [dash.no_update] * 6


@app.callback(
    [Output('current-frame-num', 'data', allow_duplicate=True),
     Output('frame-navigating', 'data')],
    [Input('prev-frame-btn', 'n_clicks'), Input('next-frame-btn', 'n_clicks')],
    State('current-frame-num', 'data'),
    prevent_initial_call=True
)
def navigate_frames(prev, next_, current_frame):
    trigger = ctx.triggered_id
    current_frame = int(current_frame or 0)
    if trigger == 'prev-frame-btn':
        return max(0, current_frame - 1), True
    elif trigger == 'next-frame-btn':
        return current_frame + 1, True
    return current_frame, False


@app.callback(
    [Output('frame-image-container', 'children', allow_duplicate=True),
     Output('frame-info', 'children', allow_duplicate=True),
     Output('frame-status', 'children', allow_duplicate=True),
     Output('new-bbox-display', 'children', allow_duplicate=True),
     Output('edit-x-min', 'value', allow_duplicate=True), Output('edit-y-min', 'value', allow_duplicate=True),
     Output('edit-x-max', 'value', allow_duplicate=True), Output('edit-y-max', 'value', allow_duplicate=True)],
    Input('frame-navigating', 'data'),
    [State('current-frame-num', 'data'), State('current-video-path', 'data'), State('original-bbox-store', 'data'),
     State('frame-modal', 'style'), State('df-store', 'data'), State('current-index', 'data'), State('image-list-store', 'data')],
    prevent_initial_call=True
)
def update_frame_on_navigate(is_navigating, frame_num, video_path, orig_bbox, modal_style, df_json, index, image_list):
    NO = dash.no_update
    if not is_navigating:
        return (NO,) * 8
    if not video_path or not modal_style or modal_style.get('display') == 'none' or not df_json:
        return (NO,) * 8

    df = pd.read_json(StringIO(df_json), orient='split')
    current_path = image_list[index] if image_list and index < len(image_list) else None
    orig = (orig_bbox['x_min'], orig_bbox['y_min'], orig_bbox['x_max'], orig_bbox['y_max'])
    graph, info, status, _ = build_frame_view(df, video_path, frame_num, current_path, orig)
    if graph is None:
        return (NO,) * 8

    # Back on the crop's own frame -> show its bbox in the fields; otherwise start empty
    row = df[df['image_path'] == current_path] if current_path else df.iloc[0:0]
    own_frame = get_video_frame(row.iloc[0].to_dict())[1] if len(row) else None
    if own_frame == frame_num:
        fields = (orig_bbox['x_min'], orig_bbox['y_min'], orig_bbox['x_max'], orig_bbox['y_max'])
    else:
        fields = (0, 0, 0, 0)
    return (graph, info, status, "(draw on image)") + fields
