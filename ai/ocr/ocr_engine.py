
from pathlib import Path

from paddleocr import PaddleOCR


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_IMAGE = Path("ai/ocr/test_images/cbcreport.jpg")

# Minimum confidence used only for filtering extremely weak
# OCR detections.
#
# IMPORTANT:
# We keep this relatively low because medical documents can
# contain faint text. Do NOT aggressively filter OCR here.
MIN_CONFIDENCE = 0.30


# ============================================================
# OCR ENGINE
# ============================================================

class OCREngine:

    def __init__(self):

        print("=" * 60)
        print("                  OCR ENGINE")
        print("=" * 60)

        print("Initializing PaddleOCR...")

        self.ocr = PaddleOCR(
            lang="en"
        )

        print("PaddleOCR initialized.")
        print()

    # ========================================================
    # RUN OCR
    # ========================================================

    def run(self, image_path):

        image_path = Path(image_path)

        print("=" * 60)
        print("                  OCR PROCESS")
        print("=" * 60)

        if not image_path.exists():

            print("Status : ERROR")
            print(f"File not found: {image_path}")

            return []

        print(f"Input  : {image_path}")
        print("Running PaddleOCR...")
        print()

        try:

            results = self.ocr.predict(
                str(image_path)
            )

        except Exception as exc:

            print()
            print("Status : ERROR")
            print("PaddleOCR failed.")
            print(f"Reason : {exc}")

            return []

        # ----------------------------------------------------
        # Convert PaddleOCR output into our own stable format
        # ----------------------------------------------------

        all_text = []

        for result in results:

            texts = result.get(
                "rec_texts",
                []
            )

            scores = result.get(
                "rec_scores",
                []
            )

            boxes = result.get(
                "rec_polys",
                []
            )

            for index, text in enumerate(texts):

                text = str(text).strip()

                if not text:
                    continue

                # --------------------------------------------
                # Confidence
                # --------------------------------------------

                confidence = 0.0

                if index < len(scores):

                    try:

                        confidence = float(
                            scores[index]
                        )

                    except (
                        TypeError,
                        ValueError
                    ):

                        confidence = 0.0

                # --------------------------------------------
                # Bounding box
                # --------------------------------------------

                bbox = None

                if index < len(boxes):

                    bbox = self._convert_bbox(
                        boxes[index]
                    )

                # --------------------------------------------
                # Weak OCR filtering
                # --------------------------------------------

                if confidence < MIN_CONFIDENCE:

                    continue

                # --------------------------------------------
                # Calculate spatial information
                # --------------------------------------------

                x = None
                y = None
                width = None
                height = None

                if bbox:

                    x1, y1, x2, y2 = bbox

                    x = (x1 + x2) / 2
                    y = (y1 + y2) / 2

                    width = x2 - x1
                    height = y2 - y1

                # --------------------------------------------
                # Store OCR item
                # --------------------------------------------

                all_text.append({

                    "text": text,

                    "confidence": round(
                        confidence,
                        3
                    ),

                    "bbox": bbox,

                    "x": x,
                    "y": y,

                    "width": width,
                    "height": height

                })

        # ====================================================
        # SORT SPATIALLY
        # ====================================================

        all_text = self._sort_ocr_results(
            all_text
        )

        # ====================================================
        # PRINT RESULTS
        # ====================================================

        print("=" * 60)
        print("                  OCR RESULT")
        print("=" * 60)

        if not all_text:

            print("No text detected.")

        else:

            for item in all_text:

                print(
                    f"{item['text']} "
                    f"[confidence: "
                    f"{item['confidence']:.2f}]"
                )

                if item["bbox"]:

                    print(
                        f"  bbox   : "
                        f"{item['bbox']}"
                    )

                    print(
                        f"  center : "
                        f"({item['x']:.1f}, "
                        f"{item['y']:.1f})"
                    )

        print("=" * 60)

        print(
            f"Total text lines: "
            f"{len(all_text)}"
        )

        print("=" * 60)

        return all_text

    # ========================================================
    # BBOX CONVERSION
    # ========================================================

    @staticmethod
    def _convert_bbox(poly):

        """
        PaddleOCR may return polygon points such as:

        [
            [x1, y1],
            [x2, y2],
            [x3, y3],
            [x4, y4]
        ]

        Convert this into:

        [min_x, min_y, max_x, max_y]
        """

        try:

            points = []

            for point in poly:

                if len(point) >= 2:

                    x = float(point[0])
                    y = float(point[1])

                    points.append(
                        (x, y)
                    )

            if not points:

                return None

            xs = [
                point[0]
                for point in points
            ]

            ys = [
                point[1]
                for point in points
            ]

            return [
                round(min(xs), 2),
                round(min(ys), 2),
                round(max(xs), 2),
                round(max(ys), 2)
            ]

        except Exception:

            return None

    # ========================================================
    # SPATIAL SORT
    # ========================================================

    @staticmethod
    def _sort_ocr_results(items):

        """
        Sort OCR results approximately:

        top → bottom
        left → right

        We use the vertical center as the primary value.

        Small Y differences are grouped into the same row.
        """

        items = [
            item
            for item in items
            if item.get("x") is not None
            and item.get("y") is not None
        ]

        # ----------------------------------------------------
        # Sort by Y first
        # ----------------------------------------------------

        items.sort(
            key=lambda item: (
                item["y"],
                item["x"]
            )
        )

        return items


# ============================================================
# GLOBAL ENGINE
# ============================================================

_engine = None


def get_ocr_engine():

    global _engine

    if _engine is None:

        _engine = OCREngine()

    return _engine


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def run_ocr(image_path):

    engine = get_ocr_engine()

    return engine.run(
        image_path
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_ocr(
        INPUT_IMAGE
    )

