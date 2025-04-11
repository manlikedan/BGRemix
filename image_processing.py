# image_processing.py

import os
import random
from rembg import remove, new_session
from PIL import Image, ImageEnhance, ImageFilter
from tqdm import tqdm

# --- THEMES ---
themes = {
    'pastel': [
        (255, 209, 220), (174, 198, 207), (202, 231, 225),
        (255, 253, 208), (255, 179, 186), (186, 255, 201),
        (241, 222, 232), (221, 245, 255), (255, 235, 205)
    ],
    'neon': [
        (57, 255, 20), (255, 20, 147), (0, 255, 255),
        (255, 255, 0), (255, 105, 180), (0, 255, 127),
        (255, 0, 255), (0, 255, 180)
    ],
    'brand': [
        (40, 166, 222), (0, 0, 0), (255, 255, 255),
        (255, 51, 102), (102, 204, 255)
    ],
    'grey': [
        (240, 240, 240), (200, 200, 200), (220, 220, 220),
        (180, 180, 180), (160, 160, 160)
    ],
    'earth': [
        (189, 183, 107), (139, 69, 19), (107, 142, 35),
        (205, 133, 63), (222, 184, 135)
    ],
    'retro': [
        (255, 105, 97), (255, 179, 71), (253, 253, 150),
        (119, 221, 119), (119, 158, 203), (203, 153, 201)
    ],
    'random': []
}

def random_color():
    return tuple(random.randint(100, 255) for _ in range(3))

def random_theme_color(theme_name='pastel'):
    return random.choice(themes.get(theme_name, [(255, 255, 255)]))

def add_padding(img, padding_percent):
    if padding_percent <= 0:
        return img
    width, height = img.size
    padding_w = int(width * padding_percent / 100)
    padding_h = int(height * padding_percent / 100)
    new_width = width + 2 * padding_w
    new_height = height + 2 * padding_h
    padded_img = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    padded_img.paste(img, (padding_w, padding_h))
    return padded_img

def autocrop(img, threshold=10):
    """
    Crop all transparent edges from the image, with a threshold for transparency.
    Pixels with alpha value below the threshold will be considered "transparent".
    """
    img = img.convert("RGBA")
    img_data = img.load()

    left, top, right, bottom = img.width, img.height, 0, 0

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img_data[x, y]
            if a >= threshold:
                if x < left:
                    left = x
                if x > right:
                    right = x
                if y < top:
                    top = y
                if y > bottom:
                    bottom = y

    if left > right or top > bottom:
        # no non-transparent pixels, return original
        return img

    return img.crop((left, top, right + 1, bottom + 1))

def fit_image(img, target_size):
    """
    Resize image to fit entirely inside target_size, maximizing size without overflow.
    """
    img_ratio = img.width / img.height
    target_width, target_height = target_size
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        scale_factor = target_width / img.width
    else:
        scale_factor = target_height / img.height

    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    resized_img = img.resize(new_size, Image.LANCZOS)
    return resized_img

def soft_despill(img, bg_color=(255, 255, 255)):
    img = img.convert('RGBA')
    pixels = img.load()
    bg_r, bg_g, bg_b = bg_color
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if 0 < a < 255:
                alpha_factor = a / 255.0
                new_r = int(r / alpha_factor - bg_r * (1 - alpha_factor))
                new_g = int(g / alpha_factor - bg_g * (1 - alpha_factor))
                new_b = int(b / alpha_factor - bg_b * (1 - alpha_factor))
                pixels[x, y] = (
                    max(0, min(255, new_r)),
                    max(0, min(255, new_g)),
                    max(0, min(255, new_b)),
                    a
                )
    return img

def boost_alpha(img, factor=1.5):
    img = img.convert('RGBA')
    r, g, b, a = img.split()
    a = a.point(lambda p: min(255, int(p * factor)))
    return Image.merge('RGBA', (r, g, b, a))

def lighten_alpha(img, blur_radius=1):
    img = img.convert('RGBA')
    r, g, b, a = img.split()
    a = a.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return Image.merge('RGBA', (r, g, b, a))

def clean_edges(img, bg_color=(255, 255, 255)):
    img = img.convert('RGBA')
    r, g, b, a = img.split()
    solid_bg = Image.new('RGBA', img.size, bg_color + (255,))
    solid_bg.paste(img, mask=a)
    return solid_bg

