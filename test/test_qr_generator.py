import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.qr_generator import generate_qr_code


class TestQRGenerator(unittest.TestCase):

    @patch("modules.qr_generator.pyqrcode.create")
    def test_generate_qr_code(self, mock_create):
        """Тест: генерация QR-кода."""
        # Настраиваем мок для pyqrcode
        mock_qr = mock_create.return_value
        mock_qr.png = unittest.mock.Mock()

        # Входные данные
        data = "mock_data"
        qr_path = "mock_qr_path.png"

        # Вызов функции
        generate_qr_code(data, qr_path)

        # Проверяем, что pyqrcode.create был вызван с правильными данными
        mock_create.assert_called_once_with(data)

        # Проверяем, что .png был вызван с правильным путем и масштабом
        mock_qr.png.assert_called_once_with(qr_path, scale=6)


if __name__ == "__main__":
    unittest.main()
