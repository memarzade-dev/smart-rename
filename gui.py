"""Smart Rename Pro GUI Application.

This module provides a modern, user-friendly graphical interface for the Smart Rename Pro tool.
It uses PySide6 for the UI framework and implements a dark theme with modern styling.
"""

import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from smart_rename_pro import DirectoryProcessor, ReplaceConfig

# --- Modern Dark Theme Stylesheet ---
CHIC_DARK_STYLESHEET = """
QWidget {
    background-color: #121212;
    color: #EAEAEA;
    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    font-size: 10pt;
}

QMainWindow, QDialog {
    background-color: #121212;
}

/* --- Section Titles --- */
QLabel#section_title {
    font-size: 13pt;
    font-weight: bold;
    color: #EAEAEA;
    padding-top: 15px;
    padding-bottom: 5px;
    border-bottom: 1px solid #333333;
}

QLabel {
    font-weight: 600;
}

/* --- Input Fields --- */
QLineEdit {
    background-color: #1E1E1E;
    border: none;
    border-bottom: 2px solid #444;
    border-radius: 0px;
    padding: 8px 4px;
    color: #EAEAEA;
}

QLineEdit:focus {
    border-bottom: 2px solid #2dce89; /* Mint Green */
}

/* --- Log Display --- */
QTextEdit {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 5px;
    color: #cccccc;
    font-family: 'Consolas', 'Courier New', 'monospace';
}

/* --- Standard Buttons --- */
QPushButton {
    background-color: #282828;
    color: #EAEAEA;
    border: 1px solid #444;
    border-radius: 5px;
    padding: 10px 18px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #383838;
    border-color: #555;
}

QPushButton:pressed {
    background-color: #222;
}

/* --- Main Action Button --- */
QPushButton#start_btn {
    background-color: #2dce89; /* Mint Green */
    color: #121212;
    border: none;
}
QPushButton#start_btn:hover {
    background-color: #28b87a;
}
QPushButton#start_btn:disabled {
    background-color: #2A4A3A;
    color: #555;
}

/* --- Sponsor Button --- */
QPushButton#sponsor_btn {
    background-color: #f5365c; /* Red */
    color: #ffffff;
    border: none;
}
QPushButton#sponsor_btn:hover {
    background-color: #ec2C52;
}

/* --- Checkbox --- */
QCheckBox {
    spacing: 10px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    background-color: #282828;
    border: 1px solid #444;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #2dce89;
    border: 1px solid #2dce89;
}
"""


class RenameWorker(QThread):
    """Worker thread for handling rename operations without freezing the UI."""

    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, config):
        """Initialize the worker with the given configuration.

        Args:
            config: ReplaceConfig object containing the rename operation parameters.
        """
        super().__init__()
        self.config = config

    def run(self):
        """Execute the rename operation in a separate thread."""
        try:
            import smart_rename_pro

            class GuiLogger:
                """Custom logger that emits messages to the GUI."""

                def __init__(self, progress_signal):
                    """Initialize with the progress signal.

                    Args:
                        progress_signal: Signal to emit log messages to.
                    """
                    self.progress_signal = progress_signal

                def info(self, msg, extra=None):
                    """Log an info message.

                    Args:
                        msg: The message to log.
                        extra: Additional context (unused).
                    """
                    self.progress_signal.emit(f"[INFO] {msg}")

                def error(self, msg, extra=None):
                    """Log an error message.

                    Args:
                        msg: The message to log.
                        extra: Additional context (unused).
                    """
                    self.progress_signal.emit(f"[ERROR] {msg}")

                def warning(self, msg, extra=None):
                    """Log a warning message.

                    Args:
                        msg: The message to log.
                        extra: Additional context (unused).
                    """
                    self.progress_signal.emit(f"[WARN] {msg}")

                def debug(self, msg, extra=None):
                    """Log a debug message (currently disabled).

                    Args:
                        msg: The message to log.
                        extra: Additional context (unused).
                    """
                    pass

            smart_rename_pro.logger = GuiLogger(self.progress)
            DirectoryProcessor.process_directory(self.config)
            self.finished.emit(True, "Operation completed successfully!")
        except Exception as e:
            self.finished.emit(False, f"An error occurred: {str(e)}")


