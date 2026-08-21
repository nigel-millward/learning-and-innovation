from Crypto.Cipher import AES

from base64 import b64decode, decodebytes


def decrypt_string_by_encode_type(encrypted_text, encode_type, aes_key, aes_iv_spec) -> str:
    if encode_type == 'base64':
        encrypted_text = b64decode(encrypted_text)
    elif encode_type == 'hex':
        encrypted_text = bytes.fromhex(encrypted_text)

    cipher = AES.new(key=b64decode(aes_key), mode=AES.MODE_CBC, IV=b64decode(aes_iv_spec))
    decrypted_text = cipher.decrypt(encrypted_text)

    return remove_padding(decrypted_text).decode('utf-8')


def remove_padding(decrypted_text):
    return decrypted_text[:-ord(decrypted_text[len(decrypted_text) - 1:])]