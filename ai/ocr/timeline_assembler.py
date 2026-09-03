
import json
import re
from pathlib import Path
from datetime import datetime


# ============================================================
# MEDICAL TIMELINE ASSEMBLY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "clinical_entities.json"
OUTPUT_FILE = BASE_DIR / "medical_timeline.json"


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def load_json(path):
    if not path.exists():
        print(f"ERROR: File not found: {path.name}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read {path.name}: {e}")
        return {}


def clean_text(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_date(date_string):
    """
    Converts common date formats into a datetime object.

    Examples:
        August 1 2024
        August 7. 2024
        August 14 2024
    """

    if not date_string:
        return None

    value = clean_text(date_string)

    # Remove OCR punctuation around dates
    value = re.sub(r"(?<=\d)\.", "", value)

    formats = [
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def date_for_sort(date_string):
    parsed = parse_date(date_string)

    if parsed:
        return parsed

    # Unknown dates go to the end
    return datetime.max


# ------------------------------------------------------------
# EVENT CREATION
# ------------------------------------------------------------

def create_event(
    date,
    event_type,
    description,
    details=None
):
    event = {
        "date": clean_text(date),
        "event_type": event_type,
        "description": clean_text(description)
    }

    if details:
        event["details"] = details

    return event


# ------------------------------------------------------------
# ADMISSION / DISCHARGE / FOLLOW-UP
# ------------------------------------------------------------

def add_date_events(data, timeline):

    dates = data.get("dates", {})

    if not isinstance(dates, dict):
        return

    # Admission
    admission_date = dates.get("admission_date")

    if admission_date:
        timeline.append(
            create_event(
                admission_date,
                "ADMISSION",
                "Patient admitted to hospital."
            )
        )

    # Discharge
    discharge_date = dates.get("discharge_date")

    if discharge_date:
        timeline.append(
            create_event(
                discharge_date,
                "DISCHARGE",
                "Patient discharged from hospital."
            )
        )

    # Follow-up
    follow_up_date = dates.get("follow_up_date")
    follow_up_time = dates.get("follow_up_time")

    if follow_up_date:

        description = "Follow-up appointment scheduled."

        details = {}

        if follow_up_time:
            details["time"] = follow_up_time

        timeline.append(
            create_event(
                follow_up_date,
                "FOLLOW_UP",
                description,
                details if details else None
            )
        )


# ------------------------------------------------------------
# DIAGNOSES
# ------------------------------------------------------------

def add_diagnosis_events(data, timeline):

    diagnoses = data.get("diagnoses", [])

    if not isinstance(diagnoses, list):
        return

    # Diagnosis does not necessarily have its own date.
    # Attach it to admission date when available.
    admission_date = data.get("dates", {}).get("admission_date")

    for diagnosis in diagnoses:

        if not isinstance(diagnosis, dict):
            continue

        name = diagnosis.get("name")

        if not name:
            continue

        diagnosis_type = diagnosis.get(
            "type",
            "unknown"
        )

        details = {
            "diagnosis_type": diagnosis_type
        }

        timeline.append(
            create_event(
                admission_date,
                "DIAGNOSIS",
                f"Diagnosis recorded: {name}.",
                details
            )
        )


# ------------------------------------------------------------
# PROCEDURES
# ------------------------------------------------------------

def add_procedure_events(data, timeline):

    procedures = data.get("procedures", [])

    if not isinstance(procedures, list):
        return

    # Procedure date may not exist in clinical_entities.json.
    # Use admission date as fallback if necessary.
    procedure_date = data.get("dates", {}).get(
        "admission_date"
    )

    for procedure in procedures:

        if not isinstance(procedure, dict):
            continue

        name = procedure.get("name")

        if not name:
            continue

        timeline.append(
            create_event(
                procedure_date,
                "PROCEDURE",
                f"Procedure performed: {name}."
            )
        )


# ------------------------------------------------------------
# MEDICATIONS
# ------------------------------------------------------------

def add_medication_events(data, timeline):

    medications = data.get("medications", [])

    if not isinstance(medications, list):
        return

    # Medication start date is not explicitly available.
    # Use discharge date as the most appropriate available date.
    medication_date = data.get("dates", {}).get(
        "discharge_date"
    )

    for medication in medications:

        if not isinstance(medication, dict):
            continue

        name = medication.get("name")

        if not name:
            continue

        details = {
            "dosage": medication.get("dosage"),
            "route": medication.get("route"),
            "frequency": medication.get("frequency"),
            "duration": medication.get("duration"),
            "instructions": medication.get("instructions")
        }

        # Remove empty values
        details = {
            key: value
            for key, value in details.items()
            if value is not None
        }

        timeline.append(
            create_event(
                medication_date,
                "MEDICATION",
                f"Medication prescribed: {name}.",
                details
            )
        )


# ------------------------------------------------------------
# LABORATORY RESULTS
# ------------------------------------------------------------

def add_lab_events(data, timeline):

    labs = data.get(
        "laboratory_results",
        []
    )

    if not isinstance(labs, list):
        return

    # Lab date is not currently included in the entity output.
    # Use admission date as fallback.
    lab_date = data.get("dates", {}).get(
        "admission_date"
    )

    for lab in labs:

        if not isinstance(lab, dict):
            continue

        name = lab.get("name")

        if not name:
            continue

        value = lab.get("value")
        unit = lab.get("unit")
        status = lab.get("status")
        abnormal = lab.get("abnormal", False)
        reference_range = lab.get(
            "reference_range"
        )

        details = {
            "value": value,
            "unit": unit,
            "reference_range": reference_range,
            "status": status,
            "abnormal": abnormal,
            "risk_flag": lab.get("risk_flag")
        }

        details = {
            key: value
            for key, value in details.items()
            if value is not None
        }

        if abnormal:
            description = (
                f"Abnormal laboratory result: {name}."
            )
        else:
            description = (
                f"Laboratory result recorded: {name}."
            )

        timeline.append(
            create_event(
                lab_date,
                "LAB_RESULT",
                description,
                details
            )
        )


# ------------------------------------------------------------
# SORT TIMELINE
# ------------------------------------------------------------

def sort_timeline(timeline):

    timeline.sort(
        key=lambda event: (
            date_for_sort(event.get("date")),
            event.get("event_type", "")
        )
    )

    return timeline


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def create_summary(timeline):

    summary = {
        "total_events": len(timeline),
        "event_counts": {
            "ADMISSION": 0,
            "DIAGNOSIS": 0,
            "PROCEDURE": 0,
            "LAB_RESULT": 0,
            "MEDICATION": 0,
            "DISCHARGE": 0,
            "FOLLOW_UP": 0
        }
    }

    for event in timeline:

        event_type = event.get(
            "event_type"
        )

        if event_type in summary["event_counts"]:
            summary["event_counts"][event_type] += 1

    return summary


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print("             MEDICAL TIMELINE ASSEMBLY")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD CLINICAL ENTITIES
    # --------------------------------------------------------

    print("\nReading clinical entities...")

    data = load_json(INPUT_FILE)

    if not data:
        print("\nERROR: clinical_entities.json is empty or invalid.")
        return

    # --------------------------------------------------------
    # BUILD TIMELINE
    # --------------------------------------------------------

    timeline = []

    print("Adding admission/discharge/follow-up events...")
    add_date_events(data, timeline)

    print("Adding diagnosis events...")
    add_diagnosis_events(data, timeline)

    print("Adding procedure events...")
    add_procedure_events(data, timeline)

    print("Adding medication events...")
    add_medication_events(data, timeline)

    print("Adding laboratory events...")
    add_lab_events(data, timeline)

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    sort_timeline(timeline)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = create_summary(timeline)

    final_result = {
        "module": "Medical Timeline Assembly",
        "status": "SUCCESS",
        "source": "clinical_entities.json",
        "summary": summary,
        "timeline": timeline
    }

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_result,
            f,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("              MEDICAL TIMELINE")
    print("=" * 60)

    for index, event in enumerate(
        timeline,
        start=1
    ):

        print(
            f"\n{index}. "
            f"[{event.get('date')}] "
            f"{event.get('event_type')}"
        )

        print(
            f"   {event.get('description')}"
        )

        if event.get("details"):

            for key, value in event["details"].items():
                print(
                    f"   {key}: {value}"
                )

    # --------------------------------------------------------
    # SUMMARY DISPLAY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("TIMELINE SUMMARY")
    print("=" * 60)

    print(
        f"Total events: "
        f"{summary['total_events']}"
    )

    for event_type, count in summary[
        "event_counts"
    ].items():

        if count > 0:
            print(
                f"{event_type}: {count}"
            )

    print("\n" + "=" * 60)
    print("STATUS: SUCCESS")
    print("=" * 60)

    print(
        f"\nJSON saved to: "
        f"{OUTPUT_FILE.name}"
    )


if __name__ == "__main__":
    main()

