"""Utilities for the card maker functionality."""
import base64
import colorsys
import hashlib
import json
import os
import textwrap
from io import BytesIO

from icrawler.builtin import GoogleImageCrawler
from PIL import Image, ImageDraw, ImageFont, ImageOps


def _get_tiled_texture(texture_path, width, height):
    img = Image.new('RGB', (width, height), "black")
    pixels = img.load()
    texture = Image.open(texture_path)
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = texture.getpixel((i % texture.width, j % texture.height))
    return img


def _apply_image_to_background(img, image_path, pad_left=20, pad_top=50, truncate_height=None):
    pixels = img.load()
    image = Image.open(image_path)
    original_width, original_height = image.width, image.height
    new_width = int(img.size[0] - pad_left * 2)
    new_height = int(new_width * original_height / original_width)
    image = image.resize((new_width, new_height))

    for j in range(min(image.height, img.size[1] - pad_top)):
        for i in range(min(image.width, img.size[0] - pad_left)):
            pixels[i + pad_left, j + pad_top] = image.getpixel((i, j))
            if truncate_height is not None and j > truncate_height:
                return img  # stop early
    return img


def _scale_lightness(rgb, scale_l):
    hue, luma, sat = colorsys.rgb_to_hls(*[x / 255 for x in rgb])
    return tuple([int(x * 255) for x in colorsys.hls_to_rgb(hue, min(1, luma * scale_l), s=sat)])


def _draw_borders(img, pad_left=10, pad_top=10, color=(210, 180, 140)):
    draw = ImageDraw.Draw(img)
    y = pad_top
    top_rect_height = 450
    bottom_rect_height = 250
    draw.rounded_rectangle((pad_left, y, img.width - pad_left, top_rect_height), fill=None, outline=color,
                           width=50, radius=10)
    y += top_rect_height + pad_top
    draw.rounded_rectangle((pad_left, y, img.width - pad_left, y + bottom_rect_height), fill=color, outline=color,
                           width=10, radius=10)
    y += bottom_rect_height - pad_top
    pill_width = 100
    pill_height = 50
    pill_color = _scale_lightness(color, 1.5)
    draw.rounded_rectangle((pad_left + pad_left / 2, y, pill_width + pad_left + pad_left / 2, y + pill_height), fill=pill_color, outline=pill_color,
                           width=10, radius=10)
    draw.rounded_rectangle((img.width - (pad_left + pill_width + pad_left / 2), y, img.width - pad_left - pad_left / 2, y + pill_height), fill=pill_color, outline=pill_color,
                           width=10, radius=10)
    return img


def _draw_text(img, color, card):
    draw = ImageDraw.Draw(img)
    title_fnt = ImageFont.truetype("./card_maker_assets/Blankenburg.ttf", 40)
    subtitle_fnt = ImageFont.truetype("./card_maker_assets/Blankenburg.ttf", 25)
    details_fnt = ImageFont.truetype("./card_maker_assets/Montserrat.ttf", 20)
    funfact_fnt = ImageFont.truetype("./card_maker_assets/Montserrat-Italic.ttf", 20)
    pill_fnt = ImageFont.truetype("./card_maker_assets/Blankenburg.ttf", 30)
    draw.text((20, 15), card['name'], fill=color, font=title_fnt)
    draw.text((25, 420), card['type'], fill=color, font=subtitle_fnt)
    draw.multiline_text((30, 485), '\n'.join(textwrap.wrap(card['description'], width=50)), fill=color, stroke_fill=color, font=details_fnt, spacing=20, stroke_width=1)
    draw.line((25, 570, 585, 570), fill=color)
    draw.multiline_text((30, 580), '\n'.join(textwrap.wrap(card['fun-fact'], width=50)), fill=color, stroke_fill=color, font=funfact_fnt, spacing=20, stroke_width=1)
    draw.text((40, 720), str(card['cost']) + 'p', fill=color, font=pill_fnt)
    draw.text((525, 720), 'L' + str(card['level']), fill=color, font=pill_fnt)
    return img


