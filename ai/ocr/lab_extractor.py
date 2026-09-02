# ============================================================
# LAB REPORT EXTRACTOR - POSITION AWARE
# MediKiosk - Module B
# ============================================================

import re
from pathlib import Path

from ocr_engine import run_ocr


# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_PATH = Path("test_images/cbcreport.jpg")


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    if text is None:
        return ""

    text = str(text).strip()

    # OCR dash normalization
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("−", "-")

    # Common OCR corrections
    text = text.replace("µ", "u")

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# NUMBER PARSING
# ============================================================

NUMBER_PATTERN = r"\d+(?:\.\d+)?"


def parse_number(text):
    text = normalize_text(text)

    match = re.fullmatch(NUMBER_PATTERN, text)

    if not match:
        return None

    try:
        return float(text)
    except ValueError:
        return None


# ============================================================
# REFERENCE RANGE
# ============================================================

REFERENCE_RANGE_PATTERN = (
    rf"({NUMBER_PATTERN})\s*-\s*({NUMBER_PATTERN})"
)


def parse_reference_range(text):
    text = normalize_text(text)

    match = re.fullmatch(
        REFERENCE_RANGE_PATTERN,
        text
    )

    if not match:
        return None

    return {
        "low": float(match.group(1)),
        "high": float(match.group(2))
    }


# ============================================================
# UNIT NORMALIZATION
# ============================================================

UNIT_ALIASES = {
    "g/dl": "g/dL",
    "g/l": "g/L",
    "mg/dl": "mg/dL",
    "mg/l": "mg/L",
    "iu/l": "IU/L",
    "u/l": "U/L",

    "cells/ul": "cells/uL",
    "cells/µl": "cells/uL",

    "10^3/ul": "10^3/uL",
    "10^3/µl": "10^3/uL",

    "10^6/ul": "10^6/uL",
    "10^6/µl": "10^6/uL",

    "mill/cumm": "mill/cumm",
    "cells/cumm": "cells/cumm",
    "cumm": "cumm",

    "mm/hr": "mm/hr",
    "fl": "fL",
    "pg": "pg",
    "%": "%",

    "mmol/l": "mmol/L",
    "meq/l": "mEq/L",
}


def normalize_unit(text):
    text = normalize_text(text)

    key = text.lower()

    return UNIT_ALIASES.get(key)


# ============================================================
# TEST NAME ALIASES
# ============================================================

TEST_ALIASES = {

    "hemoglobin (hb)": "Hemoglobin (Hb)",
    "hemoglobin": "Hemoglobin (Hb)",
    "hb": "Hemoglobin (Hb)",

    "total rbc count": "Total RBC count",
    "rbc count": "Total RBC count",

    "packed cell volume (pcv)": "Packed Cell Volume (PCV)",
    "packed cell volume": "Packed Cell Volume (PCV)",
    "pcv": "Packed Cell Volume (PCV)",

    "mean corpuscular volume (mcv)": "Mean Corpuscular Volume (MCV)",
    "mean corpuscular volume": "Mean Corpuscular Volume (MCV)",
    "mcv": "Mean Corpuscular Volume (MCV)",

    "mean corpuscular hemoglobin (mch)": "MCH",
    "mch": "MCH",

    "mean corpuscular hemoglobin concentration (mchc)": "MCHC",
    "mchc": "MCHC",

    "rdw": "RDW",

    "total wbc count": "Total WBC count",
    "total wbc": "Total WBC count",
    "wbc count": "Total WBC count",

    "neutrophils": "Neutrophils",

    # OCR sometimes drops first character
    "ymphocytes": "Lymphocytes",
    "lymphocytes": "Lymphocytes",

    "eosinophils": "Eosinophils",

    "monocytes": "Monocytes",

    "basophils": "Basophils",

    "platelet count": "Platelet Count",
    "platelets": "Platelet Count",
    "platelet": "Platelet Count",
}


def identify_test_name(text):
    text = normalize_text(text)

    key = text.lower()

    return TEST_ALIASES.get(key)


# ============================================================
# EXPECTED CBC TESTS
# ============================================================

EXPECTED_TESTS = [

    "Hemoglobin (Hb)",
    "Total RBC count",
    "Packed Cell Volume (PCV)",
    "Mean Corpuscular Volume (MCV)",
    "MCH",
    "MCHC",
    "RDW",
    "Total WBC count",
    "Neutrophils",
    "Lymphocytes",
    "Eosinophils",
    "Monocytes",
    "Basophils",
    "Platelet Count",
]


# ============================================================
# OCR ITEM PREPARATION
# ============================================================

def prepare_ocr_items(ocr_results):

    items = []

    for item in ocr_results:

        text = normalize_text(
            item.get("text", "")
        )

        if not text:
            continue

        bbox = item.get("bbox")

        if not bbox or len(bbox) != 4:
            continue

        try:

            x1 = float(bbox[0])
            y1 = float(bbox[1])
            x2 = float(bbox[2])
            y2 = float(bbox[3])

        except (ValueError, TypeError):

            continue

        item_data = {

            "text": text,

            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,

            "center_x": (x1 + x2) / 2,
            "center_y": (y1 + y2) / 2,

            "confidence": float(
                item.get("confidence", 0.0)
            )
        }

        items.append(item_data)

    return items


