
import os
import cv2
import numpy as np


class ELADetector:

    JPEG_EXTENSIONS = {".jpg", ".jpeg"}

    @staticmethod
    def analyze(image_path):

        extension = os.path.splitext(image_path)[1].lower()

        # ELA is primarily intended for JPEG images
        if extension not in ELADetector.JPEG_EXTENSIONS:
            return {
                "available": False,
                "method": "Error Level Analysis",
                "reason": (
                    "ELA is currently supported only for JPEG images. "
                    "PNG images do not retain JPEG compression history."
                ),
                "risk_signal": "Not assessed"
            }

        # Load original image
        original = cv2.imread(image_path)

        if original is None:
            raise ValueError("Unable to load image for ELA analysis.")

        # Recompress image at a fixed JPEG quality
        success, encoded_image = cv2.imencode(
            ".jpg",
            original,
            [cv2.IMWRITE_JPEG_QUALITY, 90]
        )

        if not success:
            raise ValueError("JPEG recompression failed.")

        recompressed = cv2.imdecode(
            encoded_image,
            cv2.IMREAD_COLOR
        )

        # Calculate pixel differences
        difference = cv2.absdiff(
            original,
            recompressed
        )

        # Convert difference into grayscale
        difference_gray = cv2.cvtColor(
            difference,
            cv2.COLOR_BGR2GRAY
        )

        # Calculate image statistics
        mean_error = float(np.mean(difference_gray))
        max_error = int(np.max(difference_gray))

        # Highlight differences for visualization
        ela_visualization = cv2.normalize(
            difference_gray,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        # Calculate percentage of high-error pixels
        threshold = 30

        suspicious_pixels = np.count_nonzero(
            difference_gray > threshold
        )

        total_pixels = difference_gray.size

        suspicious_region_ratio = round(
            (suspicious_pixels / total_pixels) * 100,
            2
        )

        # Do not classify an image as fake using ELA alone
        return {
            "available": True,
            "method": "Error Level Analysis",
            "mean_error": round(mean_error, 2),
            "maximum_error": max_error,
            "high_difference_pixel_ratio": suspicious_region_ratio,
            "visualization": "ELA difference image generated",
            "risk_signal": "Requires further analysis",
            "assessment_note": (
                "Compression differences are not proof of manipulation. "
                "Interpret ELA alongside other forensic signals."
            )
        }

    @staticmethod
    def save_visualization(image_path, output_path):

        extension = os.path.splitext(image_path)[1].lower()

        if extension not in ELADetector.JPEG_EXTENSIONS:
            raise ValueError(
                "ELA visualization is currently supported only for JPEG images."
            )

        original = cv2.imread(image_path)

        if original is None:
            raise ValueError("Unable to load original image.")

        success, encoded_image = cv2.imencode(
            ".jpg",
            original,
            [cv2.IMWRITE_JPEG_QUALITY, 90]
        )

        if not success:
            raise ValueError("JPEG recompression failed.")

        recompressed = cv2.imdecode(
            encoded_image,
            cv2.IMREAD_COLOR
        )

        difference = cv2.absdiff(
            original,
            recompressed
        )

        difference_gray = cv2.cvtColor(
            difference,
            cv2.COLOR_BGR2GRAY
        )

        visualization = cv2.normalize(
            difference_gray,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        saved = cv2.imwrite(
            output_path,
            visualization
        )

        if not saved:
            raise ValueError("Unable to save ELA visualization.")

        return output_path
