
import json

from detection.pixel_analyzer import PixelAnalyzer


IMAGE_PATH = "uploads/test.jpg"

try:
    print("\nStarting pixel analysis...")

    result = PixelAnalyzer.analyze(IMAGE_PATH)

    print("\n========== PIXEL ANALYSIS ==========")
    print(json.dumps(result, indent=4))

    print("\nPixel analysis test passed!")

except Exception as error:
    print("\nPIXEL ANALYSIS ERROR:", error)
