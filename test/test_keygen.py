'USING: # PYTHONPATH=/var/www/html/grav/user/scripts/wg_qr_generator python3 -m unittest test_keygen.py'

import unittest
import subprocess
from modules.keygen import generate_private_key, generate_public_key

class TestKeygen(unittest.TestCase):

    def test_generate_private_key(self):
        # Проверяем, что приватный ключ возвращается как bytes
        private_key = generate_private_key()
        self.assertIsInstance(private_key, bytes)  # Проверяем, что возвращается bytes
        self.assertEqual(len(private_key), 44, "Private key must be 44 bytes long")

        # Проверяем валидность приватного ключа через wg pubkey
        try:
            public_key = subprocess.check_output(
                ['wg', 'pubkey'],
                input=private_key,
                stderr=subprocess.PIPE
            ).strip()
            self.assertTrue(public_key, "Public key generation failed for the private key")
        except subprocess.CalledProcessError as e:
            self.fail(f"wg pubkey validation failed with error: {e.stderr.decode()}")

    def test_generate_public_key(self):
        # Проверяем, что публичный ключ корректен
        private_key = generate_private_key()
        public_key = generate_public_key(private_key)  # Передаем bytes напрямую
        self.assertIsInstance(public_key, bytes)  # Ожидаем bytes
        self.assertEqual(len(public_key), 44, "Public key must be 44 bytes long")

    def test_key_uniqueness(self):
        # Проверяем уникальность сгенерированных ключей
        private_keys = {generate_private_key() for _ in range(100)}
        self.assertEqual(len(private_keys), 100, "All private keys must be unique")

    def test_invalid_private_key(self):
        '''
        Проверяем, что при некорректном приватном ключе возникает ошибка
        Сообщение `wg: Key is not the correct length or format` связано с этим тестом.
        Оно возникает, так как передается недопустимый ключ (b"invalid_key").
        '''
        invalid_key_bytes = b"invalid_key"
        with self.assertRaises(subprocess.CalledProcessError):
            generate_public_key(invalid_key_bytes)  # Передаем bytes напрямую

if __name__ == '__main__':
    unittest.main()
