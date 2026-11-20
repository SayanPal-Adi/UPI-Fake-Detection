
import os
import cv2
import numpy as np

from skimage.metrics import structural_similarity


class ReferenceMatcher:

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    REFERENCE_DIR = os.path.join(
        BASE_DIR,
        "reference_data"
    )

    TARGET_SIZE = (256, 512)

    SUPPORTED_EXTENSIONS = {
        ".jpg", ".jpeg", ".png"
    }

    APPS = [
        "google_pay",
        "phonepe",
        "paytm"
    ]

    CATEGORIES = [
        "genuine",
        "manipulated"
    ]

    @staticmethod
    def prepare_image(image):

        if image is None:
            raise ValueError("Invalid image.")

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        target_width, target_height = (
            ReferenceMatcher.TARGET_SIZE
        )

        height, width = gray.shape

        scale = min(
            target_width / width,
            target_height / height
        )

        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))

        resized = cv2.resize(
            gray,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

        canvas = np.zeros(
            (target_height, target_width),
            dtype=np.uint8
        )

        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2

        canvas[
            y_offset:y_offset + new_height,
            x_offset:x_offset + new_width
        ] = resized

        return canvas

    @staticmethod
    def extract_features(image):

        # Structural similarity representation
        gray = image

        # Edge representation
        edges = cv2.Canny(
            gray,
            60,
            150
        )

        return {
            "gray": gray,
            "edges": edges
        }

    @staticmethod
    def compare_features(upload_features, reference_features):

        ssim_score = structural_similarity(
            upload_features["gray"],
            reference_features["gray"],
            data_range=255
        )

        edge_score = structural_similarity(
            upload_features["edges"],
            reference_features["edges"],
            data_range=255
        )

        combined_score = (
            0.65 * ssim_score +
            0.35 * edge_score
        )

        return {
            "ssim": round(
                max(0, ssim_score) * 100,
                2
            ),
            "edge_similarity": round(
                max(0, edge_score) * 100,
                2
            ),
            "combined_similarity": round(
                max(0, combined_score) * 100,
                2
            )
        }

    @staticmethod
    def load_references():

        references = []

        for app in ReferenceMatcher.APPS:

            for category in ReferenceMatcher.CATEGORIES:

                folder = os.path.join(
                    ReferenceMatcher.REFERENCE_DIR,
                    app,
                    category
                )

                if not os.path.isdir(folder):
                    continue

                for filename in os.listdir(folder):

                    extension = os.path.splitext(
                        filename
                    )[1].lower()

                    if extension not in (
                        ReferenceMatcher.SUPPORTED_EXTENSIONS
                    ):
                        continue

                    image_path = os.path.join(
                        folder,
                        filename
                    )

                    image = cv2.imread(image_path)

                    if image is None:
                        continue

                    prepared = ReferenceMatcher.prepare_image(
                        image
                    )

                    references.append({
                        "app": app,
                        "category": category,
                        "filename": filename,
                        "features": ReferenceMatcher.extract_features(
                            prepared
                        )
                    })

        return references

    @staticmethod
    def analyze(image_path):

        uploaded_image = cv2.imread(image_path)

        if uploaded_image is None:
            raise ValueError(
                "Unable to load uploaded screenshot."
            )

        prepared_upload = ReferenceMatcher.prepare_image(
            uploaded_image
        )

        upload_features = ReferenceMatcher.extract_features(
            prepared_upload
        )

        references = ReferenceMatcher.load_references()

        if not references:
            raise ValueError(
                "No valid reference images found."
            )

        matches = []

        for reference in references:

            comparison = ReferenceMatcher.compare_features(
                upload_features,
                reference["features"]
            )

            matches.append({
                "app": reference["app"],
                "category": reference["category"],
                "filename": reference["filename"],
                **comparison
            })

        matches.sort(
            key=lambda item: item["combined_similarity"],
            reverse=True
        )

        grouped_results = {}

        for app in ReferenceMatcher.APPS:

            grouped_results[app] = {}

            for category in ReferenceMatcher.CATEGORIES:

                category_matches = [
                    item for item in matches
                    if item["app"] == app
                    and item["category"] == category
                ]

                category_matches.sort(
                    key=lambda item: item["combined_similarity"],
                    reverse=True
                )

                top_matches = category_matches[:3]

                average_score = (
                    np.mean([
                        item["combined_similarity"]
                        for item in top_matches
                    ])
                    if top_matches else None
                )

                grouped_results[app][category] = {
                    "average_top_similarity": (
                        round(float(average_score), 2)
                        if average_score is not None
                        else None
                    ),
                    "top_matches": top_matches
                }

        app_scores = {}

        for app, categories in grouped_results.items():

            scores = [
                categories[category]["average_top_similarity"]
                for category in ReferenceMatcher.CATEGORIES
                if categories[category]["average_top_similarity"]
                is not None
            ]

            if scores:
                app_scores[app] = round(
                    max(scores),
                    2
                )

        likely_app = (
            max(app_scores, key=app_scores.get)
            if app_scores else "Unknown"
        )

        return {
            "method": "SSIM and Edge Similarity",
            "references_compared": len(references),
            "likely_app_by_visual_similarity": likely_app,
            "app_similarity_scores": app_scores,
            "category_comparisons": grouped_results,
            "overall_top_matches": matches[:5],
            "assessment_note": (
                "Visual similarity is not proof of authenticity "
                "or manipulation. Results require validation "
                "using independent test images."
            )
        }
