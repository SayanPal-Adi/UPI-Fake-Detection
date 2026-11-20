from detection.image_preprocessor import ImagePreprocessor

print("Starting image preprocessing test...")

image_path = "uploads/test.png"

try:
    result = ImagePreprocessor.preprocess(image_path)

    print("\nSUCCESS: Image preprocessing completed!")
    print("Width:", result["width"])
    print("Height:", result["height"])
    print("Original:", result["original"].shape)
    print("Grayscale:", result["grayscale"].shape)
    print("Enhanced:", result["enhanced"].shape)

except Exception as error:
    print("ERROR:", error)