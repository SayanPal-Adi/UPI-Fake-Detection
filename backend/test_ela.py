
import json

from detection.ela_detector import ELADetector


IMAGE_PATH = "uploads/test.jpg"

try:
    print("\nStarting ELA analysis...")

    result = ELADetector.analyze(IMAGE_PATH)

    print("\n========== ELA ANALYSIS ==========")
    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\nELA module executed successfully!")

except Exception as error:
    print("\nELA ERROR:", error)
