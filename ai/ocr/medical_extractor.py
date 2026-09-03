import re
from pathlib import Path

from ocr_engine import run_ocr

# --------------------------------------------------
# MEDICAL ENTITY EXTRACTION
# --------------------------------------------------

IMAGE_PATH = Path("processed/enhanced_prescription.png")


def extract_medical_entities(ocr_results):

    lines = [
        item["text"].strip()
        for item in ocr_results
        if item.get("text", "").strip()
    ]

    result = {
        "patient": {
            "name": None,
            "age": None,
            "gender": None
        },
        "doctor": {
            "name": None
        },
        "document": {
            "type": "prescription",
            "date": None
        },
        "clinical": {
            "chief_complaint": [],
            "diagnosis": []
        },
        "medications": [],
        "advice": []
    }

    # --------------------------------------------------
    # DOCTOR
    # --------------------------------------------------

    for line in lines:

        if line.lower().startswith("dr."):
            result["doctor"]["name"] = line
            break

    # --------------------------------------------------
    # DATE
    # --------------------------------------------------

    for line in lines:

        match = re.search(
            r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",
            line
        )

        if match:
            result["document"]["date"] = match.group(1)
            break

    # --------------------------------------------------
    # CHIEF COMPLAINT
    # --------------------------------------------------

    for line in lines:

        if "chief complaint" in line.lower():

            complaint = re.sub(
                r"^.*?:",
                "",
                line
            ).strip()

            # Split common separators
            parts = re.split(
                r",|&|\band\b",
                complaint,
                flags=re.IGNORECASE
            )

            result["clinical"]["chief_complaint"] = [
                p.strip()
                for p in parts
                if p.strip()
            ]

            break

    # --------------------------------------------------
    # MEDICATIONS
    # --------------------------------------------------

    medication_pattern = re.compile(
        r"^\s*(\d+)[\.\)]\s*"
        r"(?:Tab\.|Cap\.|Syp\.|Syrup|Tablet|Capsule)\s+"
        r"(.+?)"
        r"(?:\s+[–-]\s*|\s+)"
        r"(TDS|BD|OD|HS|SOS|QID|1-0-1|0-1-0|1-1-1)\s*$",
        re.IGNORECASE
    )

    for line in lines:

        match = medication_pattern.match(line)

        if not match:
            continue

        medicine_text = match.group(2).strip()
        frequency = match.group(3).upper()

        # Detect medicine form
        form = None

        lower_line = line.lower()

        if "tab." in lower_line:
            form = "tablet"
        elif "cap." in lower_line:
            form = "capsule"
        elif "syp." in lower_line or "syrup" in lower_line:
            form = "syrup"

        # Detect strength
        strength_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml)\b",
            medicine_text,
            re.IGNORECASE
        )

        strength = None

        if strength_match:
            strength = (
                strength_match.group(1)
                + " "
                + strength_match.group(2)
            )

        # Remove strength from medicine name
        medicine_name = re.sub(
            r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml)\b",
            "",
            medicine_text,
            flags=re.IGNORECASE
        ).strip()

        result["medications"].append({
            "name": medicine_name,
            "strength": strength,
            "form": form,
            "frequency": frequency,
            "route": None,
            "duration": None
        })

    # --------------------------------------------------
    # ADVICE
    # --------------------------------------------------

    advice_started = False

    for line in lines:

        if line.lower().startswith("advice"):
            advice_started = True
            continue

        if advice_started:

            clean = line.lstrip("•-* ").strip()

            if clean:
                result["advice"].append(clean)

    return result


def print_result(data):

    print()
    print("=" * 60)
    print("          MEDICAL ENTITY EXTRACTION")
    print("=" * 60)

    print()
    print("DOCUMENT")
    print(f"  Type : {data['document']['type']}")
    print(f"  Date : {data['document']['date']}")

    print()
    print("DOCTOR")
    print(f"  Name : {data['doctor']['name']}")

    print()
    print("CHIEF COMPLAINT")

    for complaint in data["clinical"]["chief_complaint"]:
        print(f"  - {complaint}")

    print()
    print("MEDICATIONS")

    for i, medicine in enumerate(data["medications"], 1):

        print(f"  {i}. {medicine['name']}")

        if medicine["strength"]:
            print(f"     Strength   : {medicine['strength']}")

        print(f"     Form       : {medicine['form']}")
        print(f"     Frequency  : {medicine['frequency']}")

    print()
    print("ADVICE")

    for advice in data["advice"]:
        print(f"  - {advice}")

    print()
    print("=" * 60)


def main():

    print("=" * 60)
    print("          MEDICAL DOCUMENT EXTRACTION")
    print("=" * 60)

    ocr_results = run_ocr(IMAGE_PATH)

    if not ocr_results:
        print("Extraction failed.")
        return

    extracted = extract_medical_entities(ocr_results)

    print_result(extracted)


if __name__ == "__main__":
    main()