def extract_alpha(image):
    """Extract the alpha channel from an RGBA image."""
    return image.split()[-1]

def merge_masks(masks):
    """Merge multiple alpha masks by taking maximum alpha value at each pixel."""
    width, height = masks[0].size
    merged = Image.new('L', (width, height))
    merged_pixels = merged.load()
    masks_pixels = [m.load() for m in masks]

    for y in range(height):
        for x in range(width):
            alphas = [p[x, y] for p in masks_pixels]
            max_alpha = max(alphas)
            merged_pixels[x, y] = max_alpha

    return merged

def apply_mask(original_img, mask):
    """Apply a mask to the original image."""
    original_img = original_img.convert('RGBA')
    r, g, b, _ = original_img.split()
    return Image.merge('RGBA', (r, g, b, mask))

def clean_small_white_areas(img, threshold=253):
    """
    Make almost pure white areas fully transparent.
    Be very strict to protect light gray products.
    """
    img = img.convert('RGBA')
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a > 0 and r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (r, g, b, 0)  # Fully transparent

    return img

def feather_edges(img, radius=2):
    """
    Feather (blur) the alpha channel to soften edges.
    """
    img = img.convert('RGBA')
    r, g, b, a = img.split()

    # Apply a Gaussian Blur to the alpha channel only
    a = a.filter(ImageFilter.GaussianBlur(radius=radius))

    # Recombine channels
    return Image.merge('RGBA', (r, g, b, a))

def remove_background(
    input_image,
    models_to_use=None,
    original_bg_color=(255, 255, 255),
    soft_despill_enabled=True,
    boost_alpha_factor=1.5,
    lighten_alpha_radius=1,
    threshold_white_areas=245,
    feather_edges_radius=0
):
    """
    Main function that removes the background using one or more models.
    Returns the cutout image (RGBA).
    """
    if models_to_use is None:
        models_to_use = ['isnet-general-use']

    # --- Run through models to get masks ---
    masks = []
    for model in models_to_use:
        session = new_session(model_name=model)
        cutout_temp = remove(input_image, session=session)
        alpha = extract_alpha(cutout_temp)
        masks.append(alpha)

    # Merge masks
    merged_mask = merge_masks(masks)

    # Apply merged mask to original image
    cutout = apply_mask(input_image, merged_mask)
    cutout = clean_small_white_areas(cutout, threshold=threshold_white_areas)

    # Autocrop
    cutout = autocrop(cutout)

    # Optional post-processing
    if soft_despill_enabled:
        cutout = soft_despill(cutout, bg_color=original_bg_color)

    if boost_alpha_factor > 0:
        cutout = boost_alpha(cutout, factor=boost_alpha_factor)

    if lighten_alpha_radius > 0:
        cutout = lighten_alpha(cutout, blur_radius=lighten_alpha_radius)

    if feather_edges_radius > 0:
            cutout = feather_edges(cutout, radius=feather_edges_radius)

    return cutout

def finalize_image(
    cutout,
    padding_percentage=15,
    background_mode='random',
    theme='pastel',
    fixed_background_color=(255, 255, 255),
    output_size=(1200, 1200),
    save_as_jpg=False
):
    """
    Apply padding, choose background color, and paste cutout onto background of given size.
    Returns a Pillow Image object with final result.
    """
    # Add padding
    cutout = add_padding(cutout, padding_percentage)

    # Decide background color
    if background_mode == 'random':
        bg_color = random_color()
    elif background_mode == 'fixed':
        bg_color = fixed_background_color
    elif background_mode in themes:
        bg_color = random.choice(themes[background_mode])
    elif background_mode == 'transparent':
        bg_color = (0, 0, 0, 0)
    else:
        bg_color = (255, 255, 255)

    # Clean edges
    cutout = clean_edges(cutout, bg_color=bg_color)

    # Create final background
    width, height = output_size
    background = Image.new('RGBA', (width, height), bg_color)
    fitted_image = fit_image(cutout, (width, height))
    x = (background.width - fitted_image.width) // 2
    y = (background.height - fitted_image.height) // 2
    background.paste(fitted_image, (x, y), fitted_image)

    if save_as_jpg:
        background = background.convert('RGB')

    return background