def _apply_alpha(img):
    alpha = ImageOps.invert(Image.open('./card_maker_assets/alpha.png').convert("RGB"))
    img = img.convert('RGBA')
    img.putalpha(alpha.getchannel('R'))
    return img


def _render_card_to_png(c, width=600, height=800, root_texture_asset_path='./card_maker_assets/textures', show=True, save_path=None, prepend_paths=True):
    print(os.listdir())
    texture_path = c['texture']
    if prepend_paths:
        texture_path = os.path.join(root_texture_asset_path, c['texture'])
    img = _get_tiled_texture(texture_path, width, height)
    border_color = img.resize((1, 1)).getpixel((0, 0))
    font_color = (0, 0, 0) if sum([x * s for x, s in zip(border_color, [0.299, 0.587, 0.114])]) <= 0.5 else (255, 255, 255)
    img = _draw_borders(img, color=border_color)
    image_path = c['image']
    if prepend_paths:
        image_path = os.path.join('./card_maker_assets/images', c['image'])
    img = _apply_image_to_background(img, image_path, pad_top=60, truncate_height=350)
    img = _draw_text(img, font_color, c)
    img = _apply_alpha(img)
    # TODO: Add reward if present
    # TODO: Add multi-target icon if present
    if show:
        img.show()
    if save_path is not None:
        img.save(save_path)

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return image_data_to_img_src(img_str)


def render_all_cards(card_data_path='./card_maker_assets/data', output_path='../assets/images'):
    """Render all the cards from JSON.

    Args:
        card_data_path (str, optional): the folder containing card JSON (all JSON is read). Defaults to './card_maker_assets/data'.
        output_path (str, optional): the folder to which to save the card renders. Defaults to '../assets/images'.
    """
    card_paths = os.listdir(card_data_path)
    for card_path in card_paths:
        with open(os.path.join(card_data_path, card_path), 'r', encoding="utf-8") as file_pointer:
            card = json.load(file_pointer)
            _render_card_to_png(card, show=True, save_path=os.path.join(output_path, card['output_name']))


def get_path_from_search(search):
    search_hash = hashlib.sha256(search.encode("utf-8")).hexdigest()
    search_path = './imagesearch/' + str(search_hash)
    return search_path


def _load_images_from_path(path, n_results=None, include_paths=False):
    if n_results is not None:
        files = [os.path.join(path, f) for f in os.listdir(path)][:n_results]
    else:
        files = [os.path.join(path, f) for f in os.listdir(path)]
    b64images = []
    for img_file in files:
        with open(img_file, "rb") as file_pointer:
            encoded_string = base64.b64encode(file_pointer.read())
            b64images.append(encoded_string.decode('utf-8'))
    if include_paths:
        return b64images, files
    else:
        return b64images


def crawl_search(search, n_results=30):
    search_path = get_path_from_search(search)
    existing_image_count = 0
    if os.path.exists(search_path):
        existing_image_count = len(os.listdir(search_path))
    else:
        os.makedirs(search_path)
    google_crawler = GoogleImageCrawler(storage={'root_dir': search_path})
    if existing_image_count != n_results:
        google_crawler.crawl(keyword=search, max_num=n_results, offset=n_results - existing_image_count)
    return _load_images_from_path(search_path, n_results=n_results, include_paths=True)


def image_data_to_img_src(image_data):
    return f"data:image/png;base64,{image_data}"


def search_images(search, n_results=30):
    images, paths = crawl_search(search, n_results=n_results)
    return [image_data_to_img_src(img) for img in images], paths


def load_images_as_b64(path, include_paths=False):
    images, paths = _load_images_from_path(path, include_paths=True)
    images = [image_data_to_img_src(img) for img in images]
    if include_paths:
        return images, paths
    else:
        return images
