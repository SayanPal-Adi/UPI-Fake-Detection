
import cv2
import numpy as np


class PixelAnalyzer:

    @staticmethod
    def analyze(image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Unable to load image.")

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # 1. Calculate local contrast
        local_mean = cv2.blur(
            gray.astype(np.float32),
            (15, 15)
        )

        local_squared_mean = cv2.blur(
            gray.astype(np.float32) ** 2,
            (15, 15)
        )

        local_variance = np.maximum(
            local_squared_mean - local_mean ** 2,
            0
        )

        local_contrast = np.sqrt(local_variance)

        # 2. Calculate edge density
        edges = cv2.Canny(
            gray,
            100,
            200
        )

        edge_density = (
            np.count_nonzero(edges) / edges.size
        ) * 100

        # 3. Calculate image sharpness
        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F
        )

        sharpness = float(
            laplacian.var()
        )

        # 4. Divide image into regions
        height, width = gray.shape

        rows = 4
        columns = 3

        region_results = []

        for row in range(rows):
            for column in range(columns):

                y1 = row * height // rows
                y2 = (row + 1) * height // rows

                x1 = column * width // columns
                x2 = (column + 1) * width // columns

                region = gray[y1:y2, x1:x2]

                if region.size == 0:
                    continue

                region_laplacian = cv2.Laplacian(
                    region,
                    cv2.CV_64F
                )

                region_sharpness = float(
                    region_laplacian.var()
                )

                region_contrast = float(
                    region.std()
                )

                region_results.append({
                    "region": f"row_{row + 1}_col_{column + 1}",
                    "sharpness": round(region_sharpness, 2),
                    "contrast": round(region_contrast, 2)
                })

        return {
            "method": "Pixel and Edge Analysis",
            "image_width": width,
            "image_height": height,
            "overall_sharpness": round(sharpness, 2),
            "overall_edge_density": round(edge_density, 2),
            "average_local_contrast": round(
                float(np.mean(local_contrast)),
                2
            ),
            "regions_analyzed": len(region_results),
            "region_details": region_results,
            "risk_signal": "Requires comparison with reference images",
            "assessment_note": (
                "Pixel and edge statistics alone cannot establish "
                "whether text or image regions have been manipulated."
            )
        }
