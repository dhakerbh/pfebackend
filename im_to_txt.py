#TEXT EXTRACTOR FROM IMAGE
from paddleocr import PaddleOCR

def get_text_from_image(path):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(path, cls=False)
    text=""
    for line in result[0]:
        text+=f"{line[1][0]}\n"
    return text