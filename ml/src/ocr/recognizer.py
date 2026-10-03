"""Prescription text/image recognition helpers.

The parser intentionally returns a confidence estimate rather than claiming clinical
certainty. Extracted values should be reviewed by the user before saving medication data.
"""
import re
from pathlib import Path


class OCRRecognizer:
    @staticmethod
    def extract_prescription_text(raw_text: str) -> dict:
        text = " ".join((raw_text or "").split())
        if not text:
            return {
                "medicine_name": "",
                "dosage": "",
                "quantity": 0,
                "frequency": "",
                "instructions": "",
                "confidence": 0.0,
                "raw_text": "",
            }

        dosage_match = re.search(r"\b(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu|units?))\b", text, re.I)
        qty_match = re.search(r"\b(?:qty|quantity|count|tablets?|capsules?|pills?)\s*[:=-]?\s*(\d+)\b", text, re.I)
        freq_match = re.search(
            r"\b(once|twice|thrice|\d+\s*(?:times?|x)\s*(?:a|per)?\s*day|\d+\s*/\s*day|daily|weekly)\b",
            text,
            re.I,
        )
        medicine_match = re.search(
            r"(?:rx\s*[:=-]?\s*|medicine\s*[:=-]?\s*|drug\s*[:=-]?\s*)([A-Za-z][A-Za-z0-9-]*)",
            text,
            re.I,
        )
        if not medicine_match:
            medicine_match = re.search(r"\b([A-Za-z][A-Za-z0-9-]{2,})\s+\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu)\b", text, re.I)

        quantity = int(qty_match.group(1)) if qty_match else 0
        dosage = dosage_match.group(1) if dosage_match else ""
        frequency = freq_match.group(1) if freq_match else ""
        medicine_name = medicine_match.group(1) if medicine_match else ""
        instruction_match = re.search(r"(?:take|instructions?)\s+(.+?)(?:\.|$)", text, re.I)
        instructions = instruction_match.group(1).strip() if instruction_match else ""

        fields = sum(bool(v) for v in [medicine_name, dosage, quantity, frequency])
        confidence = round(fields / 4 * 0.9 + (0.1 if fields == 4 else 0), 2)
        return {
            "medicine_name": medicine_name,
            "dosage": dosage,
            "quantity": quantity,
            "frequency": frequency,
            "instructions": instructions,
            "confidence": confidence,
            "raw_text": text,
        }

    @staticmethod
    def extract_image(image_path: str) -> dict:
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("OCR dependencies are not installed. Run pip install -r backend/requirements/base.txt") from exc

        text = pytesseract.image_to_string(Image.open(Path(image_path)))
        result = OCRRecognizer.extract_prescription_text(text)
        result["raw_text"] = text.strip()
        return result
