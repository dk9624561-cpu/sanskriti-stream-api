import base64
import json
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY = b"*$!*@(#@$#!@(!@*"
IV = bytes([92, 125, 63, 92, 58, 123, 62, 58, 125, 62, 63, 58, 123, 63, 58, 92])

def encrypt(data_str: str) -> str:
    raw_bytes = data_str.encode('utf-8')
    padded_bytes = pad(raw_bytes, AES.block_size, style='pkcs7')
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    encrypted_bytes = cipher.encrypt(padded_bytes)
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt(encrypted_b64: str) -> dict:
    ciphertext = base64.b64decode(encrypted_b64)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    decrypted_bytes = cipher.decrypt(ciphertext)
    try:
        unpadded = unpad(decrypted_bytes, AES.block_size, style='pkcs7')
        json_str = unpadded.decode('utf-8')
    except ValueError:
        json_str = decrypted_bytes.decode('utf-8', errors='ignore').strip()
        json_str = "".join([c for c in json_str if ord(c) >= 32 or c in '\n\r\t'])
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {"raw_decrypted_text": json_str}

def login(mobile, password, device_id="315811b043a633cb"):
    url = "https://app.sanskritiias.in/index.php/data_model/user/registration/login_authentication_new"
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; Build/QP1A.190711.020)",
        "Host": "app.sanskritiias.in",
        "Connection": "Keep-Alive",
        "userid": "0",
        "devicetype": "1",
        "jwt": "",
        "appversion": "38"
    }
    payload = {
        "c_code": "+91",
        "mobile": mobile,
        "password": password,
        "is_social": "0",
        "social_type": "0",
        "social_tokken": "0",
        "device_type": "1",
        "location": "",
        "device_id": device_id,
        "device_tokken": "",
        "appversion": "38"
    }
    encrypted_body = encrypt(json.dumps(payload))
    print(f"Logging in for mobile: {mobile}...")
    try:
        response = requests.post(url, data=encrypted_body, headers=headers, timeout=10)
        if response.status_code == 200:
            decrypted = decrypt(response.text)
            if decrypted.get("status"):
                data = decrypted.get("data", {})
                jwt = data.get("jwt", "")
                user_id = data.get("user_data", {}).get("id", "")
                print("\n=== LOGIN SUCCESSFUL ===")
                print(f"JWT Token: {jwt}")
                print(f"User ID: {user_id}")
                
                # Save session
                session_data = {
                    "token": jwt,
                    "user_id": user_id,
                    "mobile": mobile,
                    "device_id": device_id
                }
                with open("session.json", "w") as f:
                    json.dump(session_data, f, indent=2)
                print("\nCredentials saved to 'session.json' successfully!")
                return session_data
            else:
                print(f"\n=== LOGIN FAILED ===\nReason: {decrypted.get('message')}")
        else:
            print(f"\n=== SERVER ERROR ===\nStatus: {response.status_code}")
    except Exception as e:
        print(f"\n=== EXCEPTION ===\n{str(e)}")
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        # Prompt user interactively
        m = input("Enter mobile number (e.g. 9650xxxxxx): ")
        p = input("Enter password: ")
    else:
        m = sys.argv[1]
        p = sys.argv[2]
    login(m, p)
