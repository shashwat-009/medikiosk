import cv2
import os


INPUT_PATH = "test_images/prescription.png"
OUTPUT_DIR = "processed"


def enhance_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        print("ERROR: Could not read image.")
        return None

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    height, width = image.shape[:2]

    # -------------------------------------------------
    # 1. Upscale only when resolution is too low
    # -------------------------------------------------
    if width < 800 or height < 800:

        scale = 2

        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    # -------------------------------------------------
    # 2. Convert to grayscale
    # -------------------------------------------------
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # -------------------------------------------------
    # 3. Improve contrast
    # -------------------------------------------------
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # -------------------------------------------------
    # 4. Light denoising
    # -------------------------------------------------
    enhanced = cv2.fastNlMeansDenoising(
        enhanced,
        None,
        10,
        7,
        21
    )

    # -------------------------------------------------
    # 5. Save processed image
    # -------------------------------------------------
    filename = os.path.basename(image_path)
    output_path = os.path.join(
        OUTPUT_DIR,
        "enhanced_" + filename
    )

    cv2.imwrite(output_path, enhanced)

    return output_path


if __name__ == "__main__":

    print("=" * 60)
    print("             OPENCV IMAGE ENHANCEMENT")
    print("=" * 60)

    if not os.path.exists(INPUT_PATH):

        print("Status : FAILED")
        print("Reason : Input file does not exist.")

    else:

        output = enhance_image(INPUT_PATH)

        if output:

            print("Status : SUCCESS")
            print(f"Input  : {INPUT_PATH}")
            print(f"Output : {output}")

    print("=" * 60)