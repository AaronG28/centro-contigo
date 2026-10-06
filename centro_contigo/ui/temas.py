"""Temas claro/oscuro y hoja de estilos."""

from PySide6.QtGui import QColor, QPalette


TEMAS = {
    "light": dict(text="#1c1c1e", bg="#f5f7fa", card="#ffffff", input="#ffffff",
                  border="#d2d2d7", border2="#e5e5ea", sub="#6e6e73",
                  accent="#0071e3", accent_h="#0062c4", hover="#f0f4fa",
                  sel="#e6f0fc", alt="#fafbfd", danger="#ff3b30",
                  danger_h="#d92d24", table="#ffffff", menu="#ffffff",
                  selt="#1c1c1e"),
    "dark": dict(text="#f5f5f7", bg="#1c1c1e", card="#2c2c2e", input="#2c2c2e",
                 border="#38383a", border2="#38383a", sub="#8e8e93",
                 accent="#0a84ff", accent_h="#409cff", hover="#3a3a3c",
                 sel="#0a3a6e", alt="#232325", danger="#ff453a",
                 danger_h="#ff6961", table="#1c1c1e", menu="#2c2c2e",
                 selt="#f5f5f7"),
}

STYLE_TEMPLATE = """
QWidget { font-family: -apple-system, "SF Pro Text", "Helvetica Neue",
          "Segoe UI", sans-serif; font-size: 13px; color: @text@; }
QMainWindow, QTabWidget::pane, QStackedWidget { background: @bg@; }
QTabBar::tab { padding: 11px 22px; background: transparent; color: @sub@;
               border: none; font-weight: 500; margin-right: 4px; }
QTabBar::tab:selected { color: @accent@; border-bottom: 3px solid @accent@; }
QTabBar::tab:hover { color: @accent@; }
QPushButton { padding: 8px 14px; border-radius: 9px; border: 1px solid @border@;
              background: @card@; color: @text@; font-weight: 500; }
QPushButton:hover { background: @hover@; border-color: @accent@; color: @accent@; }
QPushButton:disabled { color: @sub@; background: @bg@; border-color: @border2@; }
QPushButton#primary { background: @accent@; color: white; border: none;
                      font-weight: 600; }
QPushButton#primary:hover { background: @accent_h@; color: white; }
QPushButton#danger { background: @danger@; color: white; border: none;
                     font-weight: 600; }
QPushButton#danger:hover { background: @danger_h@; color: white; }
QPushButton#danger:disabled, QPushButton#primary:disabled {
    background: @border2@; color: @sub@; }
QLineEdit, QPlainTextEdit, QComboBox, QDateEdit, QDateTimeEdit,
QDoubleSpinBox, QSpinBox { padding: 7px 10px; border: 1px solid @border@;
    border-radius: 8px; background: @input@; color: @text@;
    selection-background-color: @accent@; }
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus,
QDateTimeEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid @accent@; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background: @input@; color: @text@;
                              selection-background-color: @accent@; }
QTableWidget { background: @table@; border: 1px solid @border2@;
               border-radius: 10px; gridline-color: transparent;
               alternate-background-color: @alt@; color: @text@; }
QHeaderView::section { background: @bg@; padding: 9px; border: none;
                       border-bottom: 1px solid @border2@; font-weight: 600;
                       color: @sub@; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background: @sel@; color: @selt@; }
QLabel#kpiTitle { color: @sub@; font-size: 11px; font-weight: 600; }
QLabel#kpiValue { font-size: 20px; font-weight: 700; }
QFrame#kpi { background: @card@; border: 1px solid @border2@;
             border-radius: 12px; }
QScrollArea { background: transparent; }
QScrollBar:vertical, QScrollBar:horizontal { background: @bg@; }
QScrollBar::handle { background: @border@; border-radius: 4px; }
QMenuBar { background: @bg@; color: @text@; }
QMenuBar::item:selected { background: @sel@; }
QMenu { background: @menu@; color: @text@; border: 1px solid @border2@; }
QMenu::item:selected { background: @accent@; color: white; }
QMessageBox, QInputDialog, QFileDialog, QDialog { background: @bg@; }
QToolTip { background: @card@; color: @text@; border: 1px solid @border@; }
QSplitter::handle { background: @border2@; }
QSplitter::handle:hover { background: @accent@; }
QSplitter::handle:horizontal { width: 6px; }
"""


def build_stylesheet(theme):
    s = STYLE_TEMPLATE
    for k, v in TEMAS[theme].items():
        s = s.replace(f"@{k}@", v)
    return s


def build_palette(theme):
    t = TEMAS[theme]
    pal = QPalette()
    mapa = {QPalette.Window: t["bg"], QPalette.WindowText: t["text"],
            QPalette.Base: t["input"], QPalette.AlternateBase: t["alt"],
            QPalette.Text: t["text"], QPalette.Button: t["card"],
            QPalette.ButtonText: t["text"], QPalette.Highlight: t["accent"],
            QPalette.HighlightedText: "#ffffff", QPalette.ToolTipBase: t["card"],
            QPalette.ToolTipText: t["text"], QPalette.PlaceholderText: t["sub"]}
    for role, col in mapa.items():
        pal.setColor(role, QColor(col))
    for role in (QPalette.Text, QPalette.ButtonText, QPalette.WindowText):
        pal.setColor(QPalette.Disabled, role, QColor(t["sub"]))
    return pal
