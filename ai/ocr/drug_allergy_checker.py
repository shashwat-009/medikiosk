
import json
import re
from pathlib import Path


# ============================================================
# DRUG / ALLERGY INTERACTION CHECKER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ------------------------------------------------------------
# FILE HELPERS
# ------------------------------------------------------------

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
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


# ------------------------------------------------------------
# DRUG CLASS KNOWLEDGE
# ------------------------------------------------------------

DRUG_CLASSES = {

    # Penicillin antibiotics
    "amoxicillin": ["penicillin", "beta-lactam", "antibiotic"],
    "ampicillin": ["penicillin", "beta-lactam", "antibiotic"],
    "penicillin": ["penicillin", "beta-lactam", "antibiotic"],

    # Cephalosporins
    "cephalexin": ["cephalosporin", "beta-lactam", "antibiotic"],
    "cefuroxime": ["cephalosporin", "beta-lactam", "antibiotic"],
    "ceftriaxone": ["cephalosporin", "beta-lactam", "antibiotic"],

    # NSAIDs
    "ibuprofen": ["nsaid", "anti-inflammatory"],
    "diclofenac": ["nsaid", "anti-inflammatory"],
    "naproxen": ["nsaid", "anti-inflammatory"],
    "aspirin": ["nsaid", "salicylate"],

    # Analgesic
    "paracetamol": ["acetaminophen", "analgesic"],
    "acetaminophen": ["acetaminophen", "analgesic"],
}


# ------------------------------------------------------------
# ALLERGY NORMALIZATION
# ------------------------------------------------------------

ALLERGY_ALIASES = {

    "penicillin": [
        "penicillin",
        "penicillins",
        "amoxicillin",
        "ampicillin"
    ],

    "beta-lactam": [
        "beta lactam",
        "beta-lactam",
        "beta lactams",
        "beta-lactam antibiotics"
    ],

    "cephalosporin": [
        "cephalosporin",
        "cephalosporins"
    ],

    "nsaid": [
        "nsaid",
        "nsaids",
        "non steroidal anti inflammatory",
        "non-steroidal anti-inflammatory"
    ],

    "aspirin": [
        "aspirin"
    ],

    "ibuprofen": [
        "ibuprofen"
    ],

    "paracetamol": [
        "paracetamol",
        "acetaminophen"
    ]
}


# ------------------------------------------------------------
# NORMALIZE ALLERGY
# ------------------------------------------------------------

def normalize_allergy(allergen):

    text = clean_text(allergen).lower()

    for canonical, aliases in ALLERGY_ALIASES.items():

        for alias in aliases:

            if alias in text:
                return canonical

    return text


# ------------------------------------------------------------
# CHECK WHETHER DRUG MATCHES ALLERGY
# ------------------------------------------------------------

def check_drug_against_allergy(drug_name, allergy_name):

    drug = clean_text(drug_name).lower()
    allergy = normalize_allergy(allergy_name)

    if not drug or not allergy:
        return None

    # Direct drug match
    if drug == allergy:
        return {
            "match": True,
            "severity": "HIGH",
            "reason": f"{drug_name} is listed as an allergy."
        }

    # Drug class match
    drug_classes = DRUG_CLASSES.get(drug, [])

    if allergy in drug_classes:

        return {
            "match": True,
            "severity": "HIGH",
            "reason": (
                f"{drug_name} belongs to the "
                f"{allergy} drug class."
            )
        }

    # Special cross-reactivity relationship
    if allergy == "beta-lactam" and "beta-lactam" in drug_classes:

        return {
            "match": True,
            "severity": "HIGH",
            "reason": (
                f"{drug_name} is a beta-lactam antibiotic "
                f"and the patient has a beta-lactam allergy."
            )
        }

    if allergy == "penicillin" and drug in [
        "amoxicillin",
        "ampicillin",
        "penicillin"
    ]:

        return {
            "match": True,
            "severity": "HIGH",
            "reason": (
                f"{drug_name} is a penicillin-class antibiotic "
                f"and the patient has a penicillin allergy."
            )
        }

    if allergy == "cephalosporin" and "cephalosporin" in drug_classes:

        return {
            "match": True,
            "severity": "HIGH",
            "reason": (
                f"{drug_name} is a cephalosporin and "
                f"the patient has a cephalosporin allergy."
            )
        }

    if allergy == "nsaid" and "nsaid" in drug_classes:

        return {
            "match": True,
            "severity": "HIGH",
            "reason": (
                f"{drug_name} is an NSAID and "
                f"the patient has an NSAID allergy."
            )
        }

    return None


