from repolya._const import PAPER_PDFIMGS
from repolya._log import logger_paper

import fitz
import os
import io
from PIL import Image


min_width = 120
min_height = 120


def get_imgs_from_pdf(_fp):
    _f = os.path.basename(_fp)
    logger_paper.info(f"{_f}")
    _fn, _ext = os.path.splitext(_f)
    _pdf = fitz.open(_fp)
    out_dir = PAPER_PDFIMGS / _fn
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # Iterate over PDF pages
    for page_index in range(len(_pdf)):
        # Get the page itself
        page = _pdf[page_index]
        # Get image list
        img_list = page.get_images(full=True)
        # Print the number of images found on this page
        if img_list:
            logger_paper.info(f"[+] Found a total of {len(img_list)} images in page {page_index}")
        else:
            logger_paper.info(f"[!] No images found on page {page_index}")
        # Iterate over the images on the page
        for img_index, img in enumerate(img_list, start=1):
            # Get the XREF of the image
            xref = img[0]
            # Extract the image bytes
            base_img = _pdf.extract_image(xref)
            img_bytes = base_img["image"]
            # Get the image extension
            img_ext = base_img["ext"]
            #Generate image file name
            img_name = f"{_fn}_pg{page_index}_img{img_index}.{img_ext}"
            # Load it to PIL
            image = Image.open(io.BytesIO(img_bytes))
            # Check if the image meets the minimum dimensions and save it
            if image.width >= min_width and image.height >= min_height:
                image.save(
                    open(os.path.join(out_dir, img_name), "wb"),
                    format=img_ext
                )
            else:
                logger_paper.info(f"[-] Skipping image {img_index} on page {page_index} due to its small size.")

