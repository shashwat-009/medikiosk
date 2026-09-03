
import json
import re
from pathlib import Path


# ============================================================
# CLINICAL ENTITY EXTRACTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# HELPERS
# ============================================================

def load_json(filename):
    path = BASE_DIR / filename

    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"Warning: Could not read {filename}: {e}")
        return {}


def clean_text(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# MEDICATION EXTRACTION
# ============================================================

def extract_medications(data):

    medications = []

    source_medications = data.get("medications", [])

    if not isinstance(source_medications, list):
        return medications

    for med in source_medications:

        # ----------------------------------------------------
        # Medication stored as simple string
        # ----------------------------------------------------

        if isinstance(med, str):

            medications.append({
                "name": clean_text(med),
                "dosage": None,
                "route": None,
                "frequency": None,
                "duration": None,
                "instructions": None
            })

            continue

        # ----------------------------------------------------
        # Medication stored as dictionary
        # ----------------------------------------------------

        if not isinstance(med, dict):
            continue

        medication_name = (
            med.get("name")
            or med.get("medication")
            or med.get("drug")
            or med.get("medicine")
        )

        medications.append({
            "name": clean_text(medication_name),
            "dosage": clean_text(med.get("dosage")),
            "route": clean_text(med.get("route")),
            "frequency": clean_text(med.get("frequency")),
            "duration": clean_text(med.get("duration")),
            "instructions": clean_text(med.get("instructions"))
        })

    return medications


# ============================================================
# DIAGNOSIS EXTRACTION
# ============================================================

def extract_diagnoses(data):

    diagnoses = []

    diagnosis = data.get("diagnosis")

    # --------------------------------------------------------
    # Diagnosis stored as string
    # --------------------------------------------------------

    if isinstance(diagnosis, str):

        if diagnosis.strip():

            diagnoses.append({
                "name": clean_text(diagnosis),
                "type": "primary"
            })

    # --------------------------------------------------------
    # Diagnosis stored as dictionary
    # --------------------------------------------------------

    elif isinstance(diagnosis, dict):

        primary = diagnosis.get("primary")

        if primary and str(primary).lower() != "none":

            diagnoses.append({
                "name": clean_text(primary),
                "type": "primary"
            })

        secondary = diagnosis.get("secondary")

        # Secondary diagnoses stored as list
        if isinstance(secondary, list):

            for item in secondary:

                if item and str(item).lower() != "none":

                    diagnoses.append({
                        "name": clean_text(item),
                        "type": "secondary"
                    })

        # Secondary diagnosis stored as string
        elif secondary:

            if str(secondary).lower() != "none":

                diagnoses.append({
                    "name": clean_text(secondary),
                    "type": "secondary"
                })

    return diagnoses


# ============================================================
# PROCEDURE EXTRACTION
# ============================================================

def extract_procedures(data):

    procedures = []

    treatment = data.get("treatment", {})

    # --------------------------------------------------------
    # Treatment stored as dictionary
    # --------------------------------------------------------

    if isinstance(treatment, dict):

        procedure = treatment.get("procedure")

        if procedure:

            procedures.append({
                "name": clean_text(procedure)
            })

    # --------------------------------------------------------
    # Treatment stored as string
    # --------------------------------------------------------

    elif isinstance(treatment, str):

        if treatment.strip():

            procedures.append({
                "name": clean_text(treatment)
            })

    return procedures


# ============================================================
# LAB EXTRACTION
# ============================================================

def extract_labs(data):

    labs = []

    source_labs = data.get("labs", [])

    if not isinstance(source_labs, list):
        return labs

    for lab in source_labs:

        if not isinstance(lab, dict):
            continue

        reference_range = (
            lab.get("reference_range")
            or lab.get("range")
        )

        labs.append({
            "name": clean_text(
                lab.get("name")
                or lab.get("test")
                or lab.get("analyte")
            ),

            "value": lab.get("value"),

            "unit": clean_text(
                lab.get("unit")
            ),

            "reference_range": reference_range,

            "status": clean_text(
                lab.get("status")
            ),

            "abnormal": lab.get(
                "abnormal",
                False
            ),

            "risk_flag": clean_text(
                lab.get("risk_flag")
            )
        })

    return labs


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_dates(data):

    dates = {}

    # --------------------------------------------------------
    # Actual discharge extractor structure
    #
    # patient_information:
    #   admission_date
    #   discharge_date
    #   date_of_birth
    # --------------------------------------------------------

    patient_information = data.get(
        "patient_information",
        {}
    )

    if isinstance(patient_information, dict):

        if patient_information.get("admission_date"):

            dates["admission_date"] = clean_text(
                patient_information.get(
                    "admission_date"
                )
            )

        if patient_information.get("discharge_date"):

            dates["discharge_date"] = clean_text(
                patient_information.get(
                    "discharge_date"
                )
            )

        if patient_information.get("date_of_birth"):

            dates["date_of_birth"] = clean_text(
                patient_information.get(
                    "date_of_birth"
                )
            )

    # --------------------------------------------------------
    # Generic patient structure
    # --------------------------------------------------------

    patient = data.get(
        "patient",
        {}
    )

    if isinstance(patient, dict):

        if patient.get("admission_date"):

            dates["admission_date"] = clean_text(
                patient.get(
                    "admission_date"
                )
            )

        if patient.get("discharge_date"):

            dates["discharge_date"] = clean_text(
                patient.get(
                    "discharge_date"
                )
            )

        if patient.get("date_of_birth"):

            dates["date_of_birth"] = clean_text(
                patient.get(
                    "date_of_birth"
                )
            )

    # --------------------------------------------------------
    # Follow-up
    # --------------------------------------------------------

    follow_up = data.get(
        "follow_up",
        {}
    )

    if isinstance(follow_up, dict):

        if follow_up.get("date"):

            dates["follow_up_date"] = clean_text(
                follow_up.get("date")
            )

        if follow_up.get("time"):

            dates["follow_up_time"] = clean_text(
                follow_up.get("time")
            )

    return dates


# ============================================================
# PATIENT EXTRACTION
# ============================================================

def extract_patient(data):

    # --------------------------------------------------------
    # Actual discharge extractor structure
    # --------------------------------------------------------

    patient = data.get(
        "patient_information",
        {}
    )

    # --------------------------------------------------------
    # Fallback to generic patient structure
    # --------------------------------------------------------

    if not isinstance(patient, dict) or not patient:

        patient = data.get(
            "patient",
            {}
        )

    if not isinstance(patient, dict):

        return {}

    return {
        "name": clean_text(
            patient.get("name")
        ),

        "date_of_birth": clean_text(
            patient.get("date_of_birth")
        ),

        "hospital_id": clean_text(
            patient.get("hospital_id")
        )
    }


# ============================================================
# DISCHARGE SUMMARY PROCESSING
# ============================================================

def process_discharge(data):

    result = {

        "source":
            "discharge_extraction_result.json",

        "document_type":
            "DISCHARGE_SUMMARY",

        "patient":
            extract_patient(data),

        "diagnoses":
            extract_diagnoses(data),

        "medications":
            extract_medications(data),

        "procedures":
            extract_procedures(data),

        "laboratory_results":
            extract_labs(data),

        "dates":
            extract_dates(data)
    }

    return result


# ============================================================
# LAB REPORT PROCESSING
# ============================================================

def process_lab(data):

    tests = []

    # --------------------------------------------------------
    # Lab extractor may return a list directly
    # --------------------------------------------------------

    if isinstance(data, list):

        source_tests = data

    else:

        source_tests = data.get(
            "tests",
            []
        )

    if not isinstance(source_tests, list):

        source_tests = []

    for test in source_tests:

        if not isinstance(test, dict):
            continue

        reference_range = (
            test.get("reference_range")
            or test.get("range")
        )

        tests.append({

            "name": clean_text(
                test.get("name")
                or test.get("test")
                or test.get("analyte")
            ),

            "value": test.get(
                "value"
            ),

            "unit": clean_text(
                test.get("unit")
            ),

            "reference_range":
                reference_range,

            "status": clean_text(
                test.get("status")
            ),

            "abnormal": test.get(
                "abnormal",
                False
            ),

            "risk_flag": clean_text(
                test.get("risk_flag")
            )
        })

    return {

        "source":
            "lab_extraction_result.json",

        "document_type":
            "LAB_REPORT",

        "laboratory_results":
            tests
    }


# ============================================================
# REMOVE DUPLICATE MEDICATIONS
# ============================================================

def remove_duplicate_medications(
    medications
):

    unique_medications = []

    seen = set()

    for medication in medications:

        name = medication.get(
            "name"
        )

        if not name:
            continue

        key = str(name).lower().strip()

        if key in seen:
            continue

        seen.add(key)

        unique_medications.append(
            medication
        )

    return unique_medications


# ============================================================
# REMOVE DUPLICATE DIAGNOSES
# ============================================================

def remove_duplicate_diagnoses(
    diagnoses
):

    unique_diagnoses = []

    seen = set()

    for diagnosis in diagnoses:

        name = diagnosis.get(
            "name"
        )

        if not name:
            continue

        key = str(name).lower().strip()

        if key in seen:
            continue

        seen.add(key)

        unique_diagnoses.append(
            diagnosis
        )

    return unique_diagnoses


# ============================================================
# REMOVE DUPLICATE LAB RESULTS
# ============================================================

def remove_duplicate_labs(
    labs
):

    unique_labs = []

    seen = set()

    for lab in labs:

        name = lab.get(
            "name"
        )

        value = lab.get(
            "value"
        )

        key = (
            str(name).lower().strip()
            if name
            else ""
        )

        key = (
            key,
            str(value)
        )

        if key in seen:
            continue

        seen.add(key)

        unique_labs.append(
            lab
        )

    return unique_labs


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "          CLINICAL ENTITY EXTRACTION"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Input files
    # --------------------------------------------------------

    discharge_file = (
        BASE_DIR
        / "discharge_extraction_result.json"
    )

    lab_file = (
        BASE_DIR
        / "lab_extraction_result.json"
    )

    # --------------------------------------------------------
    # Final unified structure
    # --------------------------------------------------------

    final_result = {

        "module":
            "Clinical Entity Extraction",

        "status":
            "SUCCESS",

        "patient": {},

        "diagnoses": [],

        "medications": [],

        "laboratory_results": [],

        "procedures": [],

        "dates": {},

        "sources": []
    }

    # ========================================================
    # DISCHARGE SUMMARY
    # ========================================================

    if discharge_file.exists():

        print(
            "\nReading discharge extraction..."
        )

        discharge_data = load_json(
            "discharge_extraction_result.json"
        )

        if discharge_data:

            discharge_result = (
                process_discharge(
                    discharge_data
                )
            )

            final_result["sources"].append(
                "discharge_extraction_result.json"
            )

            # Patient
            if discharge_result.get(
                "patient"
            ):

                final_result[
                    "patient"
                ] = discharge_result[
                    "patient"
                ]

            # Diagnoses
            final_result[
                "diagnoses"
            ].extend(
                discharge_result[
                    "diagnoses"
                ]
            )

            # Medications
            final_result[
                "medications"
            ].extend(
                discharge_result[
                    "medications"
                ]
            )

            # Labs
            final_result[
                "laboratory_results"
            ].extend(
                discharge_result[
                    "laboratory_results"
                ]
            )

            # Procedures
            final_result[
                "procedures"
            ].extend(
                discharge_result[
                    "procedures"
                ]
            )

            # Dates
            final_result[
                "dates"
            ].update(
                discharge_result[
                    "dates"
                ]
            )

    else:

        print(
            "\nDischarge extraction file not found."
        )

    # ========================================================
    # LAB REPORT
    # ========================================================

    if lab_file.exists():

        print(
            "Reading lab extraction..."
        )

        lab_data = load_json(
            "lab_extraction_result.json"
        )

        if lab_data:

            lab_result = process_lab(
                lab_data
            )

            final_result[
                "sources"
            ].append(
                "lab_extraction_result.json"
            )

            final_result[
                "laboratory_results"
            ].extend(
                lab_result[
                    "laboratory_results"
                ]
            )

    else:

        print(
            "Lab extraction file not found."
        )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    final_result[
        "medications"
    ] = remove_duplicate_medications(
        final_result[
            "medications"
        ]
    )

    final_result[
        "diagnoses"
    ] = remove_duplicate_diagnoses(
        final_result[
            "diagnoses"
        ]
    )

    final_result[
        "laboratory_results"
    ] = remove_duplicate_labs(
        final_result[
            "laboratory_results"
        ]
    )

    # ========================================================
    # SAVE JSON
    # ========================================================

    output_file = (
        BASE_DIR
        / "clinical_entities.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_result,
            f,
            indent=4,
            ensure_ascii=False
        )

    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print("\n" + "=" * 60)
    print(
        "        CLINICAL ENTITY EXTRACTION RESULT"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Patient
    # --------------------------------------------------------

    print("\nPatient:")

    print(
        json.dumps(
            final_result["patient"],
            indent=2,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Diagnoses
    # --------------------------------------------------------

    print("\nDiagnoses:")

    if final_result["diagnoses"]:

        for item in final_result[
            "diagnoses"
        ]:

            print(
                " -",
                item
            )

    else:

        print(" - None")

    # --------------------------------------------------------
    # Medications
    # --------------------------------------------------------

    print("\nMedications:")

    if final_result["medications"]:

        for item in final_result[
            "medications"
        ]:

            print(
                " -",
                item
            )

    else:

        print(" - None")

    # --------------------------------------------------------
    # Laboratory results
    # --------------------------------------------------------

    print("\nLaboratory Results:")

    if final_result[
        "laboratory_results"
    ]:

        for item in final_result[
            "laboratory_results"
        ]:

            print(
                " -",
                item
            )

    else:

        print(" - None")

    # --------------------------------------------------------
    # Procedures
    # --------------------------------------------------------

    print("\nProcedures:")

    if final_result["procedures"]:

        for item in final_result[
            "procedures"
        ]:

            print(
                " -",
                item
            )

    else:

        print(" - None")

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    print("\nDates:")

    if final_result["dates"]:

        for key, value in final_result[
            "dates"
        ].items():

            print(
                f" - {key}: {value}"
            )

    else:

        print(" - None")

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    print("\nSources:")

    for source in final_result[
        "sources"
    ]:

        print(
            f" - {source}"
        )

    # ========================================================
    # STATUS
    # ========================================================

    print("\n" + "=" * 60)
    print("STATUS: SUCCESS")
    print("=" * 60)

    print(
        f"\nJSON saved to: {output_file.name}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()

