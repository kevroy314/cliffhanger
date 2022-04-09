import qrcode
import uuid
import os

def generate_qr_object(encode_string, encode_filepath):
    if not os.path.exists(encode_filepath):
        img = qrcode.make(encode_string)
        img.save(encode_filepath)