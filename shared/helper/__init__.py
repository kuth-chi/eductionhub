# File: shared/helper/qr_code_generator.py
# This file contains a QR code generator that can be used to create QR codes from data.
import base64
import io
import qrcode


class QRCodeGenerator:
    def __init__(self, data):
        self.data = data
    
    def generate_base64(self):
        """
        Generate a QR code in base64 format.
        """
        qr_image = qrcode.make(self.data)
        buffered = io.BytesIO()
        qr_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def generate_image(self):
        """
        Generate a QR code as an image object.
        """
        return qrcode.make(self.data)
    
    def save_to_file(self, file_path):
        """
        Save the QR code to a file.
        """
        image = self.generate_image()
        image.save(file_path, format="PNG")