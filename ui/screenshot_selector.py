"""Full-screen screenshot region selector."""

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QWidget


class ScreenshotSelector(QWidget):
    """Overlay widget that lets the user select a screenshot region."""

    region_selected = Signal(QPixmap)
    selection_cancelled = Signal()

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self._pixmap = pixmap
        self._start = QPoint()
        self._end = QPoint()
        self._selecting = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._selecting = True
            self._start = event.position().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._selecting:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton or not self._selecting:
            return

        self._selecting = False
        self._end = event.position().toPoint()
        rect = self._selection_rect()
        if rect.width() < 4 or rect.height() < 4:
            self.selection_cancelled.emit()
            self.close()
            return

        cropped = self._pixmap.copy(rect)
        self.region_selected.emit(cropped)
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)

        overlay = QColor(0, 0, 0, 110)
        painter.fillRect(self.rect(), overlay)

        rect = self._selection_rect()
        if not rect.isNull():
            painter.drawPixmap(rect, self._pixmap, rect)
            pen = QPen(QColor("#18bfd5"), 2)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

            painter.setPen(QColor("white"))
            painter.drawText(
                rect.adjusted(8, 8, -8, -8),
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                f"{rect.width()} x {rect.height()}",
            )

        painter.setPen(QColor("white"))
        painter.drawText(
            self.rect().adjusted(16, 16, -16, -16),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            "拖拽选择公式区域，Esc 取消",
        )

    def _selection_rect(self) -> QRect:
        return QRect(self._start, self._end).normalized().intersected(self.rect())
