import json
from pathlib import Path

from ocr_engine import run_ocr


# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_PATH = Path("test_images/cbcreport.jpg")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "ocr_result.json"


# ============================================================
# JSON EXPORT
# ============================================================

def save_ocr_json(ocr_results, image_path, output_file):

    output_data = {
        "ocr": {
            "engine": "PaddleOCR",
            "source_file": str(image_path),
            "text_lines": len(ocr_results)
        },
        "results": ocr_results
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_data


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("                  OCR JSON EXPORT")
    print("=" * 60)

    print()
    print(f"Input : {IMAGE_PATH}")

    if not IMAGE_PATH.exists():

        print()
        print("Status : ERROR")
        print(f"File not found: {IMAGE_PATH}")

        return

    print()
    print("Running OCR...")

    ocr_results = run_ocr(IMAGE_PATH)

    if not ocr_results:

        print()
        print("Status : FAILED")
        print("Reason : No OCR text detected.")

        return

    print()
    print("OCR completed.")

    # ========================================================
    # SAVE OCR RESULT
    # ========================================================

    data = save_ocr_json(
        ocr_results,
        IMAGE_PATH,
        OUTPUT_FILE
    )

    print()
    print("=" * 60)
    print("                  JSON RESULT")
    print("=" * 60)

    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )
    )

    print()
    print("=" * 60)
    print(f"Saved to : {OUTPUT_FILE}")
    print("Status   : SUCCESS")
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()