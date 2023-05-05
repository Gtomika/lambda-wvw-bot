import pathlib
from bot.commons import image_utils


original_size = 64
updated_size = 128


img_dir = pathlib.Path(__file__).parent.resolve()
for img_path in img_dir.glob("*.png"):
    img = image_utils.load_image_rgba(img_path.as_posix())
    if img.width == original_size and img.height == original_size:
        resized_img = img.resize((updated_size, updated_size))
        image_utils.save_image_png(resized_img, img_path.as_posix())