# ------------------------------------------------------------
# EXTRACT MEDICATIONS
# ------------------------------------------------------------

def extract_medications(data):

    medications = data.get("medications", [])

    if not isinstance(medications, list):
        return []

    result = []

    for medication in medications:

        if isinstance(medication, str):

            name = clean_text(medication)

        elif isinstance(medication, dict):

            name = clean_text(
                medication.get("name")
                or medication.get("drug")
                or medication.get("medicine")
            )

        else:
            continue

        if name:
            result.append(name)

    return result


# ------------------------------------------------------------
# EXTRACT ALLERGIES
# ------------------------------------------------------------

def extract_allergies(data):

    allergies = data.get("allergies", [])

    if not isinstance(allergies, list):
        return []

    result = []

    for allergy in allergies:

        if isinstance(allergy, str):

            allergen = clean_text(allergy)
            reaction = None

        elif isinstance(allergy, dict):

            allergen = clean_text(
                allergy.get("allergen")
                or allergy.get("name")
                or allergy.get("drug")
            )

            reaction = clean_text(
                allergy.get("reaction")
                or allergy.get("response")
            )

        else:
            continue

        if allergen:

            result.append({
                "allergen": allergen,
                "reaction": reaction if reaction else None
            })

    return result


# ------------------------------------------------------------
# CHECK INTERACTIONS
# ------------------------------------------------------------

def check_interactions(medications, allergies):

    interactions = []

    for medication in medications:

        for allergy in allergies:

            result = check_drug_against_allergy(
                medication,
                allergy["allergen"]
            )

            if result and result["match"]:

                interactions.append({
                    "medication": medication,
                    "allergen": allergy["allergen"],
                    "reaction": allergy["reaction"],
                    "severity": result["severity"],
                    "interaction": "DRUG_ALLERGY",
                    "warning": result["reason"]
                })

    return interactions


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print("             DRUG / ALLERGY INTERACTION")
    print("=" * 60)

    input_file = BASE_DIR / "clinical_entities.json"

    if not input_file.exists():

        print("\nERROR: clinical_entities.json not found.")
        print("Run clinical_entity_extractor.py first.")
        return

    print("\nReading clinical entities...")

    data = load_json("clinical_entities.json")

    medications = extract_medications(data)
    allergies = extract_allergies(data)

    print(f"Medications found: {len(medications)}")
    print(f"Allergies found   : {len(allergies)}")

    print("\nMedications:")

    for medication in medications:
        print(f" - {medication}")

    print("\nAllergies:")

    if allergies:

        for allergy in allergies:

            print(
                f" - {allergy['allergen']}"
                f" | reaction: {allergy['reaction']}"
            )

    else:

        print(" - No allergies recorded.")

    # --------------------------------------------------------
    # INTERACTION CHECK
    # --------------------------------------------------------

    print("\nChecking drug-allergy interactions...")

    interactions = check_interactions(
        medications,
        allergies
    )

    # --------------------------------------------------------
    # BUILD RESULT
    # --------------------------------------------------------

    if interactions:

        status = "WARNING"

    else:

        status = "NO_INTERACTION"

    result = {

        "module": "Drug-Allergy Interaction Detection",

        "status": status,

        "medications_checked": medications,

        "allergies_checked": allergies,

        "interaction_count": len(interactions),

        "interactions": interactions
    }

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output_file = BASE_DIR / "drug_allergy_results.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("          DRUG / ALLERGY CHECK RESULT")
    print("=" * 60)

    if interactions:

        print("\n⚠ ALLERGY INTERACTIONS DETECTED")

        for index, interaction in enumerate(
            interactions,
            start=1
        ):

            print(f"\n{index}. {interaction['medication']}")

            print(
                f"   Allergy : "
                f"{interaction['allergen']}"
            )

            print(
                f"   Reaction: "
                f"{interaction['reaction']}"
            )

            print(
                f"   Severity: "
                f"{interaction['severity']}"
            )

            print(
                f"   Warning : "
                f"{interaction['warning']}"
            )

    else:

        print("\nNo drug-allergy interactions detected.")

    print("\n" + "=" * 60)

    print(
        f"Interactions detected: "
        f"{len(interactions)}"
    )

    print(
        f"Status: {status}"
    )

    print("=" * 60)

    print(
        f"\nJSON saved to: "
        f"{output_file.name}"
    )


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":
    main()

