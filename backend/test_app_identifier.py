
from detection.app_identifier import UPIAppIdentifier


test_cases = {

    "Google Pay": """
        Google Pay
        Payment Successful
        UPI Transaction ID
    """,

    "PhonePe": """
        PhonePe
        Payment Successful
        UPI Reference ID
    """,

    "Paytm": """
        Paytm
        Payment Successful
        UPI Transaction
    """,

    "Unknown": """
        Payment Successful
        Rs 500
        Transaction ID 123456789012
    """
}


for expected, text in test_cases.items():

    result = UPIAppIdentifier.identify(text)

    print("\nExpected:", expected)
    print("Detected:", result["app"])
    print("Matched:", result.get("matched_keywords", []))

    if result["app"] == expected:
        print("TEST PASSED")
    else:
        print("TEST FAILED")

