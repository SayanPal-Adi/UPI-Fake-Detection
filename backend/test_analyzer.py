import json
from detection.analyzer import UPIAnalyzer

IMAGE_PATH = "uploads/test.jpg"

try:
    print("\nStarting UPI Shield analysis...")

    result = UPIAnalyzer.analyze_image(IMAGE_PATH)

    print("\n========== COMPLETE ANALYSIS ==========")
    print(json.dumps(result, indent=4, ensure_ascii=False))

    print("\n========== PIPELINE TEST ==========")
    print("Pipeline executed successfully!")
    print("Processing time:", result["processing_time_ms"], "ms")

except Exception as error:
    print("\nPIPELINE ERROR:", error)