
import time

from detection.image_preprocessor import ImagePreprocessor
from detection.ocr_engine import OCREngine
from detection.app_identifier import UPIAppIdentifier
from detection.anomaly_detector import AnomalyDetector
from detection.ela_detector import ELADetector
from detection.pixel_analyzer import PixelAnalyzer


class UPIAnalyzer:

    @staticmethod
    def analyze_image(image_path):

        start_time = time.perf_counter()

        # STEP 1: Image preprocessing
        image_data = ImagePreprocessor.preprocess(image_path)

        # STEP 2: OCR text extraction
        extracted_text = OCREngine.extract_text(
            image_data["enhanced"]
        )

        # STEP 3: Transaction detail extraction
        transaction_details = OCREngine.extract_details(
            extracted_text
        )

        # STEP 4: UPI application identification
        app_result = UPIAppIdentifier.identify(
            extracted_text
        )

        # STEP 5: Preliminary anomaly analysis
        anomaly_result = AnomalyDetector.analyze(
            app_result,
            transaction_details
        )

        # STEP 6: Error Level Analysis
        ela_result = ELADetector.analyze(image_path)

        # STEP 7: Pixel and edge analysis
        pixel_result = PixelAnalyzer.analyze(image_path)

        # STEP 8: Processing time
        processing_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        # STEP 9: Final result
        result = {
            "project": "UPI Shield",
            "status": "Analysis completed",

            "app_identification": app_result,

            "transaction_details": transaction_details,

            "fraud_analysis": anomaly_result,

            "ela_analysis": ela_result,

            "pixel_analysis": pixel_result,

            "image_information": {
                "width": image_data["width"],
                "height": image_data["height"]
            },

            "processing_time_ms": processing_time,

            "extracted_text": extracted_text
        }

        return result
