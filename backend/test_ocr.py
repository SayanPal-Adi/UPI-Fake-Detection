
from detection.image_preprocessor import ImagePreprocessor
from detection.ocr_engine import OCREngine


image_path = "uploads/test.png"

try:

    print("\nStarting OCR test...")

    # Step 1: Preprocess image
    image_data = ImagePreprocessor.preprocess(
        image_path
    )

    # Step 2: Extract text
    extracted_text = OCREngine.extract_text(
        image_data["enhanced"]
    )

    # Step 3: Extract transaction details
    details = OCREngine.extract_details(
        extracted_text
    )

    print("\n========== EXTRACTED TEXT ==========")
    print(extracted_text)

    print("\n========== TRANSACTION DETAILS ==========")

    for key, value in details.items():
        print(f"{key}: {value}")

    print("\nOCR TEST COMPLETED!")

except Exception as error:

    print("OCR ERROR:", error)
