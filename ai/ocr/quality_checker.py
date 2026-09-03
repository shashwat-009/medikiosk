import cv2
import os

IMAGE_PATH = "test_images/prescription.png"


def check_quality(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return {
            "status": "INVALID",
            "reason": "Image could not be read."
        }

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur detection using Laplacian variance
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Brightness
    brightness = gray.mean()

    # Contrast
    contrast = gray.std()

    issues = []

    if width < 800 or height < 800:
        issues.append("low_resolution")

    if blur_score < 50:
        issues.append("blurry")

    if brightness < 60:
        issues.append("too_dark")

    if brightness > 220:
        issues.append("too_bright")

    if contrast < 30:
        issues.append("low_contrast")

    if issues:
        status = "NEEDS_ENHANCEMENT"
    else:
        status = "GOOD"

    return {
        "status": status,
        "width": width,
        "height": height,
        "blur_score": round(blur_score, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "issues": issues
    }


if __name__ == "__main__":

    print("=" * 60)
    print("             DOCUMENT QUALITY CHECK")
    print("=" * 60)

    if not os.path.exists(IMAGE_PATH):
        print("Status : INVALID")
        print("Reason : File does not exist.")
    else:
        result = check_quality(IMAGE_PATH)

        print(f"Status      : {result['status']}")
        print(f"Resolution  : {result.get('width')} x {result.get('height')}")
        print(f"Blur Score  : {result.get('blur_score')}")
        print(f"Brightness  : {result.get('brightness')}")
        print(f"Contrast    : {result.get('contrast')}")
        print(f"Issues      : {result.get('issues')}")

    print("=" * 60)