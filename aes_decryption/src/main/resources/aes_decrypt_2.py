import snowflake.snowpark as snowpark
import snowflake.snowpark.files as snowflakefile
import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import base64


def main(session: snowpark.Session):
    # Your code goes here, inside the "python" handler.

    federated_id_str = 'E0jo13jseFtgsdjWVFbX7+fWs6WefuL8D2mhl6xvG3MuM+uyvDkXMWocK/BDlftk'

    fetch_decrypt_keys_sql = """ SELECT  BASE64_DECODE_BINARY(JSON_EXTRACT_PATH_TEXT(FEDID_JSON, ''key'')) 
                                          AS KEY_VALUE, 
                                         BASE64_DECODE_BINARY(JSON_EXTRACT_PATH_TEXT(FEDID_JSON, ''iv'')) 
                                          AS IV_VALUE,
                                          BASE64_DECODE_BINARY(''E0jo13jseFtgsdjWVFbX7+fWs6WefuL8D2mhl6xvG3MuM+uyvDkXMWocK/BDlftk'') 
                                          AS FED_ID
                                    FROM ( SELECT SDP_COMMON.COMMON.FEDERATED_ID_GET_KEYS
                                         (''test'', ''gam'') AS FEDID_JSON 
                                       ) A"""

    fetch_decrypt_keys = session.sql(fetch_decrypt_keys_sql)

    pandas_df = fetch_decrypt_keys.to_pandas()

    key_value_str = pandas_df['KEY_VALUE'].values[0]
    iv_value_str = pandas_df['IV_VALUE'].values[0]
    fed_id_binary = pandas_df['FED_ID'].values[0]

    print(f"key_value_str : {key_value_str}")
    print(f"iv_value_str : {iv_value_str}")
    print(f"fed_id_binary : {fed_id_binary}")
    print(f"")

    cipher = AES.new(key_value_str, AES.MODE_CBC, iv_value_str)
    decryptedtext = cipher.decrypt(fed_id_binary)
    decryptedtext = decryptedtext.decode("utf-8")

    print(f"decrypted_text : {decryptedtext}")

    # decryptedtext = cipher.decrypt(base64.b64decode(federated_id))

    return '''COMPLETE'''