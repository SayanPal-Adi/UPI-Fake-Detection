
import re
import pytesseract


class OCREngine:

    @staticmethod
    def extract_text(image):

        # OCR configuration
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

        if not text:
            return details

        # Normalize OCR text
        text = text.replace("\u00a0", " ")
        text = text.replace("₹", "₹")

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # --------------------------------
        # 1. AMOUNT EXTRACTION
        # --------------------------------

        amount_patterns = [

            # Currency symbol: ₹500 or ₹ 500
            r'(?:₹)\s*([0-9][0-9,]*(?:\.\d{1,2})?)',

            # INR 500, Rs. 500, Rs 500
            r'\b(?:INR|Rs\.?)\s*([0-9][0-9,]*(?:\.\d{1,2})?)',

            # Amount labels: Amount: 500, You paid 500
            r'\b(?:amount|you\s+paid|paid|total|sent)'
            r'\s*(?:is|of|:|-)?\s*'
            r'(?:₹|INR|Rs\.?)?\s*'
            r'([0-9][0-9,]*(?:\.\d{1,2})?)',

        ]

        def valid_amount(value):

            try:
                cleaned = value.replace(",", "")
                number = float(cleaned)

                # Reject zero, negative and implausibly large values
                if number <= 0 or number > 100000000:
                    return False

                return True

            except (ValueError, TypeError):
                return False

        for pattern in amount_patterns:

            for line in lines:

                match = re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                )

                if match:

                    candidate = match.group(1).strip()

                    if valid_amount(candidate):

                        details["amount"] = "₹" + candidate
                        break

            if details["amount"]:
                break

        # --------------------------------
        # 2. AMOUNT IN WORDS
        # --------------------------------

        words_patterns = [
            r'Rupees\s+(.+?)\s+Only',
            r'Indian\s+Rupees\s+(.+?)\s+Only'
        ]

        for pattern in words_patterns:

            words_match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if words_match:

                details["amount_words"] = (
                    words_match.group(1).strip()
                )

                break

        # --------------------------------
        # 3. UPI ID
        # --------------------------------

        upi_pattern = (
            r'\b[a-zA-Z0-9._-]+'
            r'@[a-zA-Z0-9.-]+\b'
        )

        upi = re.search(
            upi_pattern,
            text
        )

        if upi:

            details["upi_id"] = upi.group()

        # --------------------------------
        # 4. TRANSACTION ID
        # --------------------------------

        transaction_patterns = [

            r'(?:UPI\s*)?'
            r'(?:Ref(?:erence)?\s*(?:ID|No\.?)|'
            r'Transaction\s*ID|Txn\s*ID)'
            r'\s*[:#-]?\s*([A-Z0-9]{8,30})',

            r'\bUPI\s+Ref\s*[:#-]?\s*'
            r'([A-Z0-9]{8,30})'

        ]

        for pattern in transaction_patterns:

            transaction = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if transaction:

                details["transaction_id"] = (
                    transaction.group(1)
                )

                break

        # --------------------------------
        # 5. PAYMENT STATUS
        # --------------------------------

        lower_text = text.lower()

        if re.search(
            r'\b(?:payment|transaction)\s+successful\b'
            r'|\bsuccessfully\s+paid\b'
            r'|\bpaid\s+successfully\b'
            r'|\bpayment\s+completed\b',
            lower_text
        ):

            details["payment_status"] = "Successful"

        elif re.search(
            r'\b(?:payment|transaction)\s+failed\b'
            r'|\bpayment\s+unsuccessful\b',
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
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|'
            r'Sep|Oct|Nov|Dec)[a-z]*'
            r'\s*,?\s*\d{0,4}\b'
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
