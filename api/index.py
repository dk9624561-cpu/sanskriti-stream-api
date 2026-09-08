import os
import sys
import re
import json
import base64
import requests
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)

# Sanskriti IAS AES CBC Encryption Credentials
KEY = b"*$!*@(#@$#!@(!@*"
IV = bytes([92, 125, 63, 92, 58, 123, 62, 58, 125, 62, 63, 58, 123, 63, 58, 92])

# In-Memory Stream Cache (Instantly serves already decrypted streams)
STREAM_CACHE = {}

# Enable CORS for all incoming requests
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, userid, jwt"
    return response

def encrypt(data_str: str) -> str:
    raw_bytes = data_str.encode('utf-8')
    padded_bytes = pad(raw_bytes, AES.block_size, style='pkcs7')
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    encrypted_bytes = cipher.encrypt(padded_bytes)
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt(encrypted_b64: str) -> dict:
    try:
        raw_text = str(encrypted_b64).strip()
        if "</div>" in raw_text:
            raw_text = raw_text[raw_text.rfind("</div>") + 6:].strip()
        if raw_text.startswith("{") and raw_text.endswith("}"):
            return json.loads(raw_text)

        ciphertext = base64.b64decode(raw_text)
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted_bytes = cipher.decrypt(ciphertext)
        try:
            unpadded = unpad(decrypted_bytes, AES.block_size, style='pkcs7')
            json_str = unpadded.decode('utf-8')
        except ValueError:
            json_str = decrypted_bytes.decode('utf-8', errors='ignore').strip()
            json_str = "".join([c for c in json_str if ord(c) >= 32 or c in '\n\r\t'])
        return json.loads(json_str)
    except Exception as e:
        return {"error": str(e)}

def decode_classx(token_str):
    """Decodes encrypted ClassX token directly if formatted with AES CBC"""
    try:
        key = "638udh3829162018".encode("utf-8")
        iv = "fedcba9876543210".encode("utf-8")
        ciphertext = bytearray.fromhex(base64.b64decode(token_str.encode()).hex())
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        decoded_url = plaintext.decode('utf-8')
        if "classx.co.in" in decoded_url or "m3u8" in decoded_url or "http" in decoded_url:
            return decoded_url
    except Exception:
        pass
    return None

def decrypt_meta_link(meta_encrypted, token):
    """Decrypts Videocrypt get_dist_links dynamic meta links"""
    try:
        token_parts = str(token).split("_")
        val = int(token_parts[2]) + 200000 if len(token_parts) >= 3 else 200000
        j = f"0_0_{val}"
        j_parts = j.split("_")
        third_part = j_parts[2][:16]
        
        key_alphabet = "!*@#)($^%1fgv&C="
        key = "".join([key_alphabet[int(c)] for c in third_part if c.isdigit()]).encode('utf-8')
        
        iv_alphabet = r"?\:><{}@#Vjekl/4"
        iv = "".join([iv_alphabet[int(c)] for c in third_part if c.isdigit()]).encode('utf-8')
        
        encrypted_base64 = meta_encrypted.split(":")[0]
        ciphertext = base64.b64decode(encrypted_base64)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_bytes = cipher.decrypt(ciphertext)
        
        decrypted_str = decrypted_bytes.decode('utf-8', errors='ignore').strip()
        start_idx = decrypted_str.find("{")
        end_idx = decrypted_str.rfind("}")
        if start_idx != -1 and end_idx != -1:
            decrypted_str = decrypted_str[start_idx:end_idx+1]
        return json.loads(decrypted_str)
    except Exception as e:
        return {"error": str(e)}

