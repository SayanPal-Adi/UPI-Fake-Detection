
import json

from detection.region_matcher import RegionMatcher


IMAGE_PATH = "uploads/test.jpg"

try:
    print("\nStarting region-based comparison...")

    result = RegionMatcher.analyze(IMAGE_PATH)

    print("\n========== REGION MATCHING RESULTS ==========")

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\nRegion matching test passed!")

except Exception as error:
    print("\nREGION MATCHING ERROR:", error)
