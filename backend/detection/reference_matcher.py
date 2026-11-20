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
    TOP_MATCHES = 3

    SUPPORTED_EXTENSIONS = {
        ".jpg", ".jpeg", ".png"
    }

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
    def get_similarity(image1, image2):

        return structural_similarity(
            image1,
            image2,
            data_range=255
        )

    @staticmethod
    def load_references():

        references = []

        applications = [
            "google_pay",
            "phonepe",
            "paytm"
        ]

        for app in applications:

            for category in [
                "genuine",
                "manipulated"
            ]:

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

                    references.append({
                        "app": app,
                        "category": category,
                        "filename": filename,
                        "image": ReferenceMatcher.prepare_image(
                            image
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

        references = ReferenceMatcher.load_references()

        if not references:
            raise ValueError(
                "No valid reference images found."
            )

        matches = []

        for reference in references:

            similarity = ReferenceMatcher.get_similarity(
                prepared_upload,
                reference["image"]
            )

            matches.append({
                "app": reference["app"],
                "category": reference["category"],
                "filename": reference["filename"],
                "similarity_percent": round(
                    max(0, similarity) * 100,
                    2
                )
            })

        matches.sort(
            key=lambda item: item["similarity_percent"],
            reverse=True
        )

        # Group results by application and category
        grouped_results = {}

        for app in [
            "google_pay",
            "phonepe",
            "paytm"
        ]:

            grouped_results[app] = {}

            for category in [
                "genuine",
                "manipulated"
            ]:

                category_matches = [
                    match for match in matches
                    if match["app"] == app
                    and match["category"] == category
                ]

                category_matches.sort(
                    key=lambda item: item["similarity_percent"],
                    reverse=True
                )

                top_matches = category_matches[
                    :ReferenceMatcher.TOP_MATCHES
                ]

                average_score = (
                    sum(
                        item["similarity_percent"]
                        for item in top_matches
                    ) / len(top_matches)
                    if top_matches else None
                )

                grouped_results[app][category] = {
                    "average_top_similarity": (
                        round(average_score, 2)
                        if average_score is not None
                        else None
                    ),
                    "top_matches": top_matches
                }

        # Find the application with the strongest
        # overall visual similarity
        app_scores = {}

        for app, categories in grouped_results.items():

            scores = [
                categories[category][
                    "average_top_similarity"
                ]
                for category in [
                    "genuine",
                    "manipulated"
                ]
                if categories[category][
                    "average_top_similarity"
                ] is not None
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
            "method": "SSIM Reference Comparison",
            "references_compared": len(references),
            "likely_app_by_visual_similarity": likely_app,
            "app_similarity_scores": app_scores,
            "category_comparisons": grouped_results,
            "overall_top_matches": matches[:5],
            "assessment_note": (
                "Similarity scores indicate visual resemblance "
                "to stored examples. They do not establish "
                "authenticity or prove manipulation."
            )
        }