def format_all_stream_qualities(base_dfile_url, vdc_id=""):
    """Constructs multi-resolution M3U8 dictionary"""
    url_str = str(base_dfile_url).strip()
    clean_id = vdc_id.split("_")[0] if "_" in str(vdc_id) else str(vdc_id)
    clean_id = "".join([c for c in clean_id if c.isdigit()]) or "604239"
    
    qualities = {}
    frag_map = {"240p": "Frag1", "360p": "Frag2", "480p": "Frag3", "720p": "Frag4"}
    
    # Check if stream-os-assets or classx URL
    if "classx.co.in" in url_str or "/480p/" in url_str or "/720p/" in url_str:
        for q in ["720p", "480p", "360p", "240p"]:
            if re.search(r'/(720p|480p|360p|240p)/', url_str):
                qualities[q] = re.sub(r'/(720p|480p|360p|240p)/', f"/{q}/", url_str)
            else:
                qualities[q] = url_str
        qualities["master"] = url_str
        return qualities

    for q_name, frag in frag_map.items():
        if "_appxabr" in url_str and "-Frag" not in url_str:
            qualities[q_name] = url_str.replace("_appxabr.m3u8", f"_appxabr-{frag}.m3u8")
        elif "-Frag" in url_str:
            qualities[q_name] = re.sub(r'-Frag\d+', f"-{frag}", url_str)
        else:
            qualities[q_name] = url_str

    qualities["master"] = url_str
    return qualities

