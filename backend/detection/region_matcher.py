
import os
import cv2
import numpy as np

from skimage.metrics import structural_similarity
from detection.reference_matcher import ReferenceMatcher


class RegionMatcher:

    REGION_NAMES = [
        "header",
        "upper_details",
        "middle_details",
        "lower_details",
        "footer"
    ]

    @staticmethod
    def split_regions(image):

        height = image.shape[0]
        regions = {}

        for index, name in enumerate(
            RegionMatcher.REGION_NAMES
        ):

            y1 = index * height // 5
            y2 = (index + 1) * height // 5

            regions[name] = image[y1:y2, :]

        return regions

    @staticmethod
    def compare_regions(upload_regions, reference_regions):

        results = {}

        for name in RegionMatcher.REGION_NAMES:

            uploaded = upload_regions[name]
            reference = reference_regions[name]

            ssim_score = structural_similarity(
                uploaded,
                reference,
                data_range=255
            )

            uploaded_edges = cv2.Canny(
                uploaded, 60, 150
            )

            reference_edges = cv2.Canny(
                reference, 60, 150
            )

            edge_score = structural_similarity(
                uploaded_edges,
                reference_edges,
                data_range=255
            )

            combined = (
                0.65 * ssim_score +
                0.35 * edge_score
            )

            results[name] = round(
                max(0, combined) * 100,
                2
            )

        return results

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

                    path = os.path.join(folder, filename)

                    image = cv2.imread(path)

                    if image is None:
                        continue

                    prepared = ReferenceMatcher.prepare_image(
                        image
                    )

                    references.append({
                        "app": app,
                        "category": category,
                        "filename": filename,
                        "regions": RegionMatcher.split_regions(
                            prepared
                        )
                    })

        return references

    @staticmethod
    def analyze(image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(
                "Unable to load uploaded screenshot."
            )

        prepared = ReferenceMatcher.prepare_image(image)

        upload_regions = RegionMatcher.split_regions(
            prepared
        )

        references = RegionMatcher.load_references()

        if not references:
            raise ValueError(
                "No valid reference screenshots found."
            )

        matches = []

        for reference in references:

            region_scores = RegionMatcher.compare_regions(
                upload_regions,
                reference["regions"]
            )

            overall_score = float(
                np.mean(list(region_scores.values()))
            )

            matches.append({
                "app": reference["app"],
                "category": reference["category"],
                "filename": reference["filename"],
                "overall_similarity": round(
                    overall_score, 2
                ),
                "region_scores": region_scores
            })
        matches.sort(
            key=lambda item: item["overall_similarity"],
            reverse=True
        )
        grouped_results = {}
        for app in ReferenceMatcher.APPS:

            grouped_results[app] = {}

            for category in ReferenceMatcher.CATEGORIES:

                selected = [
                    item for item in matches
                    if item["app"] == app
                    and item["category"] == category
                ]

                selected.sort(
                    key=lambda item: item["overall_similarity"],
                    reverse=True
                )

                top_matches = selected[:3]

                average = (
                    float(np.mean([
                        item["overall_similarity"]
                        for item in top_matches
                    ]))
                    if top_matches else None
                )

                grouped_results[app][category] = {
                    "average_top_similarity": (
                        round(average, 2)
                        if average is not None else None
                    ),
                    "top_matches": top_matches
                }

        return {
            "method": "Region-based SSIM and Edge Comparison",
            "references_compared": len(references),
            "regions_compared": RegionMatcher.REGION_NAMES,
            "category_comparisons": grouped_results,
            "overall_top_matches": matches[:5],
            "assessment_note": (
                "Region scores indicate visual resemblance only. "
                "Different receipt layouts and screen dimensions "
                "can affect the results. They do not prove fraud."
            )
        }
