"""File system utilities."""
import os


def is_path_allowed(path):
    allowed_prefixes = [os.path.expanduser('~'), '/marbec-data', '/scratch', '/data', '/shared', '/home']
    abs_path = os.path.abspath(path)
    for prefix in allowed_prefixes:
        if abs_path.startswith(prefix):
            return True
    return os.access(path, os.R_OK)


def is_valid_directory(path):
    return path and os.path.isdir(path) and os.access(path, os.R_OK)


def is_valid_file(path):
    return path and os.path.isfile(path) and os.access(path, os.R_OK)


def get_parent_directory(path):
    if not path:
        return os.path.expanduser('~')
    parent = os.path.dirname(path.rstrip('/'))
    if not parent or not is_valid_directory(parent):
        return os.path.expanduser('~')
    return parent


def get_directory_contents(path, show_hidden=False, show_videos=False):
    if not is_valid_directory(path) or not is_path_allowed(path):
        return [], []
    try:
        items = os.listdir(path)
    except PermissionError:
        return [], []
    
    folders, files = [], []
    video_ext = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm')
    
    for item in sorted(items):
        if not show_hidden and item.startswith('.'):
            continue
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            folders.append({'name': item, 'path': full_path, 'type': 'folder'})
        elif os.path.isfile(full_path):
            ext = os.path.splitext(item)[1].lower()
            if ext == '.csv':
                files.append({'name': item, 'path': full_path, 'type': 'csv'})
            elif show_videos and ext in video_ext:
                files.append({'name': item, 'path': full_path, 'type': 'video'})
    return folders, files
