"""Background worker threads for OCR."""

from PIL import Image
from PySide6.QtCore import QThread, Signal


class RecognizeWorker(QThread):
    """Run formula recognition in a background thread."""

    finished = Signal(str)
    error = Signal(str)
    status = Signal(str)

    def __init__(self, recognizer, image: Image.Image, parent=None):
        super().__init__(parent)
        self.recognizer = recognizer
        self.image = image

    def run(self):
        try:
            self.status.emit("正在识别...")
            latex = self.recognizer.recognize(self.image)
            if not latex:
                self.error.emit(
                    "未识别到公式，请换一张更清晰的图片。"
                )
            else:
                self.finished.emit(latex)
        except Exception as e:
            self.error.emit(f"识别失败：{e}")


def qimage_to_pil(qimage) -> Image.Image:
    """Convert QImage to PIL Image."""
    qimage = qimage.convertToFormat(qimage.Format.Format_RGBA8888)
    buffer = bytes(qimage.bits()[:qimage.sizeInBytes()])
    return Image.frombuffer(
        "RGBA",
        (qimage.width(), qimage.height()),
        buffer,
        "raw",
        "RGBA",
        qimage.bytesPerLine(),
        1,
    ).copy()
