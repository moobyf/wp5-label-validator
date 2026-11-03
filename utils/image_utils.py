"""Image loading and caching utilities."""
import os
import base64
import threading
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image

image_cache = {}
cache_lock = threading.Lock()
prefetch_executor = ThreadPoolExecutor(max_workers=3)


def get_cached_image(image_path, root_dir):
    cache_key = image_path
    with cache_lock:
        if cache_key in image_cache:
            return image_cache[cache_key]
    
    full_path = os.path.join(root_dir, image_path) if not os.path.isabs(image_path) else image_path
    if not os.path.exists(full_path):
        return None
    
    try:
        with Image.open(full_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error loading image {full_path}: {e}")
        return None
    
    with cache_lock:
        if len(image_cache) > 30:
            keys_to_remove = list(image_cache.keys())[:10]
            for k in keys_to_remove:
                del image_cache[k]
        image_cache[cache_key] = img_data
    return img_data


def prefetch_images(image_list, current_index, root_dir, count=5):
    def load_image(path):
        get_cached_image(path, root_dir)
    for i in range(current_index + 1, min(current_index + count + 1, len(image_list))):
        prefetch_executor.submit(load_image, image_list[i])


def clear_cache():
    with cache_lock:
        image_cache.clear()


def invalidate_cache_entry(image_path):
    with cache_lock:
        if image_path in image_cache:
            del image_cache[image_path]
