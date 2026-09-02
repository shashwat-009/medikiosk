import json
import re
from pathlib import Path

from ocr_engine import OCREngine


# ============================================================
# CONFIG
# ============================================================

INPUT_IMAGE = "test_images/cbcreport.jpg"
OUTPUT_FILE = "output/cbc_parsed.json"


# ============================================================
# LAYOUT PARSER
# ============================================================

class LayoutParser:

    def __init__(self, image_path):
        self.image_path = image_path
        self.ocr = OCREngine()
        self.lines = []

    # --------------------------------------------------------
    # RUN OCR
    # --------------------------------------------------------

    def parse(self):

        print("=" * 60)
        print("                LAYOUT PARSER")
        print("=" * 60)

        print("Running OCR...")

        self.lines = self.ocr.run(self.image_path)

        print()
        print("=" * 60)
        print("             STRUCTURED PARSING")
        print("=" * 60)

        result = self.parse_cbc()

        self.print_result(result)
        self.save_json(result)

        return result

    # --------------------------------------------------------
    # NORMALIZE OCR TEXT
    # --------------------------------------------------------

    def clean(self, text):

        if text is None:
            return ""

        text = str(text).strip()

        # Common OCR mistakes
        replacements = {
            "00 - 06": "0 - 6",
            "00-06": "0 - 6",
            "00 - 10": "0 - 10",
            "00-10": "0 - 10",
            "00 - 02": "0 - 2",
            "00-02": "0 - 2",
            "32.50-34.50": "32.50 - 34.50",
            "13.00 -17.00": "13.00 - 17.00",
            "83 -101": "83 - 101",
            "27-32": "27 - 32",
            "40-50": "40 - 50",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    # --------------------------------------------------------
    # GET TEXT ONLY
    # --------------------------------------------------------

    def texts(self):

        output = []

        for item in self.lines:

            if isinstance(item, dict):
                text = item.get("text", "")
            else:
                text = str(item)

            text = self.clean(text)

            if text:
                output.append(text)

        return output

    # --------------------------------------------------------
    # FIND EXACT TEXT
    # --------------------------------------------------------

    def find_index(self, text_list, target):

        target = target.lower()

        for i, text in enumerate(text_list):

            if text.lower().strip() == target:
                return i

        return -1

    # --------------------------------------------------------
    # FIND TEXT CONTAINING KEYWORD
    # --------------------------------------------------------

    def find_contains(self, text_list, keyword):

        keyword = keyword.lower()

        for i, text in enumerate(text_list):

            if keyword in text.lower():
                return i

        return -1

    # --------------------------------------------------------
    # FIND NEXT VALUE
    # --------------------------------------------------------

    def find_next_number(self, text_list, start_index):

        number_pattern = re.compile(
            r"^\s*\d+(?:\.\d+)?\s*$"
        )

        for i in range(start_index + 1, len(text_list)):

            text = text_list[i].strip()

            if number_pattern.match(text):
                return text

        return None

    # --------------------------------------------------------
    # FIND REFERENCE RANGE
    # --------------------------------------------------------

    def find_reference(self, text_list, start_index):

        pattern = re.compile(
            r"^\s*\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\s*$"
        )

        for i in range(start_index + 1, len(text_list)):

            text = text_list[i].strip()

            if pattern.match(text):
                return text

        return None

    # --------------------------------------------------------
    # FIND UNIT
    # --------------------------------------------------------

    def find_unit(self, text_list, start_index):

        units = [
            "g/dL",
            "mill/cumm",
            "fL",
            "pg",
            "%",
            "cumm",
        ]

        # Search only a reasonable distance
        for i in range(start_index + 1,
                       min(start_index + 8, len(text_list))):

            text = text_list[i].strip()

            for unit in units:

                if text.lower() == unit.lower():
                    return unit

        return None

    # --------------------------------------------------------
    # PARSE TEST ROW USING OCR POSITIONS
    # --------------------------------------------------------

    def parse_test_from_position(
        self,
        test_name,
        test_y,
        tolerance=45
    ):

        """
        Uses X/Y positions from OCR.

        Expected CBC columns:

        Investigation -> x ~ 0
        Result        -> x ~ 350
        Status        -> x ~ 500
        Reference     -> x ~ 660
        Unit          -> x ~ 940
        """

        result = None
        reference = None
        unit = None

        candidates = []

        for item in self.lines:

            if not isinstance(item, dict):
                continue

            text = self.clean(item.get("text", ""))

            bbox = item.get("bbox")

            if not text or not bbox:
                continue

            try:
                x1, y1, x2, y2 = bbox

                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

            except Exception:
                continue

            # Only look around the test's Y position
            if abs(center_y - test_y) <= tolerance:

                candidates.append(
                    {
                        "text": text,
                        "x": center_x,
                        "y": center_y,
                    }
                )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        number_pattern = re.compile(
            r"^\d+(?:\.\d+)?$"
        )

        for item in candidates:

            if 300 <= item["x"] <= 450:

                if number_pattern.match(item["text"]):

                    result = item["text"]
                    break

        # ----------------------------------------------------
        # REFERENCE
        # ----------------------------------------------------

        reference_pattern = re.compile(
            r"^\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?$"
        )

        for item in candidates:

            if 620 <= item["x"] <= 850:

                if reference_pattern.match(item["text"]):

                    reference = item["text"]
                    break

        # ----------------------------------------------------
        # UNIT
        # ----------------------------------------------------

        for item in candidates:

            if item["x"] >= 900:

                text = item["text"]

                if text.lower() in [
                    "g/dl",
                    "mill/cumm",
                    "fl",
                    "pg",
                    "%",
                    "cumm",
                ]:

                    unit = text
                    break

        return {
            "name": test_name,
            "result": result,
            "reference": reference,
            "unit": unit,
        }

    # --------------------------------------------------------
    # CBC PARSER
    # --------------------------------------------------------

    def parse_cbc(self):

        print()
        print("=" * 60)
        print("             STRUCTURED CBC RESULT")
        print("=" * 60)

        # ----------------------------------------------------
        # GET PATIENT
        # ----------------------------------------------------

        patient_name = None
        age = None
        sex = None
        uhid = None

        for item in self.lines:

            if not isinstance(item, dict):
                continue

            text = self.clean(item.get("text", ""))

            if not text:
                continue

            # Patient name
            if (
                patient_name is None
                and re.match(
                    r"^[A-Za-z]+(?:\s+[A-Za-z.]+)+$",
                    text
                )
                and "pathology" not in text.lower()
                and "complete blood" not in text.lower()
            ):
                if item.get("bbox", [999])[0] < 300:
                    patient_name = text

            # Age
            match = re.search(
                r"Age\s*:\s*(\d+)",
                text,
                re.IGNORECASE
            )

            if match:
                age = int(match.group(1))

            # Sex
            match = re.search(
                r"Sex\s*:\s*(Male|Female)",
                text,
                re.IGNORECASE
            )

            if match:
                sex = match.group(1).capitalize()

            # UHID
            match = re.search(
                r"UHID\s*:\s*(.+)",
                text,
                re.IGNORECASE
            )

            if match:
                uhid = match.group(1).strip()

        # ----------------------------------------------------
        # CBC TEST DEFINITIONS
        # ----------------------------------------------------

        test_names = [
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

        tests = []

        # ----------------------------------------------------
        # FIND EACH TEST BY OCR POSITION
        # ----------------------------------------------------

        for test_name in test_names:

            test_y = None

            for item in self.lines:

                if not isinstance(item, dict):
                    continue

                text = self.clean(item.get("text", ""))

                if text.lower() == test_name.lower():

                    bbox = item.get("bbox")

                    if bbox:
                        test_y = (
                            float(bbox[1]) +
                            float(bbox[3])
                        ) / 2

                    break

            # If OCR didn't exactly match test name,
            # try partial matching.
            if test_y is None:

                for item in self.lines:

                    if not isinstance(item, dict):
                        continue

                    text = self.clean(
                        item.get("text", "")
                    ).lower()

                    if (
                        test_name.lower() in text
                        or text in test_name.lower()
                    ):

                        bbox = item.get("bbox")

                        if bbox:
                            test_y = (
                                float(bbox[1]) +
                                float(bbox[3])
                            ) / 2

                        break

            # ------------------------------------------------
            # TEST FOUND
            # ------------------------------------------------

            if test_y is not None:

                parsed = self.parse_test_from_position(
                    test_name,
                    test_y,
                    tolerance=35
                )

                tests.append(parsed)

            else:

                tests.append(
                    {
                        "name": test_name,
                        "result": None,
                        "reference": None,
                        "unit": None,
                    }
                )

        # ----------------------------------------------------
        # SPECIAL FIXES
        # ----------------------------------------------------

        # RDW unit is %
        for test in tests:

            if test["name"] == "RDW":

                if test["result"] is not None:
                    test["unit"] = "%"

        # ----------------------------------------------------
        # PRINT
        # ----------------------------------------------------

        result = {
            "document_type": "CBC",

            "patient": {
                "name": patient_name,
                "age": age,
                "sex": sex,
                "uhid": uhid,
            },

            "tests": tests,
        }

        return result

    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    def print_result(self, result):

        print()
        print("=" * 60)
        print("             STRUCTURED CBC RESULT")
        print("=" * 60)

        print()
        print("DOCUMENT TYPE:")
        print(result["document_type"])

        print()
        print("PATIENT:")
        print(json.dumps(
            result["patient"],
            indent=2
        ))

        print()
        print("TESTS:")

        for test in result["tests"]:

            print("-" * 60)

            print(test["name"])

            print(
                f"  Result    : {test['result']}"
            )

            print(
                f"  Reference : {test['reference']}"
            )

            print(
                f"  Unit      : {test['unit']}"
            )

        print()
        print("=" * 60)

        print(
            f"Total tests extracted: "
            f"{len(result['tests'])}"
        )

        print("=" * 60)

    # --------------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------------

    def save_json(self, result):

        output_path = Path(OUTPUT_FILE)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                indent=2,
                ensure_ascii=False
            )

        print()
        print(
            f"JSON saved to: {output_path}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = LayoutParser(
        INPUT_IMAGE
    )

    parser.parse()


if __name__ == "__main__":
    main()