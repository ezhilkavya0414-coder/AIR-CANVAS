import cv2
import numpy as np

from modules.ocr import read_text_from_canvas


# Create white canvas
canvas = np.ones(
    (400, 800, 3),
    dtype=np.uint8
) * 255


# Write test equation
cv2.putText(
    canvas,
    "3x - 7 = 14",
    (50, 200),
    cv2.FONT_HERSHEY_SIMPLEX,
    2,
    (0, 0, 0),
    4
)


# OCR
text = read_text_from_canvas(canvas)


print("--------------------------------")
print("OCR RESULT")
print("--------------------------------")
print(text)
print("--------------------------------")
