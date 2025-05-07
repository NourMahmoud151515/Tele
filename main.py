import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget
from ui_calculator import Ui_Form  # Assuming you have this UI file
from client_application_layer import prepare_message  # Function to prepare the bitstream

# Function to run the server in a separate thread
def run_server():
    from server_transport_layer import start_server
    start_server()

class CalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.init_signals()

    def init_signals(self):
        # Connect the button to calculate result
        self.ui.Calculer.clicked.connect(self.calculate_result)
        self.ui.Reset.clicked.connect(self.reset_fields)

    def calculate_result(self):
        # Get user input from the UI
        op1 = self.ui.lineEdit.text()
        operator = self.ui.lineEdit_2.text()
        op2 = self.ui.lineEdit_3.text()

        # Send the request to the server and get the result
        result = self.send_request_to_server(op1, op2, operator)

        # Display the result in the GUI
        self.ui.lineEdit_4.setText(result)

    def send_request_to_server(self, op1, op2, operator):
        # Prepare the bitstream to send to the server
        bitstream = prepare_message(op1, op2, operator)

        # Establish a connection with the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 5000))  # Assuming the server is running on localhost and port 5000
            # Send the bitstream (converted to string) to the server
            bit_string = ''.join(str(bit) for bit in bitstream)
            s.sendall(bit_string.encode())

            # Receive the response from the server
            response = s.recv(4096).decode()
            return response

    def reset_fields(self):
        # Clear the input fields and result output
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit_3.clear()
        self.ui.lineEdit_4.clear()

if __name__ == "__main__":
    # Start the server in a separate thread to prevent blocking the UI
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Ensure the thread ends when the main program exits
    server_thread.start()

    # Create and run the PyQt5 application
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()

    sys.exit(app.exec_())





