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

    fetch_decrypt_keys_sql  = """ SELECT  BASE64_DECODE_BINARY(JSON_EXTRACT_PATH_TEXT(FEDID_JSON, 'key'))
                                          AS KEY_VALUE,
                                         BASE64_DECODE_BINARY(JSON_EXTRACT_PATH_TEXT(FEDID_JSON, 'iv'))
                                          AS IV_VALUE,
                                          BASE64_DECODE_BINARY('E0jo13jseFtgsdjWVFbX7+fWs6WefuL8D2mhl6xvG3MuM+uyvDkXMWocK/BDlftk')
                                          AS FED_ID
                                    FROM ( SELECT SDP_COMMON.COMMON.FEDERATED_ID_GET_KEYS
                                         ('test', 'gam') AS FEDID_JSON
                                       ) A"""

    fetch_decrypt_keys = session.sql(fetch_decrypt_keys_sql)

    pandas_df = fetch_decrypt_keys.to_pandas()

    key_value_str = pandas_df['KEY_VALUE'].values[0]
    iv_value_str =  pandas_df['IV_VALUE'].values[0]
    fed_id_binary = pandas_df['FED_ID'].values[0]

    print(f"key_value_str : {key_value_str}")
    print(f"iv_value_str : {iv_value_str}")
    print(f"fed_id_binary : {fed_id_binary}")
    print(f"       ")

    key = key_value_str.encode("utf-8")
    iv  = iv_value_str.encode("utf-8")
    fedid = federated_id_str.encode("utf-8")

    print(f"key : {key}")
    print(f"iv : {iv}")
    print(f"fedid : {fedid}")
    print(f"       ")
    key = base64.b64encode(key)
    iv = base64.b64encode(iv)
    fedid = base64.b64encode(fedid)

    print(f"key : {key}")
    print(f"iv : {iv}")
    print(f"fedid : {fedid}")
    print(f"       ")
    cipher = AES.new(base64.b64decode(key_value_str), AES.MODE_CBC, base64.b64decode(iv_value_str))
    decryptedtext = cipher.decrypt(base64.b64decode(fedid))

    #decodedstring=base64.b64decode(decryptedtext).decode('utf-8')
    #print(decodedstring)
   # decryptedtext  = decryptedtext.decode("ascii")

    print(f"decryptedtext : {decryptedtext}")

    fed_id_q1 = """SELECT HEX_DECODE_STRING(TO_VARCHAR(DECRYPT_RAW( '"""+fed_id_binary+"""',"""+key_value_str+"""',"""+iv_value_str+"""'),
       NULL,  'AES-CBC/pad:PKCS' ))) fed_id """

    print(f"fed_id_q1 : {fed_id_q1}")
    #fetch_fedid = session.sql(fed_id_q1)

    #pandas_df = fetch_fedid.to_pandas()

    #fed_id = pandas_df['fed_id'].values[0]
    #print(f"fed_id : {fed_id}") return 'COMPLETE'