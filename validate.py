"""Smoke tests for Formula OCR core functionality.

Usage:
    python validate.py
    python validate.py --image path/to/formula.png
"""

import argparse
import tempfile
from pathlib import Path

from PIL import Image
from PySide6.QtGui import QColor, QImage

from core.converter import (
    create_word_doc,
    latex_to_mathml,
    latex_to_omml_string,
    normalize_latex,
    render_latex_preview,
)
from core.recognizer import DEFAULT_ENGINE, get_recognizer
from ui.workers import qimage_to_pil


def validate_conversion() -> None:
    latex = r"\frac{a}{b}+x^2"
    mathml = latex_to_mathml(latex)
    omml = latex_to_omml_string(latex)
    assert "<math" in mathml, "MathML output is missing <math>"
    assert "<m:oMath" in omml, "OMML output is missing <m:oMath>"

    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "formula.docx"
        create_word_doc(latex, str(output))
        assert output.exists() and output.stat().st_size > 0, "Word export failed"


def validate_script_normalization() -> None:
    cases = {
        r"x_i": r"x_{i}",
        r"x^2_i": r"x^{2}_{i}",
        r"x_ij": r"x_{ij}",
        r"x^ij": r"x^{ij}",
        r"e^-x": r"e^{-x}",
        r"10^-3": r"10^{-3}",
    }
    for source, expected in cases.items():
        actual = normalize_latex(source)
        assert actual == expected, f"{source} normalized to {actual}, expected {expected}"
        latex_to_mathml(actual)


def validate_preview_rendering() -> None:
    latex = (
        r"\hat { Y } _{ t } [ n , f , c ] = \tilde { Y } _{ t }"
        r" [ n , f , c ] \cdot \Big ( \sigma _{ ( n , c ) } ^{ M }"
        r" + \varepsilon \Big ) + \mu _{ ( n , c ) } ^{ M }"
    )
    preview = render_latex_preview(latex)
    assert preview.width > 0 and preview.height > 0, "LaTeX preview rendering failed"


def validate_qimage_conversion() -> None:
    image = QImage(32, 16, QImage.Format.Format_RGB32)
    image.fill(QColor("white"))
    pil_image = qimage_to_pil(image)
    assert pil_image.mode == "RGBA", "QImage conversion returned the wrong mode"
    assert pil_image.size == (32, 16), "QImage conversion returned the wrong size"


def validate_ocr(image_path: Path, engine: str) -> None:
    image = Image.open(image_path)
    recognizer = get_recognizer(engine)
    latex = recognizer.recognize(image)
    assert latex, "OCR returned an empty result"
    print(f"{engine} OCR LaTeX: {latex}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image",
        type=Path,
        help="Optional formula image for a real Pix2Tex OCR smoke test.",
    )
    parser.add_argument(
        "--engine",
        default=DEFAULT_ENGINE,
        choices=["pix2tex", "unimernet"],
        help="OCR engine to use with --image.",
    )
    args = parser.parse_args()

    validate_conversion()
    validate_script_normalization()
    validate_preview_rendering()
    validate_qimage_conversion()

    if args.image:
        validate_ocr(args.image, args.engine)

    print("Validation passed.")


if __name__ == "__main__":
    main()
