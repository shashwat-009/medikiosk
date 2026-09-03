from pathlib import Path
from ocr_engine import run_ocr

# --------------------------------------------------
# DOCUMENT TYPE CLASSIFIER
# --------------------------------------------------

IMAGE_PATH = Path("processed/enhanced_prescription.png")


def classify_document(ocr_results):
    """
    Classify medical document using OCR text.
    """

    text = " ".join(
        item["text"].lower()
        for item in ocr_results
        if item.get("text")
    )

    # Prescription indicators
    prescription_words = [
        "prescription",
        "rx",
        "tab.",
        "tablet",
        "cap.",
        "capsule",
        "syp.",
        "syrup",
        "dose",
        "tds",
        "bd",
        "od",
        "hs",
        "medicine",
        "medication"
    ]

    # Lab report indicators
    lab_words = [
        "laboratory",
        "lab report",
        "hemoglobin",
        "haemoglobin",
        "wbc",
        "rbc",
        "platelet",
        "reference range",
        "reference value",
        "blood test",
        "test result",
        "mg/dl",
        "g/dl"
    ]

    # Imaging report indicators
    imaging_words = [
        "x-ray",
        "xray",
        "mri",
        "ct scan",
        "ultrasound",
        "radiology",
        "impression",
        "findings",
        "scan report"
    ]

    # Discharge summary indicators
    discharge_words = [
        "discharge summary",
        "discharge diagnosis",
        "date of admission",
        "date of discharge",
        "hospital course",
        "discharge medications"
    ]

    scores = {
        "prescription": 0,
        "lab_report": 0,
        "imaging_report": 0,
        "discharge_summary": 0
    }

    for word in prescription_words:
        if word in text:
            scores["prescription"] += 1

    for word in lab_words:
        if word in text:
            scores["lab_report"] += 1

    for word in imaging_words:
        if word in text:
            scores["imaging_report"] += 1

    for word in discharge_words:
        if word in text:
            scores["discharge_summary"] += 1

    document_type = max(scores, key=scores.get)

    # Nothing meaningful detected
    if scores[document_type] == 0:
        document_type = "unknown"

    return document_type, scores


def main():

    print("=" * 60)
    print("             DOCUMENT CLASSIFICATION")
    print("=" * 60)

    # Run OCR
    ocr_results = run_ocr(IMAGE_PATH)

    if not ocr_results:
        print("Status : FAILED")
        print("Reason : No OCR text detected.")
        return

    # Classify
    document_type, scores = classify_document(ocr_results)

    print()
    print("=" * 60)
    print("             CLASSIFICATION RESULT")
    print("=" * 60)

    print(f"Document Type : {document_type}")

    print()
    print("Scores:")

    for name, score in scores.items():
        print(f"  {name:<22}: {score}")

    print("=" * 60)


if __name__ == "__main__":
    main()