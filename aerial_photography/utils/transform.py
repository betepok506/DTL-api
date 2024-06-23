from PIL import Image


def convert_tif2img(img):
    image = Image.fromarray(img)
    red, green, blue = image.split()

    image = Image.merge('RGB', (blue, green, red))
    return image