def call_sanskriti_api(endpoint, payload, jwt_token="", user_id="0"):
    """Calls app.sanskritiias.in directly with AES payload encryption"""
    url = "https://app.sanskritiias.in/index.php/data_model/" + endpoint
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; Build/QP1A.190711.020)",
        "Host": "app.sanskritiias.in",
        "Connection": "Keep-Alive",
        "userid": str(user_id),
        "devicetype": "1",
        "jwt": str(jwt_token),
        "appversion": "38"
    }
    encrypted_body = encrypt(json.dumps(payload))
    try:
        r = requests.post(url, data=encrypted_body, headers=headers, timeout=8)
        if r.status_code == 200:
            return decrypt(r.text)
    except Exception as e:
        return {"error": str(e)}
    return {"status": False, "message": "HTTP Request Failed"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "service": "Custom Sanskriti & ClassX High-Speed Stream API",
        "endpoint": "/codex",
        "version": "6.0.0",
        "description": "High-availability bypass and decryption API with automatic upstream failover."
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK", "uptime": "active", "cached_videos": len(STREAM_CACHE)})

@app.route("/codex", methods=["POST", "OPTIONS"])
@app.route("/decrypt", methods=["POST", "OPTIONS"])
def codex_decrypt_handler():
    if request.method == "OPTIONS":
        return jsonify({"status": True})

    data = request.get_json(silent=True) or {}
    
    vdc_id = str(data.get("vdc_id") or data.get("name") or "").strip()
    course_id = str(data.get("course_id") or "0").strip()
    tile_id = str(data.get("tile_id") or "0").strip()
    user_id = str(data.get("user_id") or "128005").strip()
    jwt_token = str(data.get("token") or data.get("jwt") or "").strip()
    mobile = str(data.get("mobile") or "6207725410").strip()
    quality = str(data.get("quality") or "720").strip()

    if not vdc_id:
        return jsonify({"status": False, "message": "The name field is required."}), 200

    target_q = quality if quality.endswith("p") else quality + "p"
    q_num = "".join([c for c in target_q if c.isdigit()]) or "720"
    tile_str = tile_id if tile_id and tile_id != "0" else "2041"

    # Check In-Memory Cache first
    cache_key = f"{vdc_id}_{q_num}"
    if cache_key in STREAM_CACHE:
        cached_res = STREAM_CACHE[cache_key]
        return jsonify(cached_res)


    # ========================================================
    # TIER 1: Primary Stream-OS Providers (High Speed Direct Stream)
    # ========================================================
    upstream_endpoints = [
        "https://code-x-sanskriti.vercel.app/codex",
        "https://codexapisrc.vercel.app/codex"
    ]
    upstream_payload = {
        "course_id": str(course_id),
        "vdc_id": str(vdc_id),
        "tile_id": str(tile_str),
        "user_id": str(user_id),
        "token": str(jwt_token),
        "quality": q_num
    }

    for ep in upstream_endpoints:
        try:
            r_up = requests.post(ep, json=upstream_payload, timeout=6)
            if r_up.status_code == 200:
                up_data = r_up.json()
                if up_data.get("status") and up_data.get("url"):
                    stream_url = up_data.get("url")
                    qualities = format_all_stream_qualities(stream_url, vdc_id)
                    final_url = qualities.get(target_q, stream_url)
                    result = {
                        "status": True,
                        "url": final_url,
                        "quality": q_num,
                        "qualities": qualities,
                        "provider": "stream_os_upstream_resolved"
                    }
                    STREAM_CACHE[cache_key] = result
                    return jsonify(result)
        except Exception as e:
            print(f"[Upstream Warn] {ep} error: {e}")

    # ========================================================
    # TIER 2: ClassX AES Token Direct Decryption
    # ========================================================
    classx_url = decode_classx(vdc_id)
    if classx_url:
        qualities = format_all_stream_qualities(classx_url, vdc_id)
        final_url = qualities.get(target_q, classx_url)
        result = {
            "status": True,
            "url": final_url,
            "quality": q_num,
            "qualities": qualities,
            "provider": "classx_aes_decrypted"
        }
        STREAM_CACHE[cache_key] = result
        return jsonify(result)

    # ========================================================
    # TIER 3: Direct Videocrypt Dist Links Decryption
    # ========================================================
    dist_payload = {
        "name": vdc_id,
        "course_id": course_id if course_id != "0" else "705",
        "tile_id": tile_str,
        "type": "video",
        "device_id": "ce5916c25be30f81",
        "device_type": "1",
        "mobile": mobile
    }
    dist_res = call_sanskriti_api("video_file_uploader/get_dist_links", dist_payload, jwt_token, user_id)
    if dist_res.get("status") and dist_res.get("data", {}).get("meta"):
        meta = dist_res["data"]["meta"]
        decrypted = decrypt_meta_link(meta, vdc_id)
        if decrypted and not "error" in decrypted:
            links = decrypted.get("link", [])
            qualities = {}
            main_url = None
            for link in links:
                q = str(link.get("title", "720")).replace("p", "") + "p"
                u = link.get("url", "")
                qualities[q] = u
                if not main_url:
                    main_url = u
            if main_url:
                result = {
                    "status": True,
                    "url": qualities.get(target_q, main_url),
                    "quality": q_num,
                    "qualities": qualities,
                    "provider": "videocrypt_meta_decrypted"
                }
                STREAM_CACHE[cache_key] = result
                return jsonify(result)

    # ========================================================
    # TIER 4: Sanskriti Course Backend Video Extraction
    # ========================================================
    target_lec_id = vdc_id.split("_")[0] if "_" in vdc_id else vdc_id
    chapters_to_try = [tile_str, "17", "20", "3", "0"]
    for ch_id in chapters_to_try:
        lec_payload = {
            "user_id": user_id,
            "id": course_id if course_id != "0" else "705",
            "layer": "3",
            "topic_id": ch_id
        }
        lec_res = call_sanskriti_api("courses/exam/get_video_data", lec_payload, jwt_token, user_id)
        if lec_res.get("status"):
            lec_list = lec_res.get("data", {}).get("list", [])
            for lec in lec_list:
                if str(lec.get("id")) == str(target_lec_id) or str(lec.get("token")) == str(vdc_id):
                    raw_dfile = lec.get("dfile_url")
                    if raw_dfile:
                        qualities = format_all_stream_qualities(raw_dfile, vdc_id)
                        result = {
                            "status": True,
                            "url": qualities.get(target_q, raw_dfile),
                            "quality": q_num,
                            "qualities": qualities,
                            "title": lec.get("title", "Class Lecture"),
                            "provider": "sanskriti_multi_format_resolved"
                        }
                        STREAM_CACHE[cache_key] = result
                        return jsonify(result)

    # ========================================================
    # TIER 5: Direct Multi-Format CloudFront Stream Fallback
    # ========================================================
    clean_id = "".join([c for c in target_lec_id if c.isdigit()]) or "55302"
    base_url = f"https://liveclasses.cloud-front.in/live/T_{clean_id}_appxabr.m3u8"
    qualities = format_all_stream_qualities(base_url, vdc_id)
    result = {
        "status": True,
        "url": qualities.get(target_q, base_url),
        "quality": q_num,
        "qualities": qualities,
        "provider": "sanskriti_constructed_multi_format"
    }
    return jsonify(result)

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Custom Sanskriti & ClassX API Server running on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
