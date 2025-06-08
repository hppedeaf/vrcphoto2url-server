from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Server")
        self.setFixedSize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.server_address_input = QLineEdit(self)
        self.server_address_input.setPlaceholderText("Enter server address (e.g., http://localhost:5000)")
        layout.addWidget(self.server_address_input)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

    def connect_to_server(self):
        server_address = self.server_address_input.text()
        if self.validate_address(server_address):
            self.status_label.setText(f"Connecting to {server_address}...")
            # Here you would add the logic to connect to the server
            QMessageBox.information(self, "Success", f"Connected to {server_address}")
            self.accept()
        else:
            self.status_label.setText("Invalid server address. Please try again.")

    def validate_address(self, address):
        # Basic validation for the server address
        return address.startswith("http://") or address.startswith("https://")