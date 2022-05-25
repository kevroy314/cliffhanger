import os
import argparse
import torch
from PIL import Image, ImageFile
from net import Net
from utils import DEVICE, test_transform
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
Image.MAX_IMAGE_PIXELS = None  
ImageFile.LOAD_TRUNCATED_IMAGES = True

    
def transfer_style(content_image, style_image):
    if not os.path.exists("./checkpoints"): # TODO: Test uncomrpess logic
        os.makedirs("./checkpoints")
        os.system("cde ./checkpoints & cat ../checkpoints_compressed/x* | tar xz")
    default_args = argparse.Namespace(pretrained=True, requires_grad=True, training=False, model_dir="./checkpoints")
    model = Net(default_args)
    model.eval()
    model = model.to(DEVICE)
    
    tf = test_transform()

    Ic = tf(content_image).to(DEVICE)
    Is = tf(style_image).to(DEVICE)

    Ic = Ic.unsqueeze(dim=0)
    Is = Is.unsqueeze(dim=0)
    
    with torch.no_grad():
        Ics = model(Ic, Is)

    img = Ics[0]
    img = img.cpu().numpy()
    img = np.moveaxis(img, 0, -1)
    img = Image.fromarray(np.uint8(img*255))
    return img

if __name__ == "__main__":
    content_image = Image.fromarray(mpimg.imread('content.jpg'))
    style_image = Image.fromarray(mpimg.imread('style.jpg'))

    img = transfer_style(content_image, style_image)
    
    plt.imshow(img)
    plt.show()