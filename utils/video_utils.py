"""Video frame extraction utilities."""
import os
import re
import base64
from io import BytesIO

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from PIL import Image


def extract_video_info_from_crop_path(crop_path):
    """
    Extract video name and frame number from crop filename.
    Supports multiple formats:
    - Manual crop: F{frame}_D{detection}_{video}.jpg
    - Pipeline crop: {video}_F{frame}_{detection}.jpg  (e.g. MOOBYF_FT2_GX013499_F0_1.jpg)
      also with the '_1', '_1_1' suffixes added when a crop is moved onto an existing name
    - YOLO native: {video}_{frame}.jpg
    """
    # Accept both '/' and '\' separators (CSVs written on Windows use '\')
    basename = re.split(r'[\\/]', str(crop_path))[-1]
    name_without_ext = os.path.splitext(basename)[0]

    # Format 1: Manual crop - F{frame}_D{detection}_{video}.jpg
    match = re.match(r'F(\d+)_D\d+_(.+)', name_without_ext, re.IGNORECASE)
    if match:
        return match.group(2), int(match.group(1))

    # Format 2: Pipeline crop - {video}_F{frame}_{detection}[_1[_1...]].jpg
    match = re.match(r'^(.+)_F(\d+)_\d+(?:_\d+)*$', name_without_ext)
    if match:
        return match.group(1), int(match.group(2))

    # Format 3: YOLO native - {video}_{frame}.jpg
    # Split from the right to get the frame number
    parts = name_without_ext.rsplit('_', 1)
    if len(parts) == 2:
        video_name = parts[0]
        frame_part = parts[1]
        try:
            frame_num = int(frame_part)
            return video_name, frame_num
        except ValueError:
            pass
    
    return None, None


def find_video_file(video_name, videos_dir):
    if not videos_dir or not os.path.isdir(videos_dir):
        return None
    extensions = ['.mp4', '.MP4', '.avi', '.AVI', '.mov', '.MOV', '.mkv', '.MKV']
    for ext in extensions:
        video_path = os.path.join(videos_dir, video_name + ext)
        if os.path.exists(video_path):
            return video_path
    for root, dirs, files in os.walk(videos_dir):
        for f in files:
            if os.path.splitext(f)[0] == video_name:
                return os.path.join(root, f)
    return None


def extract_frame_from_video(video_path, frame_num):
    if not CV2_AVAILABLE:
        return None
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
        return None
    except Exception as e:
        print(f"Error extracting frame: {e}")
        return None


def get_frame_with_bbox(video_path, frame_num, bbox, label="", color=(0, 255, 0), thickness=3):
    if not CV2_AVAILABLE:
        return None
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        x_min, y_min, x_max, y_max = bbox
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Error processing frame: {e}")
        return None


def get_video_info(video_path):
    if not CV2_AVAILABLE:
        return None
    try:
        cap = cv2.VideoCapture(video_path)
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        }
        cap.release()
        return info
    except:
        return None
