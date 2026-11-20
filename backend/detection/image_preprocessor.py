
import cv2
import numpy as np


class ImagePreprocessor:

    MAX_DIMENSION = 1600
    MIN_DIMENSION = 100

    @staticmethod
    def load_image(image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Invalid or unreadable image")

        height, width = image.shape[:2]

        if width < ImagePreprocessor.MIN_DIMENSION:
            raise ValueError("Image width is too small")

        if height < ImagePreprocessor.MIN_DIMENSION:
            raise ValueError("Image height is too small")

        return image

    @staticmethod
    def resize_image(image):

        height, width = image.shape[:2]

        scale = min(
            ImagePreprocessor.MAX_DIMENSION / width,
            ImagePreprocessor.MAX_DIMENSION / height,
            1.0
        )

        if scale < 1.0:

            new_width = int(width * scale)
            new_height = int(height * scale)

            image = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA
            )

        return image

    @staticmethod
    def convert_to_grayscale(image):

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    @staticmethod
    def enhance_image(gray_image):

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        return clahe.apply(gray_image)

    @staticmethod
    def preprocess(image_path):

        original = ImagePreprocessor.load_image(
            image_path
        )

        resized = ImagePreprocessor.resize_image(
            original
        )

        grayscale = ImagePreprocessor.convert_to_grayscale(
            resized
        )

        enhanced = ImagePreprocessor.enhance_image(
            grayscale
        )

        return {
            "original": resized,
            "grayscale": grayscale,
            "enhanced": enhanced,
            "width": resized.shape[1],
            "height": resized.shape[0]
        }
