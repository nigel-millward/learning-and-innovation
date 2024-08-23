import unittest
from src.main.aes_decrypt import decrypt_string_by_encode_type


class TestAES(unittest.TestCase):

    def test_aes_decrypt_base_64_string(self):
        # ASSEMBLE
        plain_text = '5e3b5612-daea-460d-80f4-df91026a0779'
        base64_encrypted_text = 'bK9whZ7xdHjaNFqXiLzTtdk7JgdwIF8jCUdNT3kbjG0IHiyCDLVMi44bMLYZXav9'
        aes_key_base64 = 'dGVzdGtleV8xMjM0NTY3ODkwXzAxMjM0NTY3ODkwXzE='
        aes_iv_base64 = 'dGVzdHZlY3Rvcl8wMTIzNA=='

        # ACT
        decrypted_text = decrypt_string_by_encode_type(base64_encrypted_text, 'base64', aes_key_base64, aes_iv_base64)

        # ASSERT
        self.assertEqual(decrypted_text, plain_text)

    def test_aes_decrypt_hex_string(self):
        # ASSEMBLE
        plain_text = 'bba7bc71-19bd-4985-a106-81ed56a6c0a6'
        base64_encrypted_text = '766F5674C4CA7A55A2175A2454038FED570DEDEDAF8EFED4EE30F032E41DE6A131BB77275BC6126BFFD2E329E5E8FCC9'
        aes_key_base64 = 'dGVzdGtleV8xMjM0NTY3ODkwXzAxMjM0NTY3ODkwXzE='
        aes_iv_base64 = 'dGVzdHZlY3Rvcl8wMTIzNA=='

        # ACT
        decrypted_text = decrypt_string_by_encode_type(base64_encrypted_text, 'hex', aes_key_base64, aes_iv_base64)

        # ASSERT
        self.assertEqual(decrypted_text, plain_text)
