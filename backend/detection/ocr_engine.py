
import pytesseract
import re


class OCREngine:

    @staticmethod
    def extract_text(image):
        """
        Extract text from a preprocessed image.
        """

        config = "--oem 3 --psm 6"

        text = pytesseract.image_to_string(
            image,
            config=config
        )

        return text

    @staticmethod
    def extract_details(text):

        details = {
            "amount": None,
            "upi_id": None,
            "transaction_id": None,
            "payment_status": None,
            "date": None,
            "time": None
        }

        # Extract amount
        amount_pattern = (
            r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d{1,2})?'
        )

        amount = re.search(
            amount_pattern,
            text,
            re.IGNORECASE
        )

        if amount:
            details["amount"] = amount.group()

        # Extract UPI ID
        upi_pattern = (
            r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b'
        )

        upi = re.search(upi_pattern, text)

        if upi:
            details["upi_id"] = upi.group()

        # Extract transaction ID
        transaction_pattern = (
            r'(?:transaction\s*id|txn\s*id|'
            r'upi\s*ref(?:erence)?\s*(?:no|number)?)'
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

        # Identify payment status
        lower_text = text.lower()

        if "payment successful" in lower_text:
            details["payment_status"] = "Successful"

        elif "successful" in lower_text:
            details["payment_status"] = "Possible success"

        elif "failed" in lower_text:
            details["payment_status"] = "Failed"

        elif "pending" in lower_text:
            details["payment_status"] = "Pending"

        # Extract date
        date_pattern = (
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        )

        date = re.search(date_pattern, text)

        if date:
            details["date"] = date.group()

        # Extract time
        time_pattern = (
            r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\b'
        )

        time = re.search(
            time_pattern,
            text,
            re.IGNORECASE
        )

        if time:
            details["time"] = time.group()

        return details
