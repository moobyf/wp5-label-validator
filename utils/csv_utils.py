"""CSV handling utilities."""
import os
import pandas as pd


# Column mapping: new format -> internal names
COLUMN_MAP = {
    # New pipeline format
    'crop_path': 'image_path',
    'yolo_prediction': 'YOLO_Prediction',
    'yolo_confidence': 'YOLO_Confidence',
    'dino_prediction': 'DINO_Prediction',
    'dino_confidence': 'DINO_Confidence',
    'dino_top1_class': 'dino_top1_class',
    'dino_top1_conf': 'dino_top1_conf',
    'dino_top2_class': 'dino_top2_class',
    'dino_top2_conf': 'dino_top2_conf',
    'dino_top3_class': 'dino_top3_class',
    'dino_top3_conf': 'dino_top3_conf',
    'frame_idx': 'frame_idx',
    'source_video': 'source_video',
    'source_stem': 'source_stem',
    # Old format (keep as-is)
    'Crop_Path': 'image_path',
}

# Reverse mapping for saving
REVERSE_COLUMN_MAP = {
    'image_path': 'crop_path',
    'YOLO_Prediction': 'yolo_prediction',
    'YOLO_Confidence': 'yolo_confidence',
    'DINO_Prediction': 'dino_prediction',
    'DINO_Confidence': 'dino_confidence',
}


def get_image_column(df):
    possible_names = ['image_path', 'Crop_Path', 'crop_path', 'path', 'file', 'filename']
    for name in possible_names:
        if name in df.columns:
            return name
    return None


def load_csv_from_path(csv_path, crops_root=''):
    """Load CSV, normalize columns, and resolve relative paths."""
    try:
        # The pipeline writes ';' separated CSVs, the app writes ',' -> detect it
        with open(csv_path, 'r', encoding='utf-8-sig', errors='ignore') as fh:
            header = fh.readline()
        sep = ';' if header.count(';') > header.count(',') else ','
        df = pd.read_csv(csv_path, sep=sep)
        
        # Detect original column name for crop path
        original_path_col = None
        for col in ['crop_path', 'Crop_Path', 'image_path']:
            if col in df.columns:
                original_path_col = col
                break
        
        # Rename columns to internal names
        rename_dict = {}
        for old_name, new_name in COLUMN_MAP.items():
            if old_name in df.columns and old_name != new_name:
                rename_dict[old_name] = new_name
        
        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)
        
        # Find image column
        img_col = get_image_column(df)
        if not img_col:
            return None, "No image path column found"
        if img_col != 'image_path':
            df['image_path'] = df[img_col]
        
        # Store original relative paths before resolving
        df['_original_path'] = df['image_path'].copy()
        df['_original_col_name'] = original_path_col or 'crop_path'
        df['_crops_root'] = crops_root or ''
        
        # Resolve relative paths if crops_root provided
        if crops_root:
            crops_root = os.path.abspath(crops_root)
            
            def resolve_path(p):
                if pd.isna(p) or not p:
                    return p
                p = str(p)
                # If already absolute and exists, keep it
                if os.path.isabs(p) and os.path.exists(p):
                    return p
                # Try to resolve relative to crops_root
                full_path = os.path.join(crops_root, p)
                if os.path.exists(full_path):
                    return full_path
                return p  # Return original if nothing works
            
            df['image_path'] = df['image_path'].apply(resolve_path)
        
        # Initialize validation columns
        if 'validated' not in df.columns:
            df['validated'] = 'No'
        if 'final_label' not in df.columns:
            df['final_label'] = ''
        if 'validation_source' not in df.columns:
            df['validation_source'] = ''
        
        return df.to_json(orient='split'), None
    except Exception as e:
        return None, str(e)


def save_csv(df, output_path, crops_root=''):
    """Save CSV, converting absolute paths back to relative."""
    try:
        # Create a copy for saving
        save_df = df.copy()
        
        # Get crops_root from dataframe if stored
        if '_crops_root' in save_df.columns and save_df['_crops_root'].iloc[0]:
            crops_root = save_df['_crops_root'].iloc[0]
        
        # Convert absolute paths back to relative
        if crops_root and 'image_path' in save_df.columns:
            crops_root = os.path.abspath(crops_root)
            
            def make_relative(p):
                if pd.isna(p) or not p:
                    return p
                p = str(p)
                if os.path.isabs(p) and p.startswith(crops_root):
                    # Remove crops_root prefix to get relative path
                    rel = os.path.relpath(p, crops_root)
                    return rel
                return p
            
            save_df['image_path'] = save_df['image_path'].apply(make_relative)
        
        # Get original column name
        original_col = 'crop_path'
        if '_original_col_name' in save_df.columns:
            original_col = save_df['_original_col_name'].iloc[0] or 'crop_path'
        
        # Remove internal columns before saving
        internal_cols = ['_original_path', '_original_col_name', '_crops_root']
        save_df = save_df.drop(columns=[c for c in internal_cols if c in save_df.columns])
        
        # Rename image_path back to original column name
        if 'image_path' in save_df.columns and original_col != 'image_path':
            save_df = save_df.rename(columns={'image_path': original_col})
        
        save_df.to_csv(output_path, index=False)
        return True, None
    except Exception as e:
        return False, str(e)
