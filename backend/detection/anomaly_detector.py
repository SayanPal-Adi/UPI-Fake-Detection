
import re


class AnomalyDetector:

    WORD_NUMBERS = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
        "hundred": 100,
        "thousand": 1000,
        "lakh": 100000,
        "lakhs": 100000,
        "million": 1000000,
        "crore": 10000000
    }

    @staticmethod
    def parse_amount(amount):
        if not amount:
            return None

        cleaned = re.sub(r"[^0-9.]", "", amount)

        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def parse_amount_words(words):

        if not words:
            return None

        tokens = re.findall(
            r"[a-zA-Z]+",
            words.lower()
        )

        total = 0
        current = 0

        for token in tokens:

            if token not in AnomalyDetector.WORD_NUMBERS:
                return None

            value = AnomalyDetector.WORD_NUMBERS[token]

            if value == 100:
                current = max(current, 1) * value

            elif value >= 1000:
                total += max(current, 1) * value
                current = 0

            else:
                current += value

        return float(total + current)

    @staticmethod
    def analyze(app_result, transaction_details):

        signals = []

        # 1. Check application identification
        if app_result.get("app") == "Unknown":
            signals.append({
                "code": "UNKNOWN_APP",
                "severity": "review",
                "message": "UPI application could not be identified."
            })

        # 2. Check transaction ID
        if not transaction_details.get("transaction_id"):
            signals.append({
                "code": "MISSING_TRANSACTION_ID",
                "severity": "review",
                "message": "Transaction reference ID was not detected."
            })

        # 3. Check amount
        if not transaction_details.get("amount"):
            signals.append({
                "code": "MISSING_AMOUNT",
                "severity": "review",
                "message": "Payment amount could not be extracted."
            })

        # 4. Check date
        if not transaction_details.get("date"):
            signals.append({
                "code": "MISSING_DATE",
                "severity": "review",
                "message": "Transaction date was not detected."
            })

        # 5. Check time
        if not transaction_details.get("time"):
            signals.append({
                "code": "MISSING_TIME",
                "severity": "review",
                "message": "Transaction time was not detected."
            })

        # 6. Check payment status
        status = transaction_details.get(
            "payment_status", "Unknown"
        )

        if status == "Failed":
            signals.append({
                "code": "PAYMENT_FAILED",
                "severity": "review",
                "message": "The screenshot indicates a failed payment."
            })

        elif status == "Pending":
            signals.append({
                "code": "PAYMENT_PENDING",
                "severity": "review",
                "message": "The screenshot indicates a pending payment."
            })

        elif status == "Unknown":
            signals.append({
                "code": "UNKNOWN_PAYMENT_STATUS",
                "severity": "review",
                "message": "Payment status could not be identified."
            })

        # 7. Compare numeric amount with amount in words
        numeric_amount = AnomalyDetector.parse_amount(
            transaction_details.get("amount")
        )

        written_amount = AnomalyDetector.parse_amount_words(
            transaction_details.get("amount_words")
        )

        if (
            numeric_amount is not None
            and written_amount is not None
            and numeric_amount != written_amount
        ):
            signals.append({
                "code": "AMOUNT_MISMATCH",
                "severity": "high",
                "message": (
                    "Numeric amount does not match the amount "
                    "written in words."
                ),
                "numeric_amount": numeric_amount,
                "written_amount": written_amount
            })

        # 8. Generate preliminary verdict
        high_signals = [
            signal for signal in signals
            if signal["severity"] == "high"
        ]

        if high_signals:
            verdict = "Suspicious"
        elif signals:
            verdict = "Review required"
        else:
            verdict = "No obvious OCR-level issues detected"

        return {
            "verdict": verdict,
            "signal_count": len(signals),
            "signals": signals,
            "assessment_note": (
                "This assessment uses screenshot-derived signals only. "
                "It does not verify whether money was received."
            )
        }
