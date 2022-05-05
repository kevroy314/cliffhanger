"""QR Code Generation."""
import os

import qrcode


def generate_qr_object(encode_string, encode_filepath):
    """Generate a QR code from a string and save it in the server.

    Args:
        encode_string (str): the string to encode
        encode_filepath (str): the place to save the QR code
    """
    if not os.path.exists(encode_filepath):
        img = qrcode.make(encode_string)
        img.save(encode_filepath)
