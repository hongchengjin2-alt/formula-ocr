"""Main application window."""

from io import BytesIO

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QClipboard,
    QColor,
    QGuiApplication,
    QImage,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QComboBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.converter import (
    create_word_doc,
    create_word_doc_multi,
    latex_to_mathml,
    latex_to_omml_string,
    render_latex_preview,
)
from core.recognizer import DEFAULT_ENGINE, available_engines, get_recognizer
from ui.image_drop_label import ImageDropLabel
from ui.screenshot_selector import ScreenshotSelector
from ui.theme import APP_NAME, APP_SUBTITLE, LOGO_PATH
from ui.workers import RecognizeWorker, qimage_to_pil


class MainWindow(QMainWindow):
    """Formula OCR main window."""

    def __init__(self, app_clipboard: QClipboard):
        super().__init__()
        self.app_clipboard = app_clipboard
        self.recognizer = get_recognizer(DEFAULT_ENGINE)
        self.current_latex = ""
        self.current_mathml = ""
        self.current_omml = ""
        self.current_qimage: QImage | None = None
        self._worker: RecognizeWorker | None = None
        self._selector: ScreenshotSelector | None = None
        self._history: list[str] = []

        self._init_ui()
        self._init_toolbar()
        self._init_statusbar()

    def _init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1080, 720)
        self.resize(1280, 820)

        central = QWidget()
        central.setObjectName("RootSurface")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 12, 18, 12)
        main_layout.setSpacing(12)

        main_layout.addWidget(self._build_header())

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter)

        left_panel = self._panel("input")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        left_layout.addWidget(self._section_block("图片输入", "拖拽 / 粘贴 / 截图"))

        engine_layout = QHBoxLayout()
        engine_layout.setSpacing(10)
        engine_layout.addWidget(self._field_label("识别引擎"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(available_engines())
        self.engine_combo.setCurrentText(DEFAULT_ENGINE)
        self.engine_combo.currentTextChanged.connect(self._on_engine_changed)
        engine_layout.addWidget(self.engine_combo)
        left_layout.addLayout(engine_layout)

        self.image_label = ImageDropLabel()
        self.image_label.image_loaded.connect(self._on_image_loaded)
        left_layout.addWidget(self.image_label)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        self.screenshot_btn = QPushButton("截图识别")
        self.screenshot_btn.setProperty("variant", "primary")
        self.screenshot_btn.setFixedHeight(42)
        self.screenshot_btn.clicked.connect(self._take_screenshot)
        action_layout.addWidget(self.screenshot_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setProperty("variant", "ghost")
        self.clear_btn.setFixedHeight(42)
        self.clear_btn.clicked.connect(self._clear_all)
        action_layout.addWidget(self.clear_btn)
        left_layout.addLayout(action_layout)

        left_layout.addWidget(self._workflow_card())
        left_layout.addStretch()

        splitter.addWidget(left_panel)

        right_panel = self._panel("output")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        latex_header = QHBoxLayout()
        latex_header.addWidget(self._section_block("LaTeX", "可编辑"))
        latex_header.addStretch()
        self.copy_latex_btn = QPushButton("复制")
        self.copy_latex_btn.setFixedHeight(36)
        self.copy_latex_btn.clicked.connect(self._copy_latex)
        self.copy_latex_btn.setEnabled(False)
        latex_header.addWidget(self.copy_latex_btn)
        right_layout.addLayout(latex_header)

        self.latex_edit = QTextEdit()
        self.latex_edit.setObjectName("LatexEdit")
        self.latex_edit.setMaximumHeight(92)
        self.latex_edit.setPlaceholderText("识别结果会显示在这里")
        self.latex_edit.textChanged.connect(self._on_latex_changed)
        right_layout.addWidget(self.latex_edit)

        right_layout.addWidget(self._section_block("公式预览", "渲染校验"))
        self.preview_label = QLabel()
        self.preview_label.setObjectName("PreviewSurface")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(150)
        self.preview_label.setText("等待识别")
        self.preview_label.setProperty("previewState", "empty")
        right_layout.addWidget(self.preview_label)

        code_header = QHBoxLayout()
        code_header.addWidget(self._section_block("格式转换", "MathML / Word"))
        code_header.addStretch()
        self.copy_mathml_btn = QPushButton("复制 MathML")
        self.copy_mathml_btn.setFixedHeight(36)
        self.copy_mathml_btn.clicked.connect(self._copy_mathml)
        self.copy_mathml_btn.setEnabled(False)
        code_header.addWidget(self.copy_mathml_btn)

        self.copy_omml_btn = QPushButton("复制 Word")
        self.copy_omml_btn.setFixedHeight(36)
        self.copy_omml_btn.clicked.connect(self._copy_omml)
        self.copy_omml_btn.setEnabled(False)
        code_header.addWidget(self.copy_omml_btn)
        right_layout.addLayout(code_header)

        self.code_tabs = QTabWidget()
        self.mathml_edit = self._readonly_code_edit(
            "由 LaTeX 转换生成的 MathML。"
        )
        self.omml_edit = self._readonly_code_edit(
            "用于 Word 原生公式的 OMML。"
        )
        self.code_tabs.addTab(self.mathml_edit, "MathML")
        self.code_tabs.addTab(self.omml_edit, "Word OMML")
        self.code_tabs.setMinimumHeight(190)
        right_layout.addWidget(self.code_tabs)

        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        self.export_word_btn = QPushButton("导出 Word")
        self.export_word_btn.setProperty("variant", "primary")
        self.export_word_btn.setFixedHeight(42)
        self.export_word_btn.clicked.connect(self._export_word)
        self.export_word_btn.setEnabled(False)
        export_layout.addWidget(self.export_word_btn)

        self.export_multi_btn = QPushButton("导出历史")
        self.export_multi_btn.setFixedHeight(42)
        self.export_multi_btn.clicked.connect(self._export_multi_word)
        self.export_multi_btn.setEnabled(False)
        export_layout.addWidget(self.export_multi_btn)
        right_layout.addLayout(export_layout)

        right_layout.addWidget(self._section_block("历史记录", "去重保存"))
        self.history_edit = QTextEdit()
        self.history_edit.setObjectName("HistoryEdit")
        self.history_edit.setReadOnly(True)
        self.history_edit.setPlaceholderText("暂无记录")
        self.history_edit.setMaximumHeight(110)
        right_layout.addWidget(self.history_edit)

        splitter.addWidget(right_panel)
        splitter.setSizes([430, 850])

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("AppHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        logo_label = QLabel()
        logo_label.setObjectName("LogoBadge")
        logo_label.setFixedSize(96, 96)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setPixmap(self._logo_pixmap(74))
        layout.addWidget(logo_label)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        title = QLabel(APP_NAME)
        title.setObjectName("AppTitle")
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setObjectName("AppSubtitle")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        content_layout.addLayout(text_layout)

        chip_layout = QHBoxLayout()
        chip_layout.setSpacing(8)
        chip_layout.addWidget(self._header_chip("截图"))
        chip_layout.addWidget(self._header_chip("粘贴"))
        chip_layout.addWidget(self._header_chip("Word 导出"))
        chip_layout.addStretch()
        content_layout.addLayout(chip_layout)

        layout.addLayout(content_layout, 1)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(10)
        metrics.setVerticalSpacing(10)
        metrics.addWidget(
            self._header_metric_card("引擎", DEFAULT_ENGINE.upper()), 0, 0
        )
        metrics.addWidget(self._header_metric_card("格式", "LaTeX / Word"), 0, 1)
        metrics.addWidget(self._header_metric_card("输入", "图片 / 截屏"), 1, 0)
        self.status_chip = QLabel("就绪")
        self.status_chip.setObjectName("StatusBadge")
        self.status_chip.setProperty("state", "idle")
        self.status_chip.setAlignment(Qt.AlignCenter)
        metrics.addWidget(self.status_chip, 1, 1)
        layout.addLayout(metrics)
        return header

    def _panel(self, role: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")
        frame.setProperty("panelRole", role)
        return frame

    def _section_block(self, title: str, hint: str) -> QWidget:
        block = QWidget()
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        hint_label = QLabel(hint)
        hint_label.setObjectName("SectionHint")

        layout.addWidget(title_label)
        layout.addWidget(hint_label)
        return block

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FieldLabel")
        return label

    def _support_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("SupportLabel")
        return label

    def _header_chip(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FeatureChip")
        return label

    def _header_metric_card(self, title: str, value: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("HeaderMetricCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("HeaderMetricTitle")
        value_label = QLabel(value)
        value_label.setObjectName("HeaderMetricValue")
        value_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return frame

    def _workflow_card(self) -> QFrame:
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(8)

        title = QLabel("快捷操作")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        tags = QHBoxLayout()
        tags.setSpacing(8)
        tags.addWidget(self._quick_tag("Ctrl+V"))
        tags.addWidget(self._quick_tag("截图"))
        tags.addWidget(self._quick_tag("Word"))
        tags.addStretch()
        layout.addLayout(tags)
        hint = QLabel("识别后可直接复制或导出")
        hint.setObjectName("QuickHint")
        layout.addWidget(hint)
        return card

    def _quick_tag(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("QuickTag")
        return label

    def _logo_pixmap(self, size: int) -> QPixmap:
        pixmap = QPixmap(str(LOGO_PATH))
        if not pixmap.isNull():
            return pixmap.scaled(
                size,
                size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        fallback = QPixmap(size, size)
        fallback.fill(Qt.transparent)
        painter = QPainter(fallback)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(size), float(size), 20.0, 20.0)
        painter.fillPath(path, QColor("#113d77"))
        painter.end()
        return fallback

    def _readonly_code_edit(self, placeholder: str) -> QTextEdit:
        edit = QTextEdit()
        edit.setObjectName("CodeEdit")
        edit.setReadOnly(True)
        edit.setPlaceholderText(placeholder)
        return edit

    def _init_toolbar(self):
        toolbar = QToolBar("工具")
        toolbar.setObjectName("TopToolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        open_action = QAction("打开图片", self)
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        clear_action = QAction("清空", self)
        clear_action.triggered.connect(self._clear_all)
        toolbar.addAction(clear_action)

    def _init_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        self._set_status_chip("就绪", "idle")

    def _on_engine_changed(self, engine: str):
        try:
            self.recognizer = get_recognizer(engine)
            self._refresh_header_engine(engine)
            self.status_bar.showMessage(f"识别引擎已切换为 {engine}", 3000)
        except Exception as e:
            QMessageBox.warning(self, "引擎错误", str(e))
            self.engine_combo.blockSignals(True)
            self.engine_combo.setCurrentText(DEFAULT_ENGINE)
            self.engine_combo.blockSignals(False)
            self.recognizer = get_recognizer(DEFAULT_ENGINE)
            self._refresh_header_engine(DEFAULT_ENGINE)

    def _on_image_loaded(self, image: QImage):
        self.current_qimage = image
        self._run_recognition(image)

    def _run_recognition(self, image: QImage):
        if self._worker and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.quit()
            self._worker.wait(500)

        pil_image = qimage_to_pil(image)
        self._worker = RecognizeWorker(self.recognizer, pil_image)
        self._worker.finished.connect(self._on_recognize_done)
        self._worker.error.connect(self._on_recognize_error)
        self._worker.status.connect(lambda msg: self.status_bar.showMessage(msg))
        self._worker.start()

        self.status_bar.showMessage("正在识别...")
        self._set_status_chip("识别中", "running")
        self._set_output_enabled(False)

    def _on_recognize_done(self, latex: str):
        self.current_latex = latex
        self.latex_edit.blockSignals(True)
        self.latex_edit.setPlainText(latex)
        self.latex_edit.blockSignals(False)

        self._refresh_outputs(latex)
        self._add_to_history(latex)
        self.status_bar.showMessage(f"识别完成，{len(latex)} 个 LaTeX 字符")
        self._set_status_chip("完成", "success")

    def _on_recognize_error(self, msg: str):
        self.status_bar.showMessage(msg)
        self._set_status_chip("失败", "error")
        QMessageBox.warning(self, "识别失败", msg)

    def _on_latex_changed(self):
        latex = self.latex_edit.toPlainText().strip()
        self.current_latex = latex
        self._refresh_outputs(latex)

    def _refresh_outputs(self, latex: str):
        if not latex:
            self.preview_label.clear()
            self.preview_label.setText("等待识别")
            self.preview_label.setProperty("previewState", "empty")
            self.preview_label.style().unpolish(self.preview_label)
            self.preview_label.style().polish(self.preview_label)
            self.mathml_edit.clear()
            self.omml_edit.clear()
            self.current_mathml = ""
            self.current_omml = ""
            self._set_output_enabled(False)
            return

        self._update_preview(latex)
        self._update_xml_outputs(latex)
        self._set_output_enabled(True)

    def _update_xml_outputs(self, latex: str):
        try:
            self.current_mathml = latex_to_mathml(latex)
            self.current_omml = latex_to_omml_string(latex)
            self.mathml_edit.setPlainText(self.current_mathml)
            self.omml_edit.setPlainText(self.current_omml)
            self.copy_mathml_btn.setEnabled(True)
            self.copy_omml_btn.setEnabled(True)
        except Exception as e:
            self.current_mathml = ""
            self.current_omml = ""
            self.mathml_edit.setPlainText(f"MathML 转换失败：{e}")
            self.omml_edit.clear()
            self.copy_mathml_btn.setEnabled(False)
            self.copy_omml_btn.setEnabled(False)
            self.status_bar.showMessage(f"XML 转换失败：{e}")

    def _update_preview(self, latex: str):
        try:
            pil_img = render_latex_preview(latex)
            buf = BytesIO()
            pil_img.save(buf, format="PNG")
            buf.seek(0)
            qimg = QImage()
            qimg.loadFromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            scaled = pixmap.scaled(
                self._label_available_size(self.preview_label),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.preview_label.setPixmap(scaled)
            self.preview_label.setProperty("previewState", "filled")
            self.preview_label.style().unpolish(self.preview_label)
            self.preview_label.style().polish(self.preview_label)
        except Exception as e:
            self.preview_label.setText(f"预览失败：{e}")
            self.preview_label.setProperty("previewState", "empty")
            self.preview_label.style().unpolish(self.preview_label)
            self.preview_label.style().polish(self.preview_label)

    def _label_available_size(self, label: QLabel) -> QSize:
        margins = label.contentsMargins()
        width = max(1, label.width() - margins.left() - margins.right())
        height = max(1, label.height() - margins.top() - margins.bottom())
        return QSize(width, height)

    def _set_output_enabled(self, enabled: bool):
        self.copy_latex_btn.setEnabled(enabled)
        self.export_word_btn.setEnabled(enabled)
        self.export_multi_btn.setEnabled(bool(self._history))
        self.copy_mathml_btn.setEnabled(enabled and bool(self.current_mathml))
        self.copy_omml_btn.setEnabled(enabled and bool(self.current_omml))

    def _add_to_history(self, latex: str):
        if latex not in self._history:
            self._history.append(latex)
            self.history_edit.append(f"[{len(self._history)}] {latex}\n")
        self.export_multi_btn.setEnabled(bool(self._history))

    def _copy_latex(self):
        latex = self.latex_edit.toPlainText().strip()
        if latex:
            self.app_clipboard.setText(latex)
            self.status_bar.showMessage("已复制 LaTeX", 3000)

    def _copy_mathml(self):
        if self.current_mathml:
            self.app_clipboard.setText(self.current_mathml)
            self.status_bar.showMessage("已复制 MathML", 3000)

    def _copy_omml(self):
        if self.current_omml:
            self.app_clipboard.setText(self.current_omml)
            self.status_bar.showMessage("已复制 Word OMML", 3000)

    def _export_word(self):
        if not self.current_latex:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 Word 文档",
            "formula.docx",
            "Word document (*.docx)",
        )
        if path:
            try:
                create_word_doc(self.current_latex, path)
                self.status_bar.showMessage(f"已保存：{path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "导出失败", str(e))

    def _export_multi_word(self):
        if not self._history:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 Word 文档",
            "formulas.docx",
            "Word document (*.docx)",
        )
        if path:
            try:
                create_word_doc_multi(self._history, path)
                self.status_bar.showMessage(
                    f"已导出 {len(self._history)} 条公式：{path}", 5000
                )
            except Exception as e:
                QMessageBox.critical(self, "导出失败", str(e))

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开公式图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff)",
        )
        if path:
            image = QImage(path)
            if not image.isNull():
                self.image_label._load_image(image)
            else:
                QMessageBox.warning(self, "打开失败", "所选文件不是图片。")

    def _take_screenshot(self):
        self.showMinimized()
        QTimer.singleShot(500, self._capture_screen)

    def _capture_screen(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            self.showNormal()
            return

        screenshot = screen.grabWindow(0)
        self._selector = ScreenshotSelector(screenshot)
        self._selector.region_selected.connect(self._on_screenshot_region_selected)
        self._selector.selection_cancelled.connect(self._on_screenshot_cancelled)
        self._selector.showFullScreen()
        self._selector.raise_()
        self._selector.activateWindow()
        self.status_bar.showMessage("拖拽选择公式区域")

    def _on_screenshot_region_selected(self, pixmap: QPixmap):
        self.showNormal()
        self.image_label._load_image(pixmap.toImage())
        self.status_bar.showMessage("截图已载入，正在识别...", 3000)

    def _on_screenshot_cancelled(self):
        self.showNormal()
        self.status_bar.showMessage("已取消截图", 3000)

    def _clear_all(self):
        self.image_label.clear_image()
        self.latex_edit.clear()
        self.preview_label.clear()
        self.preview_label.setText("等待识别")
        self.preview_label.setProperty("previewState", "empty")
        self.preview_label.style().unpolish(self.preview_label)
        self.preview_label.style().polish(self.preview_label)
        self.mathml_edit.clear()
        self.omml_edit.clear()
        self.history_edit.clear()
        self.current_latex = ""
        self.current_mathml = ""
        self.current_omml = ""
        self.current_qimage = None
        self._history.clear()
        self._set_output_enabled(False)
        self._set_status_chip("就绪", "idle")
        self.status_bar.showMessage("已清空")

    def _set_status_chip(self, text: str, state: str):
        self.status_chip.setText(text)
        self.status_chip.setProperty("state", state)
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)

    def _refresh_header_engine(self, engine: str):
        for frame in self.findChildren(QFrame, "HeaderMetricCard"):
            values = frame.findChildren(QLabel, "HeaderMetricValue")
            titles = frame.findChildren(QLabel, "HeaderMetricTitle")
            if values and titles and titles[0].text() == "引擎":
                values[0].setText(engine.upper())
                break
