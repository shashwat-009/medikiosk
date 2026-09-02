from paddleocr import PaddleOCR

# Initialize OCR
ocr = PaddleOCR(lang="en")

# Prescription image
image_path = "test_images/discharge.jpg"

# Run OCR
result = ocr.predict(image_path)

# Print clean result
print("\n" + "=" * 60)
print("                 PRESCRIPTION")
print("=" * 60)

for res in result:
    texts = res.get("rec_texts", [])

    for text in texts:
        text = text.strip()

        if text:
            print(text)

print("=" * 60)