class SponsorshipDialog(QDialog):
    """Dialog for displaying sponsorship options."""

    def __init__(self, parent=None):
        """Initialize the sponsorship dialog.

        Args:
            parent: Parent widget (optional).
        """
        super().__init__(parent)
        self.setWindowTitle("💖 Support Smart Rename Pro")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Support the Project")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        intro_text = QLabel(
            "This project is maintained with care. Your contribution helps ensure it stays "
            "robust and actively developed."
        )
        intro_text.setWordWrap(True)
        intro_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(intro_text)

        # Sponsorship options
        self.create_sponsor_button(
            layout, "💼 Sponsor on GitHub", "https://github.com/sponsors/memarzade-dev"
        )
        self.create_sponsor_button(
            layout, "☕ Buy Me a Coffee", "https://www.buymeacoffee.com/memarzade-dev"
        )
        self.create_sponsor_button(
            layout, "💝 Support on Ko-fi", "https://ko-fi.com/memarzade-dev"
        )

    def create_sponsor_button(self, layout, text, url):
        """Create a sponsorship button with the given text and URL.

        Args:
            layout: The layout to add the button to.
            text: The button text.
            url: The URL to open when clicked.
        """
        button = QPushButton(text)
        button.setObjectName("sponsor_btn")
        button.clicked.connect(lambda: webbrowser.open(url))
        layout.addWidget(button)


class MainWindow(QMainWindow):
    """Main window of the Smart Rename Pro application."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Smart Rename Pro")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)

        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory to process...")
        dir_layout.addWidget(self.dir_input)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)

        layout.addLayout(dir_layout)

        # Search and replace inputs
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Text to search for...")
        layout.addWidget(self.search_input)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Text to replace with...")
        layout.addWidget(self.replace_input)

        # Options
        self.recursive_checkbox = QCheckBox("Process subdirectories")
        self.recursive_checkbox.setChecked(True)
        layout.addWidget(self.recursive_checkbox)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        # Action buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Renaming")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.clicked.connect(self.start_renaming)
        button_layout.addWidget(self.start_btn)

        sponsor_btn = QPushButton("💖 Support Project")
        sponsor_btn.setObjectName("sponsor_btn")
        sponsor_btn.clicked.connect(self.open_sponsorship_dialog)
        button_layout.addWidget(sponsor_btn)

        layout.addLayout(button_layout)

        # Apply stylesheet
        self.setStyleSheet(CHIC_DARK_STYLESHEET)

    def browse_directory(self):
        """Open a directory selection dialog."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", str(Path.home())
        )
        if dir_path:
            self.dir_input.setText(dir_path)

    def open_sponsorship_dialog(self):
        """Open the sponsorship dialog."""
        dialog = SponsorshipDialog(self)
        dialog.exec()

    def start_renaming(self):
        """Start the renaming process."""
        dir_path = self.dir_input.text()
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()

        if not dir_path:
            QMessageBox.warning(self, "Error", "Please select a directory.")
            return

        if not search_text:
            QMessageBox.warning(self, "Error", "Please enter text to search for.")
            return

        config = ReplaceConfig(
            directory=dir_path,
            search_text=search_text,
            replace_text=replace_text,
            recursive=self.recursive_checkbox.isChecked(),
        )

        self.start_btn.setEnabled(False)
        self.log_display.clear()

        self.worker = RenameWorker(config)
        self.worker.progress.connect(self.update_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_log(self, message):
        """Update the log display with a new message.

        Args:
            message: The message to display.
        """
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def on_finished(self, success, message):
        """Handle the completion of the renaming process.

        Args:
            success: Whether the operation was successful.
            message: The completion message.
        """
        self.start_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
