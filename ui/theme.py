"""Shared styling and assets for the desktop UI."""

from pathlib import Path

from core.paths import resource_path


APP_NAME = "公式识别"
APP_SUBTITLE = "Math OCR"

ASSETS_DIR = resource_path("assets")
LOGO_PATH = ASSETS_DIR / "math_ocr_logo.svg"


def app_stylesheet() -> str:
    return """
        QMainWindow {
            background: #edf4f9;
            color: #12263f;
        }
        QWidget#RootSurface {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #f7fbff,
                stop: 0.48 #eef5fb,
                stop: 1 #edf2f7
            );
        }
        QWidget#AppHeader {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #081b38,
                stop: 0.5 #123d77,
                stop: 1 #18bfd5
            );
            border: 1px solid #6ca6d3;
            border-radius: 12px;
        }
        QLabel#LogoBadge {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.20);
            border-radius: 10px;
            padding: 8px;
        }
        QLabel#AppTitle {
            color: #f8fdff;
            font-family: "Microsoft YaHei UI";
            font-size: 28px;
            font-weight: 700;
        }
        QLabel#AppSubtitle {
            color: #d4eaff;
            font-size: 12px;
        }
        QLabel#FeatureChip {
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 8px;
            color: #f2fbff;
            font-size: 11px;
            font-weight: 600;
            padding: 5px 10px;
        }
        QLabel#StatusBadge {
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            padding: 8px 14px;
        }
        QLabel#StatusBadge[state="idle"] {
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.22);
            color: #eefaff;
        }
        QLabel#StatusBadge[state="running"] {
            background: #fff0cf;
            border: 1px solid #ffd492;
            color: #885600;
        }
        QLabel#StatusBadge[state="success"] {
            background: #daf9ee;
            border: 1px solid #97e7c8;
            color: #0a6a58;
        }
        QLabel#StatusBadge[state="error"] {
            background: #ffe1e1;
            border: 1px solid #efabab;
            color: #982f3b;
        }
        QFrame#HeaderMetricCard {
            background: rgba(8, 20, 40, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 8px;
        }
        QLabel#HeaderMetricTitle {
            color: #8cc6ef;
            font-size: 11px;
            font-weight: 600;
        }
        QLabel#HeaderMetricValue {
            color: #f3fbff;
            font-size: 13px;
            font-weight: 700;
        }
        QFrame#Panel {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #d5e3ee;
            border-radius: 10px;
        }
        QFrame#Panel[panelRole="input"] {
            background: rgba(249, 253, 255, 0.96);
        }
        QFrame#Panel[panelRole="output"] {
            background: rgba(255, 255, 255, 0.98);
        }
        QLabel#SectionTitle {
            color: #14304f;
            font-family: "Microsoft YaHei UI";
            font-size: 15px;
            font-weight: 700;
        }
        QLabel#SectionHint {
            color: #6d8197;
            font-size: 11px;
        }
        QLabel#FieldLabel {
            color: #5d7085;
            font-size: 12px;
            font-weight: 600;
        }
        QLabel#SupportLabel {
            color: #7f91a3;
            font-size: 11px;
        }
        QFrame#QuickCard {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #f8fcff,
                stop: 1 #eef6fb
            );
            border: 1px solid #d8e6ef;
            border-radius: 8px;
        }
        QLabel#QuickTag {
            background: #ffffff;
            border: 1px solid #d6e5ee;
            border-radius: 7px;
            color: #1d4f7d;
            font-size: 11px;
            font-weight: 700;
            padding: 5px 10px;
        }
        QLabel#QuickHint {
            color: #6b7f95;
            font-size: 11px;
        }
        QLabel#ImageDropZone {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #f8fdff,
                stop: 1 #eef7fb
            );
            border: 2px dashed #8db7d2;
            border-radius: 10px;
            color: #325372;
            font-family: "Microsoft YaHei UI";
            font-size: 15px;
            font-weight: 700;
            padding: 20px;
        }
        QLabel#ImageDropZone[dragActive="true"] {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #eefaff,
                stop: 1 #d9f5fb
            );
            border: 2px solid #22bfd6;
            color: #124a73;
        }
        QLabel#ImageDropZone[imageState="loaded"] {
            background: #fbfeff;
            border: 1px solid #83cfe0;
            padding: 12px;
        }
        QPushButton {
            background: #f7fbfe;
            border: 1px solid #c8d9e6;
            border-radius: 8px;
            color: #17324f;
            font-size: 13px;
            font-weight: 700;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background: #eef7fc;
            border-color: #a9c5d8;
        }
        QPushButton:pressed {
            background: #e3f0f8;
            border-color: #96b7ce;
        }
        QPushButton[variant="primary"] {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #0c2c55,
                stop: 0.6 #186bc4,
                stop: 1 #15c5d7
            );
            border: 1px solid #125d9d;
            color: #ffffff;
        }
        QPushButton[variant="primary"]:hover {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #0a2547,
                stop: 0.6 #165da9,
                stop: 1 #12acc0
            );
            border-color: #104f88;
        }
        QPushButton[variant="ghost"] {
            background: rgba(17, 52, 88, 0.04);
            border: 1px solid #d3e2ec;
            color: #1f4d7a;
        }
        QPushButton:disabled,
        QPushButton[variant="primary"]:disabled,
        QPushButton[variant="ghost"]:disabled {
            background: #eef3f7;
            border-color: #d6e0e7;
            color: #9aabba;
        }
        QComboBox {
            background: #ffffff;
            border: 1px solid #cddbe6;
            border-radius: 8px;
            color: #17324f;
            font-size: 13px;
            padding: 8px 12px;
        }
        QComboBox:hover,
        QComboBox:focus {
            border-color: #79bdd0;
        }
        QComboBox::drop-down {
            border: none;
            width: 26px;
        }
        QComboBox QAbstractItemView {
            background: #ffffff;
            border: 1px solid #cddbe6;
            selection-background-color: #d9f3fa;
            selection-color: #17324f;
        }
        QTextEdit {
            border-radius: 8px;
            padding: 10px 12px;
            selection-background-color: #7dcfe2;
            selection-color: #08233d;
        }
        QTextEdit#LatexEdit {
            background: #0d1f36;
            border: 1px solid #1c3b5f;
            color: #e5f2ff;
            font-family: "Cascadia Code";
            font-size: 13px;
        }
        QTextEdit#CodeEdit {
            background: #112440;
            border: 1px solid #213d60;
            color: #d8eaff;
            font-family: "Cascadia Code";
            font-size: 12px;
        }
        QTextEdit#HistoryEdit {
            background: #f7fbfe;
            border: 1px solid #d7e4ed;
            color: #24415e;
            font-family: "Cascadia Code";
            font-size: 12px;
        }
        QLabel#PreviewSurface {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,
                stop: 0 #fbfeff,
                stop: 1 #eef8fc
            );
            border: 1px solid #d7e8f0;
            border-radius: 10px;
            color: #7b8ea4;
            padding: 16px;
        }
        QLabel#PreviewSurface[previewState="filled"] {
            background: #ffffff;
            border: 1px solid #bfe0ee;
        }
        QTabWidget::pane {
            border: 1px solid #d5e2ec;
            border-radius: 10px;
            background: #0f1f36;
            top: -1px;
        }
        QTabBar::tab {
            background: #e9f0f5;
            border: 1px solid #d4e0e9;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            color: #5b6f84;
            font-size: 12px;
            font-weight: 700;
            padding: 8px 16px;
        }
        QTabBar::tab:selected {
            background: #0f1f36;
            color: #eff9ff;
            border-color: #203958;
        }
        QTabBar::tab:hover:!selected {
            background: #dde9f0;
            color: #24415e;
        }
        QToolBar#TopToolbar {
            background: transparent;
            border: none;
            padding: 2px 0 8px 0;
            spacing: 8px;
        }
        QToolBar#TopToolbar::separator {
            background: transparent;
            width: 6px;
        }
        QToolBar#TopToolbar QToolButton {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid #d1e0ea;
            border-radius: 8px;
            color: #17324f;
            font-size: 12px;
            font-weight: 700;
            padding: 8px 14px;
        }
        QToolBar#TopToolbar QToolButton:hover {
            background: #f2f9fd;
            border-color: #aac7d8;
        }
        QStatusBar {
            background: #f5fbfe;
            border-top: 1px solid #d7e4ed;
            color: #526b84;
            padding: 2px 8px;
        }
        QStatusBar::item {
            border: none;
        }
        QSplitter::handle {
            background: transparent;
            width: 12px;
        }
        QSplitter::handle:hover {
            background: rgba(36, 102, 156, 0.12);
            border-radius: 6px;
        }
    """