# ============================================================
# TABLE COLUMN DETECTION
# ============================================================

def classify_column(item):

    x = item["center_x"]

    # Investigation column
    if x < 300:
        return "name"

    # Result column
    if 300 <= x < 500:
        return "value"

    # Reference range column
    if 600 <= x < 850:
        return "reference"

    # Unit column
    if 900 <= x < 1050:
        return "unit"

    # Status column
    if 500 <= x < 600:
        return "status"

    return "other"


# ============================================================
# STATUS
# ============================================================

VALID_STATUSES = {
    "NORMAL",
    "HIGH",
    "LOW",
    "ABNORMAL",
}


def normalize_status(text):

    text = normalize_text(text).upper()

    if text in VALID_STATUSES:
        return text

    return None


def determine_status(value, reference_range):

    if value is None:
        return "UNKNOWN"

    if not reference_range:
        return "UNKNOWN"

    low = reference_range["low"]
    high = reference_range["high"]

    if value < low:
        return "LOW"

    if value > high:
        return "HIGH"

    return "NORMAL"


# ============================================================
# RISK FLAG
# ============================================================

def determine_risk_flag(status):

    if status == "LOW":
        return "LOW"

    if status == "HIGH":
        return "HIGH"

    if status == "ABNORMAL":
        return "ABNORMAL"

    if status == "NORMAL":
        return "NONE"

    return "UNKNOWN"


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    value,
    unit,
    reference_range,
    ocr_confidence
):

    score = 0.0

    if value is not None:
        score += 0.40

    if unit is not None:
        score += 0.15

    if reference_range is not None:
        score += 0.30

    score += 0.15 * max(
        0.0,
        min(1.0, ocr_confidence)
    )

    return round(
        min(score, 1.0),
        2
    )


# ============================================================
# FIND ROWS
# ============================================================

def get_test_rows(items):

    rows = []

    for item in items:

        test_name = identify_test_name(
            item["text"]
        )

        if not test_name:
            continue

        row = {

            "name": test_name,

            "name_item": item,

            "y": item["center_y"],

            "value_items": [],
            "reference_items": [],
            "unit_items": [],
            "status_items": [],

        }

        rows.append(row)

    return rows


# ============================================================
# ASSIGN OCR ITEMS TO TEST ROW
# ============================================================

def assign_items_to_rows(
    items,
    rows,
    y_tolerance=28
):

    for item in items:

        # Ignore test-name items
        if identify_test_name(item["text"]):
            continue

        best_row = None
        best_distance = None

        for row in rows:

            distance = abs(
                item["center_y"] - row["y"]
            )

            if distance > y_tolerance:
                continue

            if (
                best_distance is None
                or distance < best_distance
            ):

                best_row = row
                best_distance = distance

        if best_row is None:
            continue

        column = classify_column(item)

        if column == "value":

            best_row["value_items"].append(item)

        elif column == "reference":

            best_row["reference_items"].append(item)

        elif column == "unit":

            best_row["unit_items"].append(item)

        elif column == "status":

            best_row["status_items"].append(item)


# ============================================================
# EXTRACT VALUE FROM ROW
# ============================================================

def extract_value(row):

    candidates = []

    for item in row["value_items"]:

        number = parse_number(
            item["text"]
        )

        if number is None:
            continue

        candidates.append(
            (
                item["center_y"],
                number,
                item["confidence"]
            )
        )

    if not candidates:
        return None, 0.0

    # Closest vertically to test name
    candidates.sort(
        key=lambda x: abs(
            x[0] - row["y"]
        )
    )

    _, value, confidence = candidates[0]

    return value, confidence


# ============================================================
# EXTRACT REFERENCE RANGE
# ============================================================

def extract_reference(row):

    candidates = []

    for item in row["reference_items"]:

        reference = parse_reference_range(
            item["text"]
        )

        if reference is None:
            continue

        candidates.append(
            (
                abs(
                    item["center_y"]
                    - row["y"]
                ),
                reference,
                item["confidence"]
            )
        )

    if not candidates:
        return None, 0.0

    candidates.sort(
        key=lambda x: x[0]
    )

    _, reference, confidence = candidates[0]

    return reference, confidence


# ============================================================
# EXTRACT UNIT
# ============================================================

def extract_unit(row):

    candidates = []

    for item in row["unit_items"]:

        unit = normalize_unit(
            item["text"]
        )

        if unit is None:
            continue

        candidates.append(
            (
                abs(
                    item["center_y"]
                    - row["y"]
                ),
                unit,
                item["confidence"]
            )
        )

    if not candidates:
        return None, 0.0

    candidates.sort(
        key=lambda x: x[0]
    )

    _, unit, confidence = candidates[0]

    return unit, confidence


# ============================================================
# EXTRACT EXPLICIT STATUS
# ============================================================

