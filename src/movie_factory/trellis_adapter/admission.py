"""Prepared-alpha admission only. No automatic segmentation or downloads."""
import numpy as np
from PIL import Image


def prepare_rgba(image):
    if not isinstance(image, Image.Image) or image.mode != 'RGBA':
        raise ValueError('Prepared RGBA image required; background removal disabled')
    alpha = np.asarray(image)[:, :, 3]
    if np.all(alpha == 255):
        raise ValueError('Opaque alpha is not a prepared foreground mask')
    if not np.any(alpha > 204):
        raise ValueError('No sufficiently opaque foreground')
    scale = min(1, 1024 / max(image.size))
    if scale < 1:
        image = image.resize((max(1, int(image.width*scale)), max(1, int(image.height*scale))), Image.Resampling.LANCZOS)
    arr = np.asarray(image)
    yy, xx = np.where(arr[:, :, 3] > 204)
    if not len(xx):
        raise ValueError('Foreground disappears at admitted resolution')
    # Inclusive bounds: retain last row/column; avoid upstream one-pixel empty crop.
    side = max(int(xx.max()-xx.min()+1), int(yy.max()-yy.min()+1))
    left = int((int(xx.min())+int(xx.max())+1-side)//2)
    top = int((int(yy.min())+int(yy.max())+1-side)//2)
    crop = np.asarray(image.crop((left, top, left+side, top+side))).astype(np.float32)/255
    return Image.fromarray((crop[:, :, :3]*crop[:, :, 3:4]*255).astype(np.uint8))
