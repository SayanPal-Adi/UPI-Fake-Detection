
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

        if not text:
            return details

        # Normalize OCR text
        text = text.replace("\u00a0", " ")
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # --------------------------------
        # 1. AMOUNT EXTRACTION
        # --------------------------------

        def valid_amount(value):

            try:
                cleaned = value.replace(",", "")
                number = float(cleaned)

                return (
                    0 < number <= 100000000
                )

            except (ValueError, TypeError):
                return False

        # First preference: explicit currency or amount labels
        explicit_patterns = [

            # ₹500, ₹ 500
            r'₹\s*([0-9][0-9,]*(?:\.\d{1,2})?)',

            # Rs. 500, INR 500
            r'\b(?:INR|Rs\.?)\s*'
            r'([0-9][0-9,]*(?:\.\d{1,2})?)',

            # Amount: 500, You paid 500
            r'\b(?:amount|you\s+paid|paid|total|sent)'
            r'\s*(?:is|of|:|-)?\s*'
            r'(?:₹|INR|Rs\.?)?\s*'
            r'([0-9][0-9,]*(?:\.\d{1,2})?)'
        ]

        for pattern in explicit_patterns:

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

        
        if not details["amount"]:

            grouped_pattern = (
                r'(?<![\w/])'
                r'(\d{1,3}(?:,\d{3})+)'
                r'(?:\.\d{1,2})?'
                r'(?![\w/])'
            )

            for line in lines:

                match = re.search(
                    grouped_pattern,
                    line
                )

                if match:

                    candidate = match.group(0).strip()

                    if valid_amount(candidate):

                        details["amount"] = "₹" + candidate
                        break

        # --------------------------------
        # 2. AMOUNT IN WORDS
        # --------------------------------

        words_patterns = [
            r'(?:Indian\s+)?Rupees\s+(.+?)\s+Only'
        ]

        for pattern in words_patterns:

            words_match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL
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

        month_names = (
            r'Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|'
            r'Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|'
            r'Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|'
            r'Nov(?:ember)?|Dec(?:ember)?'
        )

        date_patterns = [

            # Example: 30 Jun, 2026 or 30 Jun
            r'\b\d{1,2}\s+'
            + month_names
            + r'(?:\s*,?\s+\d{4})?\b',

            # Example: 30/06/2026 or 30-06-2026
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        ]

        for pattern in date_patterns:

            date = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if date:

                details["date"] = date.group().strip()
                break

        # --------------------------------
        # 7. TIME
        # --------------------------------

        time_pattern = (
            r'\b(?:0?[1-9]|1[0-2]):[0-5]\d'
            r'(?::[0-5]\d)?'
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
