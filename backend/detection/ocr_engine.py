
import re
import pytesseract


class OCREngine:

    @staticmethod
    def extract_text(image):

        config = "--oem 3 --psm 6"

        text = pytesseract.image_to_string(
            image,
            config=config
        )

        return text.strip()

    @staticmethod
    def extract_details(text):

        details = {
            "amount": None,
            "amount_words": None,
            "upi_id": None,
            "transaction_id": None,
            "payment_status": "Unknown",
            "date": None,
            "time": None
        }

        # --------------------------------
        # 1. AMOUNT EXTRACTION
        # --------------------------------

        amount_patterns = [
            r'(?:₹|Rs\.?|INR|=)\s*[\d,]+(?:\.\d{1,2})?',
            r'\b\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?\b'
        ]

        for pattern in amount_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                details["amount"] = match.group().strip()

                if details["amount"].startswith("="):
                    details["amount"] = (
                        "₹" + details["amount"][1:].strip()
                    )

                break

        # --------------------------------
        # 2. AMOUNT IN WORDS
        # --------------------------------

        words_pattern = (
            r'Rupees\s+(.+?)\s+Only'
        )

        words_match = re.search(
            words_pattern,
            text,
            re.IGNORECASE
        )

        if words_match:
            details["amount_words"] = (
                words_match.group(1).strip()
            )

        # --------------------------------
        # 3. UPI ID
        # --------------------------------

        upi_pattern = (
            r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b'
        )

        upi = re.search(upi_pattern, text)

        if upi:
            details["upi_id"] = upi.group()

        # --------------------------------
        # 4. TRANSACTION ID
        # --------------------------------

        transaction_pattern = (
            r'(?:UPI\s*)?'
            r'(?:Ref(?:erence)?\s*(?:ID|No\.?)|'
            r'Transaction\s*ID|Txn\s*ID)'
            r'\s*[:#-]?\s*([A-Z0-9]{8,30})'
        )

        transaction = re.search(
            transaction_pattern,
            text,
            re.IGNORECASE
        )

        if transaction:
            details["transaction_id"] = (
                transaction.group(1)
            )

        # --------------------------------
        # 5. PAYMENT STATUS
        # --------------------------------

        lower_text = text.lower()

        if re.search(
            r'\b(?:payment|transaction)\s+successful\b'
            r'|\bsuccessfully\s+paid\b'
            r'|\bpaid\s+successfully\b',
            lower_text
        ):
            details["payment_status"] = "Successful"

        elif re.search(
            r'\b(?:payment|transaction)\s+failed\b',
            lower_text
        ):
            details["payment_status"] = "Failed"

        elif re.search(
            r'\b(?:payment|transaction)\s+pending\b',
            lower_text
        ):
            details["payment_status"] = "Pending"

        # --------------------------------
        # 6. DATE
        # --------------------------------

        date_pattern = (
            r'\b\d{1,2}\s+'
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            r'[a-z]*'
            r'(?!\w)'
            r'|'
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        )

        date = re.search(
            date_pattern,
            text,
            re.IGNORECASE
        )

        if date:
            details["date"] = date.group().strip()

        # --------------------------------
        # 7. TIME
        # --------------------------------

        time_pattern = (
            r'\b\d{1,2}:\d{2}'
            r'(?::\d{2})?'
            r'\s*(?:AM|PM)\b'
        )

        time = re.search(
            time_pattern,
            text,
            re.IGNORECASE
        )

        if time:
            details["time"] = time.group().strip()

        return details
