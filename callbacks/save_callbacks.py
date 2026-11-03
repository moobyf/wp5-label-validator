"""Save validation callbacks."""
import os
import sys
import shutil
import pandas as pd
from io import StringIO
from dash import html, Input, Output, State
import dash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils import invalidate_cache_entry
from utils.csv_utils import save_csv


def move_image_to_label_folder(image_path, label, root_dir):
    """Move image to folder corresponding to its validated label.
    
    Returns: (new_path, error_message)
    """
    try:
        # Get full path
        if os.path.isabs(image_path):
            full_path = image_path
        else:
            full_path = os.path.join(root_dir, image_path)
        
        if not os.path.exists(full_path):
            return image_path, None  # File doesn't exist, keep original path
        
        # Get current directory and filename
        current_dir = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        
        # Get parent of current directory (where species folders are)
        parent_dir = os.path.dirname(current_dir)
        current_folder = os.path.basename(current_dir)
        
        # If already in correct folder, do nothing
        if current_folder == label:
            return image_path, None
        
        # Create target folder if needed
        target_dir = os.path.join(parent_dir, label)
        os.makedirs(target_dir, exist_ok=True)

        # On Windows / Mac the file system ignores case: 'fish' and 'Fish' are the SAME folder.
        # Without this check the file was "moved" onto itself and renamed *_1.jpg, *_1_1.jpg ...
        if os.path.samefile(target_dir, current_dir):
            return image_path, None
        
        # Target path
        target_path = os.path.join(target_dir, filename)
        
        # Handle filename collision
        if os.path.exists(target_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(target_path):
                target_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                counter += 1
        
        # Move the file
        shutil.move(full_path, target_path)
        
        # Calculate new relative path (same structure as original)
        if os.path.isabs(image_path):
            new_path = target_path
        else:
            # Rebuild relative path
            rel_parent = os.path.dirname(os.path.dirname(image_path))
            new_filename = os.path.basename(target_path)
            new_path = os.path.join(rel_parent, label, new_filename)
        
        return new_path, None
        
    except Exception as e:
        return image_path, str(e)


@app.callback(
    [Output('df-store', 'data', allow_duplicate=True), Output('current-index', 'data', allow_duplicate=True),
     Output('save-status', 'children'), Output('selected-label', 'data', allow_duplicate=True),
     Output('selected-display', 'children', allow_duplicate=True), Output('validation-source', 'data', allow_duplicate=True),
     Output('image-list-store', 'data', allow_duplicate=True)],
    Input('save-btn', 'n_clicks'),
    [State('selected-label', 'data'), State('validation-source', 'data'), State('current-index', 'data'), 
     State('image-list-store', 'data'), State('df-store', 'data'), State('output-path-store', 'data'),
     State('root-dir-store', 'data')],
    prevent_initial_call=True
)
def save_validation(n, label, source, index, image_list, df_json, output_path, root_dir):
    if not n or not label or not df_json:
        return dash.no_update, dash.no_update, html.Span("⚠️ Select a label first", style={'color': '#ffc107'}), dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    df = pd.read_json(StringIO(df_json), orient='split') 
    current_path = image_list[index]
    
    # Add validation_source column if not exists
    if 'validation_source' not in df.columns:
        df['validation_source'] = ''
    
    # Move image to label folder
    new_path, move_error = move_image_to_label_folder(current_path, label, root_dir)
    
    # Invalidate cache if path changed
    if new_path != current_path:
        invalidate_cache_entry(current_path)
    
    # Update dataframe
    df.loc[df['image_path'] == current_path, 'validated'] = 'Yes'
    df.loc[df['image_path'] == current_path, 'final_label'] = label
    df.loc[df['image_path'] == current_path, 'validation_source'] = source or 'manual'
    
    # Update image_path if moved
    if new_path != current_path:
        df.loc[df['image_path'] == current_path, 'image_path'] = new_path
        # Also update Crop_Path if it exists
        if 'Crop_Path' in df.columns:
            df.loc[df['image_path'] == new_path, 'Crop_Path'] = new_path
    
    # Update image list
    new_image_list = image_list.copy()
    new_image_list[index] = new_path
    
    try:
        # Use save_csv to properly handle relative paths and column names
        success, error = save_csv(df, output_path, root_dir)
        if not success:
            raise Exception(error)
        
        source_display = f" ({source})" if source else ""
        if move_error:
            status = html.Span([
                html.Span(f"✅ Saved: {label}{source_display}", style={'color': '#28a745'}),
                html.Span(f" ⚠️ Move error: {move_error}", style={'color': '#ffc107', 'fontSize': '12px'})
            ])
        elif new_path != current_path:
            status = html.Span(f"✅ Saved & moved to {label}/", style={'color': '#28a745'})
        else:
            status = html.Span(f"✅ Saved: {label}{source_display}", style={'color': '#28a745'})
    except Exception as e:
        return df.to_json(orient='split'), index, html.Span(f"❌ Error: {e}", style={'color': '#dc3545'}), '', 'None', '', image_list
    
    new_index = min(index + 1, len(image_list) - 1)
    return df.to_json(orient='split'), new_index, status, '', 'None', '', new_image_list
