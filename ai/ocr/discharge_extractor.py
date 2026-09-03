import json
import re
from pathlib import Path

from ocr_engine import run_ocr


# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_PATH = Path("test_images/discharge.jpg")
OUTPUT_PATH = Path("discharge_extraction_result.json")


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(text):
    if text is None:
        return ""

    text = str(text).strip()

    # Normalize OCR punctuation
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("−", "-")
    text = text.replace("â€“", "-")
    text = text.replace("â€”", "-")

    # Normalize repeated spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_ocr_text(text):
    text = normalize_text(text)

    # Common OCR mistakes
    replacements = {
        "tedications": "Medications",
        "antibioties": "antibiotics",
        "Resumeanormaldietastolerated": "Resume a normal diet as tolerated",
        "Startwithlightmealsandgraduallyretumtoregulareatinghabits":
            "Start with light meals and gradually return to regular eating habits.",
        "Avoidheavy liftingand strenuousactivities for2 weeks":
            "Avoid heavy lifting and strenuous activities for 2 weeks.",
        "Gentlewalkingisencouraged":
            "Gentle walking is encouraged.",
        "Returnforafollow-upappointmentwith thesurgeon":
            "Return for a follow-up appointment with the surgeon",
        "Keeptheincision sitecleananddry":
            "Keep the incision site clean and dry",
        "Changedressingsasinstructed":
            "Change dressings as instructed",
        "Monitor forsignsof":
            "Monitor for signs of",
        "Takeall prescribed medicationsasdirected":
            "Take all prescribed medications as directed",
        "Completethefull courseofantibiotics":
            "Complete the full course of antibiotics",
        "If you experienceahigh fever":
            "If you experience a high fever",
        "increased pain, swelling rednessat the incision site":
            "increased pain, swelling or redness at the incision site",
        "contact yourhealthcareprovider":
            "contact your healthcare provider",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


# ============================================================
# DATE / TIME HELPERS
# ============================================================

MONTHS = (
    "January|February|March|April|May|June|July|August|"
    "September|October|November|December"
)

DATE_PATTERN = re.compile(
    rf"\b(?:{MONTHS})\s+\d{{1,2}}[,.]?\s+\d{{4}}\b",
    re.IGNORECASE
)

TIME_PATTERN = re.compile(
    r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b",
    re.IGNORECASE
)


def find_date(text):
    match = DATE_PATTERN.search(text)

    if not match:
        return None

    value = match.group(0)
    value = value.replace(",", "")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def find_time(text):
    match = TIME_PATTERN.search(text)

    if not match:
        return None

    return match.group(0).strip()


# ============================================================
# SECTION DETECTION
# ============================================================

SECTION_NAMES = {
    "patient information": "patient_information",
    "diagnosis": "diagnosis",
    "treatment summary": "treatment_summary",
    "medications prescribed": "medications",
    "discharge instructions": "discharge_instructions",
    "next appointment": "next_appointment",
    "contact information": "contact_information",
}


def detect_section(line):
    clean = normalize_text(line).lower()

    for heading, section in SECTION_NAMES.items():
        if clean.startswith(heading):
            return section

    return None


# ============================================================
# SECTION EXTRACTION
# ============================================================

def split_sections(lines):

    sections = {
        "header": [],
        "patient_information": [],
        "diagnosis": [],
        "treatment_summary": [],
        "medications": [],
        "discharge_instructions": [],
        "next_appointment": [],
        "contact_information": [],
        "other": []
    }

    current_section = "header"

    for line in lines:

        clean = clean_ocr_text(line)

        if not clean:
            continue

        detected = detect_section(clean)

        if detected:
            current_section = detected

            # Remove heading itself
            remainder = re.sub(
                r"^[^:]+:\s*",
                "",
                clean,
                count=1
            ).strip()

            if remainder:
                sections[current_section].append(remainder)

            continue

        sections[current_section].append(clean)

    return sections


# ============================================================
# PATIENT INFORMATION
# ============================================================

def extract_patient_information(lines):

    data = {
        "name": None,
        "date_of_birth": None,
        "hospital_id": None,
        "admission_date": None,
        "discharge_date": None
    }

    for line in lines:

        clean = clean_ocr_text(line)

        lower = clean.lower()

        # Name
        if lower.startswith("name:"):
            data["name"] = clean.split(":", 1)[1].strip()

        # Admission date
        elif lower.startswith("admission date:"):
            value = clean.split(":", 1)[1].strip()
            data["admission_date"] = find_date(value) or value

        # Date of birth
        elif lower.startswith("date of birth:"):
            value = clean.split(":", 1)[1].strip()
            data["date_of_birth"] = find_date(value) or value

        # Discharge date
        elif lower.startswith("discharge date:"):
            value = clean.split(":", 1)[1].strip()
            data["discharge_date"] = find_date(value) or value

        # Hospital ID
        elif lower.startswith("hospital id:"):
            data["hospital_id"] = clean.split(":", 1)[1].strip()

    return data


# ============================================================
# DIAGNOSIS EXTRACTION
# ============================================================

def extract_diagnosis(lines):

    data = {
        "primary": None,
        "secondary": None
    }

    for line in lines:

        clean = clean_ocr_text(line)

        lower = clean.lower()

        if lower.startswith("primary diagnosis:"):
            value = clean.split(":", 1)[1].strip()

            if value:
                data["primary"] = value

        elif lower.startswith("secondary diagnosis:"):
            value = clean.split(":", 1)[1].strip()

            if value:
                data["secondary"] = value

        elif lower == "acute appendicitis":
            if data["primary"] is None:
                data["primary"] = clean

        elif lower == "none":
            if data["secondary"] is None:
                data["secondary"] = "None"

    return data


# ============================================================
# TREATMENT / PROCEDURE EXTRACTION
# ============================================================

def extract_treatment(lines):

    full_text = " ".join(lines)

    procedure = None

    # Detect common procedure wording
    match = re.search(
        r"underwent an?\s+(.+?)\s+on\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2}",
        full_text,
        re.IGNORECASE
    )

    if match:
        procedure = match.group(1).strip()

    return {
        "procedure": procedure,
        "hospital_course": full_text if full_text else None
    }


# ============================================================
# MEDICATION EXTRACTION
# ============================================================

def parse_medication_line(line):

    clean = clean_ocr_text(line)

    # Ignore empty lines
    if not clean:
        return None

    # Expected format:
    #
    # Amoxicillin: 500 mg, orally, three times a day for 7 days

    if ":" not in clean:
        return None

    medication_name, details = clean.split(":", 1)

    medication_name = medication_name.strip()
    details = details.strip()

    if not medication_name:
        return None

    result = {
        "medication": medication_name,
        "dosage": None,
        "route": None,
        "frequency": None,
        "duration": None,
        "instructions": None
    }

    parts = [
        p.strip()
        for p in details.split(",")
        if p.strip()
    ]

    if parts:
        result["dosage"] = parts[0]

    for part in parts[1:]:

        lower = part.lower()

        # Route
        if any(
            word in lower
            for word in [
                "oral",
                "orally",
                "intravenous",
                "iv",
                "intramuscular",
                "im",
                "topical",
                "sublingual"
            ]
        ):
            result["route"] = part

        # Duration
        elif re.search(
            r"\b\d+\s*(day|days|week|weeks|month|months)\b",
            lower
        ):
            result["duration"] = part

        # Frequency
        elif any(
            phrase in lower
            for phrase in [
                "times a day",
                "once daily",
                "twice daily",
                "three times",
                "four times",
                "every",
                "as needed"
            ]
        ):
            result["frequency"] = part

        else:
            if result["instructions"] is None:
                result["instructions"] = part
            else:
                result["instructions"] += ", " + part

    # Sometimes duration is attached to frequency
    duration_match = re.search(
        r"\bfor\s+(\d+\s*(?:day|days|week|weeks|month|months))\b",
        details,
        re.IGNORECASE
    )

    if duration_match:
        result["duration"] = duration_match.group(1)

    # Remove "for X days" from frequency
    if result["frequency"]:
        result["frequency"] = re.sub(
            r"\s+for\s+\d+\s*(?:day|days|week|weeks|month|months)\b",
            "",
            result["frequency"],
            flags=re.IGNORECASE
        ).strip()

    return result


def extract_medications(lines):

    medications = []

    for line in lines:

        clean = clean_ocr_text(line)

        # Only process likely medication lines
        if ":" not in clean:
            continue

        lower = clean.lower()

        if any(
            key in lower
            for key in [
                "diet:",
                "activity:",
                "follow-up care:",
                "wound care:",
                "medications:"
            ]
        ):
            continue

        medication = parse_medication_line(clean)

        if medication:
            medications.append(medication)

    return medications


# ============================================================
# DISCHARGE INSTRUCTIONS
# ============================================================

def extract_discharge_instructions(lines):

    data = {
        "diet": None,
        "activity": None,
        "follow_up_care": None,
        "wound_care": None,
        "medication_instruction": None,
        "signs_of_concern": None
    }

    for line in lines:

        clean = clean_ocr_text(line)

        lower = clean.lower()

        if lower.startswith("diet:"):
            data["diet"] = clean.split(":", 1)[1].strip()

        elif lower.startswith("activity:"):
            data["activity"] = clean.split(":", 1)[1].strip()

        elif lower.startswith("follow-up care:"):
            data["follow_up_care"] = clean.split(":", 1)[1].strip()

        elif lower.startswith("wound care:"):
            data["wound_care"] = clean.split(":", 1)[1].strip()

        elif lower.startswith("medications:"):
            data["medication_instruction"] = clean.split(":", 1)[1].strip()

        elif lower.startswith("signs of concern:"):
            data["signs_of_concern"] = clean.split(":", 1)[1].strip()

        else:
            # Attach continuation text to the most recent field
            for key in [
                "diet",
                "activity",
                "follow_up_care",
                "wound_care",
                "medication_instruction",
                "signs_of_concern"
            ]:
                if data[key] is not None:
                    data[key] += " " + clean
                    break

    return data


# ============================================================
# NEXT APPOINTMENT
# ============================================================

def extract_next_appointment(lines):

    data = {
        "date": None,
        "time": None,
        "location": None
    }

    for line in lines:

        clean = clean_ocr_text(line)

        lower = clean.lower()

        if lower.startswith("date:"):
            value = clean.split(":", 1)[1].strip()
            data["date"] = find_date(value) or value

        elif lower.startswith("time:"):
            value = clean.split(":", 1)[1].strip()
            data["time"] = find_time(value) or value

        elif lower.startswith("location:"):
            data["location"] = clean.split(":", 1)[1].strip()

    return data


# ============================================================
# CONTACT INFORMATION
# ============================================================

def extract_contact_information(lines):

    data = {
        "physician": None,
        "hospital": None
    }

    for line in lines:

        clean = clean_ocr_text(line)

        lower = clean.lower()

        if lower.startswith("physician:"):
            data["physician"] = clean.split(":", 1)[1].strip()

        elif lower.startswith("hospital:"):
            data["hospital"] = clean.split(":", 1)[1].strip()

    return data


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_discharge_summary(ocr_results):

    lines = []

    for item in ocr_results:

        if isinstance(item, dict):

            text = item.get("text", "")

            if text:
                clean = clean_ocr_text(text)

                if clean:
                    lines.append(clean)

    sections = split_sections(lines)

    result = {
        "document_type": "DISCHARGE_SUMMARY",

        "patient_information":
            extract_patient_information(
                sections["patient_information"]
            ),

        "diagnosis":
            extract_diagnosis(
                sections["diagnosis"]
            ),

        "treatment":
            extract_treatment(
                sections["treatment_summary"]
            ),

        "medications":
            extract_medications(
                sections["medications"]
            ),

        "discharge_instructions":
            extract_discharge_instructions(
                sections["discharge_instructions"]
            ),

        "follow_up":
            extract_next_appointment(
                sections["next_appointment"]
            ),

        "contact_information":
            extract_contact_information(
                sections["contact_information"]
            )
    }

    return result


# ============================================================
# PRINT RESULT
# ============================================================

def print_result(result):

    print()
    print("=" * 60)
    print("       DISCHARGE SUMMARY EXTRACTION")
    print("=" * 60)

    print()

    print("Document Type:")
    print(" ", result["document_type"])

    print()

    print("PATIENT")
    print("-" * 60)

    for key, value in result["patient_information"].items():
        print(f"{key}: {value}")

    print()

    print("DIAGNOSIS")
    print("-" * 60)

    print(
        "Primary:",
        result["diagnosis"]["primary"]
    )

    print(
        "Secondary:",
        result["diagnosis"]["secondary"]
    )

    print()

    print("TREATMENT")
    print("-" * 60)

    print(
        "Procedure:",
        result["treatment"]["procedure"]
    )

    print(
        "Hospital Course:",
        result["treatment"]["hospital_course"]
    )

    print()

    print("MEDICATIONS")
    print("-" * 60)

    medications = result["medications"]

    if not medications:
        print("No medications detected.")

    for index, medication in enumerate(
        medications,
        1
    ):

        print()
        print(f"{index}. {medication['medication']}")
        print("   Dosage    :", medication["dosage"])
        print("   Route     :", medication["route"])
        print("   Frequency :", medication["frequency"])
        print("   Duration  :", medication["duration"])

    print()

    print("DISCHARGE INSTRUCTIONS")
    print("-" * 60)

    for key, value in result[
        "discharge_instructions"
    ].items():

        print(f"{key}: {value}")

    print()

    print("FOLLOW-UP")
    print("-" * 60)

    for key, value in result["follow_up"].items():
        print(f"{key}: {value}")

    print()

    print("CONTACT")
    print("-" * 60)

    for key, value in result[
        "contact_information"
    ].items():

        print(f"{key}: {value}")

    print()
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("       DISCHARGE SUMMARY EXTRACTION")
    print("=" * 60)

    print()
    print("Input:", IMAGE_PATH)

    if not IMAGE_PATH.exists():

        print()
        print("ERROR: Discharge summary image not found.")
        print()
        print("Expected:")
        print(IMAGE_PATH)

        return

    print()
    print("Running OCR...")

    ocr_results = run_ocr(
        IMAGE_PATH
    )

    if not ocr_results:

        print()
        print("ERROR: OCR returned no results.")

        return

    print()
    print("OCR completed.")
    print(
        "Total OCR items:",
        len(ocr_results)
    )

    print()
    print("Extracting discharge summary...")

    result = extract_discharge_summary(
        ocr_results
    )

    print_result(result)

    # Save JSON
    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(
        "JSON saved to:",
        OUTPUT_PATH
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()