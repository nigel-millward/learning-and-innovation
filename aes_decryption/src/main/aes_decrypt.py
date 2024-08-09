from Crypto.Cipher import AES

from base64 import b64decode


def decrypt_string_by_encode_type(encrypted_text, encode_type) -> str:
    aes_key = 'testkey_1234567890_01234567890_1'
    aes_iv_spec = 'testvector_01234'

    if encode_type == 'base64':
        encrypted_text = b64decode(encrypted_text)
    elif encode_type == 'hex':
        encrypted_text = bytes.fromhex(encrypted_text)

    cipher = AES.new(key=aes_key.encode(), mode=AES.MODE_CBC, IV=aes_iv_spec.encode())
    decrypted_text = cipher.decrypt(encrypted_text)

    return remove_padding(decrypted_text).decode('utf-8')


def remove_padding(decrypted_text):
    return decrypted_text[:-ord(decrypted_text[len(decrypted_text) - 1:])]