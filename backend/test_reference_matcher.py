import json

from detection.reference_matcher import ReferenceMatcher


IMAGE_PATH = "uploads/test.jpg"

try:
    print("\nStarting reference comparison...")

    result = ReferenceMatcher.analyze(
        IMAGE_PATH
    )

    print("\n========== REFERENCE MATCHING RESULTS ==========")

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\nReference matching test passed!")

except Exception as error:
    print("\nREFERENCE MATCHING ERROR:", error)