"""Image drop/paste label widget."""

from pathlib import Path

from PySide6.QtCore import QMimeData, QSize, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImage, QKeyEvent, QPixmap
from PySide6.QtWidgets import QFileDialog, QLabel


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff")


class ImageDropLabel(QLabel):
    """A QLabel that accepts images via drag-and-drop, paste, or file dialog."""

    image_loaded = Signal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(300, 300)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setObjectName("ImageDropZone")
        self._original_image: QImage | None = None
        self._set_placeholder()

    def _set_placeholder(self):
        self.setText(
            "拖入公式图片\n\n"
            "支持 Ctrl+V 粘贴，或点击选择"
        )
        self.setProperty("dragActive", False)
        self.setProperty("imageState", "empty")
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)
        mime: QMimeData = event.mimeData()
        if mime.hasImage():
            image = QImage(mime.imageData())
            self._load_image(image)
            return

        if mime.hasUrls():
            for url in mime.urls():
                path = url.toLocalFile()
                if path and Path(path).suffix.lower() in IMAGE_EXTENSIONS:
                    image = QImage(path)
                    if not image.isNull():
                        self._load_image(image)
                        break

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().dragLeaveEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            clipboard = self.window().app_clipboard
            if clipboard and clipboard.mimeData().hasImage():
                image = clipboard.image()
                if not image.isNull():
                    self._load_image(image)
                    return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "选择公式图片",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff)",
            )
            if path:
                image = QImage(path)
                if not image.isNull():
                    self._load_image(image)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._original_image is not None:
            self._set_pixmap(self._original_image)

    def _set_pixmap(self, image: QImage):
        pixmap = QPixmap.fromImage(image)
        scaled = pixmap.scaled(
            self._available_size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.setPixmap(scaled)

    def _available_size(self) -> QSize:
        margins = self.contentsMargins()
        width = max(1, self.width() - margins.left() - margins.right())
        height = max(1, self.height() - margins.top() - margins.bottom())
        return QSize(width, height)

    def _load_image(self, image: QImage):
        """Display the image and emit signal."""
        self._original_image = image
        self._set_pixmap(image)
        self.setProperty("dragActive", False)
        self.setProperty("imageState", "loaded")
        self.setText("")
        self.style().unpolish(self)
        self.style().polish(self)
        self.image_loaded.emit(image)

    def clear_image(self):
        self._original_image = None
        self.clear()
        self._set_placeholder()
