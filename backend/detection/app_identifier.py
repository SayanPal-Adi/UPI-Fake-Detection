
import re


class UPIAppIdentifier:

    APP_SIGNATURES = {

        "Google Pay": {
            "strong": [
                "google pay",
                "google india"
            ],
            "weak": [
                "gpay",
                "google transaction"
            ]
        },

        "PhonePe": {
            "strong": [
                "phonepe",
                "phone pe"
            ],
            "weak": [
                "phonepe wallet",
                "phonepe transaction"
            ]
        },

        "Paytm": {
            "strong": [
                "paytm payments bank",
                "paytm"
            ],
            "weak": [
                "paytm upi",
                "paytm wallet"
            ]
        }
    }

    @staticmethod
    def normalize_text(text):

        text = text.lower()

        text = re.sub(
            r'[^a-z0-9\s]',
            ' ',
            text
        )

        text = re.sub(
            r'\s+',
            ' ',
            text
        )

        return text.strip()

    @staticmethod
    def identify(text):

        normalized_text = (
            UPIAppIdentifier.normalize_text(text)
        )

        results = {}

        for app, signatures in (
            UPIAppIdentifier.APP_SIGNATURES.items()
        ):

            score = 0
            matched = []

            for keyword in signatures["strong"]:

                if keyword in normalized_text:

                    score += 3
                    matched.append(keyword)

            for keyword in signatures["weak"]:

                if keyword in normalized_text:

                    score += 1
                    matched.append(keyword)

            results[app] = {
                "score": score,
                "matched_keywords": matched
            }

        ranked = sorted(
            results.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )

        best_app, best_result = ranked[0]

        second_score = ranked[1][1]["score"]

        # Require positive and sufficiently distinctive evidence.
        if (
            best_result["score"] < 3
            or best_result["score"] == second_score
        ):

            return {
                "app": "Unknown",
                "confidence": None,
                "identification_method": "OCR keywords",
                "scores": results
            }

        return {
            "app": best_app,
            "confidence": None,
            "identification_method": "OCR keywords",
            "matched_keywords": best_result[
                "matched_keywords"
            ],
            "scores": results
        }