def extract_status(row):

    for item in row["status_items"]:

        status = normalize_status(
            item["text"]
        )

        if status:
            return status

    return None


# ============================================================
# BUILD TEST
# ============================================================

def build_test(row):

    value, value_confidence = extract_value(
        row
    )

    reference_range, reference_confidence = (
        extract_reference(row)
    )

    unit, unit_confidence = extract_unit(
        row
    )

    explicit_status = extract_status(
        row
    )

    calculated_status = determine_status(
        value,
        reference_range
    )

    # Prefer mathematically calculated status
    # when both value and reference exist.
    if calculated_status != "UNKNOWN":

        status = calculated_status

    elif explicit_status:

        status = explicit_status

    else:

        status = "UNKNOWN"

    abnormal = status in {
        "LOW",
        "HIGH",
        "ABNORMAL"
    }

    risk_flag = determine_risk_flag(
        status
    )

    confidence = calculate_confidence(

        value=value,

        unit=unit,

        reference_range=reference_range,

        ocr_confidence=max(
            value_confidence,
            reference_confidence,
            unit_confidence
        )
    )

    return {

        "name": row["name"],

        "value": value,

        "unit": unit,

        "reference_range": reference_range,

        "status": status,

        "abnormal": abnormal,

        "risk_flag": risk_flag,

        "confidence": confidence
    }


# ============================================================
# LAB TEST EXTRACTION
# ============================================================

def extract_lab_tests(ocr_results):

    items = prepare_ocr_items(
        ocr_results
    )

    if not items:
        return []

    # --------------------------------------------------------
    # Find test rows
    # --------------------------------------------------------

    rows = get_test_rows(
        items
    )

    if not rows:
        return []

    # --------------------------------------------------------
    # Assign values/reference/unit/status
    # according to Y position + X column.
    # --------------------------------------------------------

    assign_items_to_rows(
        items,
        rows,
        y_tolerance=32
    )

    # --------------------------------------------------------
    # Build structured tests
    # --------------------------------------------------------

    tests = []

    for row in rows:

        test = build_test(
            row
        )

        tests.append(
            test
        )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique_tests = []

    seen = set()

    for test in tests:

        key = test["name"].lower()

        if key in seen:
            continue

        seen.add(key)

        unique_tests.append(
            test
        )

    return unique_tests


# ============================================================
# PRINT RESULT
# ============================================================

def print_result(tests):

    print()

    print("=" * 60)
    print("             LAB TEST EXTRACTION")
    print("=" * 60)

    if not tests:

        print()
        print(
            "No laboratory values detected."
        )

    else:

        for i, test in enumerate(
            tests,
            1
        ):

            print()

            print(
                f"{i}. {test['name']}"
            )

            print(
                f"   Value      : "
                f"{test['value']}"
            )

            print(
                f"   Unit       : "
                f"{test['unit']}"
            )

            print(
                f"   Range      : "
                f"{test['reference_range']}"
            )

            print(
                f"   Status     : "
                f"{test['status']}"
            )

            print(
                f"   Abnormal   : "
                f"{test['abnormal']}"
            )

            print(
                f"   Risk Flag  : "
                f"{test['risk_flag']}"
            )

            print(
                f"   Confidence : "
                f"{test['confidence']}"
            )

    print()

    print("=" * 60)

    print(
        f"Total tests detected: "
        f"{len(tests)}"
    )

    print("=" * 60)


# ============================================================
# SAVE JSON
# ============================================================

def save_json(tests):

    output_path = Path(
        "lab_extraction_result.json"
    )

    data = {

        "document_type": "laboratory_report",

        "source_file": str(
            IMAGE_PATH
        ),

        "tests": tests,

        "total_tests": len(tests)
    }

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        import json

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()

    print(
        f"JSON saved to: "
        f"{output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("             LAB REPORT EXTRACTION")
    print("=" * 60)

    print()

    print(
        f"Input : {IMAGE_PATH}"
    )

    # --------------------------------------------------------
    # Check image
    # --------------------------------------------------------

    if not IMAGE_PATH.exists():

        print()

        print(
            "ERROR: Lab report image not found."
        )

        print(
            f"Expected: {IMAGE_PATH}"
        )

        return

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    print()

    print(
        "Running OCR..."
    )

    print("=" * 60)
    print("                  OCR ENGINE")
    print("=" * 60)

    try:

        ocr_results = run_ocr(
            IMAGE_PATH
        )

    except Exception as error:

        print()

        print(
            "ERROR: OCR failed."
        )

        print(
            f"Reason: {error}"
        )

        return

    if not ocr_results:

        print()

        print(
            "OCR returned no text."
        )

        return

    print()

    print(
        f"OCR completed."
    )

    print(
        f"Total OCR items: "
        f"{len(ocr_results)}"
    )

    # --------------------------------------------------------
    # Extraction
    # --------------------------------------------------------

    print()

    print(
        "Extracting laboratory tests..."
    )

    tests = extract_lab_tests(
        ocr_results
    )

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print_result(
        tests
    )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    save_json(
        tests
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()