import StringIO

import PIL.Image


def bytes_to_image(raw_bytes):
    fakefile = StringIO.StringIO(raw_bytes)
    return PIL.Image.open(fakefile)
