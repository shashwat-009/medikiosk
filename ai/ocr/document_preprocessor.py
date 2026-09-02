from pathlib import Path
import pymupdf


SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png"}
SUPPORTED_PDFS = {".pdf"}


def prepare_document(file_path, output_dir="prepared"):
    path = Path(file_path)
    output = Path(output_dir)

    output.mkdir(parents=True, exist_ok=True)

    extension = path.suffix.lower()

    if extension in SUPPORTED_IMAGES:
        print(f"Image detected: {path.name}")

        return [str(path)]

    if extension in SUPPORTED_PDFS:
        print(f"PDF detected: {path.name}")

        pdf = pymupdf.open(path)
        image_paths = []

        for page_number, page in enumerate(pdf):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            image_path = output / f"{path.stem}_page_{page_number + 1}.png"

            pix.save(str(image_path))
            image_paths.append(str(image_path))

            print(f"Converted page {page_number + 1}: {image_path}")

        pdf.close()

        return image_paths

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Allowed: JPG, JPEG, PNG, PDF"
    )


if __name__ == "__main__":

    test_file = "test_images/prescription.png"

    print("=" * 60)
    print("          DOCUMENT PREPARATION")
    print("=" * 60)

    try:
        images = prepare_document(test_file)

        print("\nPrepared files:")

        for image in images:
            print(f"  {image}")

        print("\nStatus: SUCCESS")

    except Exception as e:
        print(f"\nStatus: FAILED")
        print(f"Error: {e}")

    print("=" * 60)