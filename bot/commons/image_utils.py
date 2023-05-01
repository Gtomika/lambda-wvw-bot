from PIL import Image


class Coordinate:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_tuple(self) -> tuple[int, int]:
        return self.x, self.y


def load_image_rgba(file_name: str) -> Image:
    """
    Load an RGBA image.
    """
    img = Image.open(file_name)
    img = img.convert('RGBA')
    print(f'Image opened: {file_name}. Mode: {img.mode}')
    return img


def save_image_png(image: Image, file_name: str):
    """
    Save an image as PNG.
    """
    if not file_name.endswith('.png'):
        raise Exception(f'File should be a png but was {file_name}')
    image.save(file_name)


def save_image_jpg(image: Image, file_name: str):
    """
    Save an image as JPEG.
    """
    if not file_name.endswith('.jpg'):
        raise Exception(f'File should be a jpg but was {file_name}')
    image = image.convert('RGB')
    image.save(file_name)


def gw2_api_coordinates_to_pixels(
        wvw_map,
        map_image: Image,
        gw2_api_objective_coordinates: Coordinate,
) -> Coordinate:
    """
    Core method to convert WvW objective coordinates received from the GW2 API to
    pixel coordinates of the given image.
    """
    relative_coordinates = wvw_map.relative_gw2_api_coordinate(gw2_api_objective_coordinates)

    pixels_x = (relative_coordinates.x * map_image.width) / wvw_map.width_gw2_api()
    pixels_y = (relative_coordinates.y * map_image.height) / wvw_map.height_gw2_api()

    return Coordinate(int(pixels_x), int(pixels_y))


def shift_image_from_center_point(image: Image, center: Coordinate) -> Coordinate:
    """
    Find the top left coordinate of the image, given the center point.
    """
    image_width = image.width
    image_height = image.height

    return Coordinate(center.x - int(image_width/2), center.y - int(image_height/2))


def place_image_to_point(image: Image, overlay_image: Image, point: Coordinate):
    """
    Modify the 'image' in such a way that 'overlay_image' is placed over it at the specified point.
    """
    image.paste(overlay_image, point.as_tuple(), overlay_image)  # 3. parameter ensures transparency is kept


