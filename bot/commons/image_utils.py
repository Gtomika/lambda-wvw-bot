import cv2


def shift_image_from_center_point(image, center):
    """
    Find the top left coordinate of the image, given the center point.
    """
    center_x = center[0]
    center_y = center[1]

    image_width = image.shape[0]
    image_height = image.shape[1]

    return [center_x - int(image_width/2), center_y - int(image_height/2)]


def overlay_image_at_point(image, overlay_image, point):
    """
    Modify the 'image' in such a way that 'overlay_image' is placed over it at the specified point.
    Transparency is handled.
    """
    x1 = point[1]
    y1 = point[0]
    x2 = x1 + overlay_image.shape[1]
    y2 = y1 + overlay_image.shape[0]

    alpha_overlay_image = overlay_image[:, :, 3] / 255.0
    alpha_image = 1.0 - alpha_overlay_image

    for c in range(0, 3):
        image[y1:y2, x1:x2, c] = (alpha_overlay_image * overlay_image[:, :, c] + alpha_image * image[y1:y2, x1:x2, c])


