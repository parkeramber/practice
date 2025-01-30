import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl  # Import QUrl to handle URL format

class WebApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("PyQt Web App")
        self.setGeometry(100, 100, 800, 600)

        # Create web view widget
        self.browser = QWebEngineView()

        # Load the local HTML file (optional)
        html_path = os.path.abspath("index.html")  # Ensure correct path
        local_url = QUrl.fromLocalFile(html_path)  # Convert to QUrl
        self.browser.setUrl(local_url)  # Use QUrl object for local file

        # Load the Flask web page (corrected)
        flask_url = QUrl("http://127.0.0.1:5000")  # Convert string to QUrl
        self.browser.setUrl(flask_url)  # Use QUrl object for web address

        # Set the central widget to the web browser
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebApp()
    window.show()
    sys.exit(app.exec_())
