# Dhiraj Sanskriti Bypass API Project

यह प्रोजेक्ट **Sanskriti IAS** के वीडियो लिंक्स को बाईपास और डिक्रिप्ट (Decrypt) करने की API है। यह Flask फ्रेमवर्क पर आधारित है और इसे **Vercel** पर सर्वरलेस (Serverless) डिप्लॉयमेंट के लिए तैयार किया गया है।

---

## Features (विशेषताएं)
1. **Flask API Endpoint (`/codex`):** वीडियो डिक्रिप्शन और स्ट्रीमिंग लिंक प्राप्त करने के लिए `POST` एपीआई।
2. **Local Session Authentication:** `login_helper.py` द्वारा यूजर क्रेडेंशियल्स दर्ज करके `session.json` बनाने की सुविधा।
3. **Automatic Crypto decryption:** संस्कृतियों के वीडियो यूआरएल और मेटाडेटा के डिक्रिप्शन का इन-बिल्ट स्थानीय लॉजिक।
4. **Vercel Serverless Ready:** Vercel पर एक क्लिक में आसानी से डिप्लॉय करने के लिए कॉन्फ़िगरेशन।

---

## Project Structure (प्रोजेक्ट संरचना)
```text
dhiraj_api/
├── .gitignore
├── README.md               # यह हेल्प फ़ाइल
├── requirements.txt         # डिपेंडेंसी पैकेजेस
├── vercel.json             # Vercel डिप्लॉयमेंट रूट्स
├── login_helper.py         # क्रेडेंशियल्स से टोकन जनरेट करने का टूल
├── test_client.py          # एपीआई टेस्टिंग स्क्रिप्ट
└── api/
    └── index.py            # मुख्य एपीआई कोड (Flask सर्वर)
```

---

## Setup & Running Locally (लोकल सेटअप और चलाना)

### 1. Requirements (आवश्यकताएं)
आपके पास **Python 3.8+** इंस्टॉल होना चाहिए। 

टर्मिनल/कमांड प्रॉम्प्ट में प्रोजेक्ट फोल्डर के अंदर जाकर ये कमांड्स चलाएं:
```bash
# 1. वर्चुअल एनवायरनमेंट बनाएं (वैकल्पिक / Optional)
python -m venv venv
venv\Scripts\activate

# 2. डिपेंडेंसीज़ इंस्टॉल करें
pip install -r requirements.txt
```

### 2. Login to Get Token (लॉगिन और टोकन प्राप्त करना)
API का उपयोग करने के लिए आपके पास संस्कृतियों का एक्टिव टोकन होना चाहिए। नीचे दी गई स्क्रिप्ट चलाकर लॉगिन करें:
```bash
python login_helper.py
```
*यह आपसे मोबाइल नंबर और पासवर्ड मांगेगा, और लॉगिन सफल होने पर `session.json` फाइल बना देगा।*

### 3. Start Local Server (लोकल सर्वर चालू करें)
मुख्य एपीआई सर्वर शुरू करने के लिए:
```bash
python api/index.py
```
*यह स्थानीय तौर पर `http://localhost:5000` पर चलना शुरू हो जाएगा।*

### 4. Test the API (एपीआई टेस्ट करें)
एक दूसरा टर्मिनल खोलें और यह स्क्रिप्ट चलाकर अपनी लोकल एपीआई का परीक्षण करें:
```bash
python test_client.py
```
*यह आपसे वीडियो का `vdc_id` मांगेगा और रिस्पॉन्स शो करेगा।*

---

## Vercel Deployment (वर्सेल पर डिप्लॉय करना)

इस एपीआई को इंटरनेट पर होस्ट करने के लिए:
1. **Vercel CLI** इंस्टॉल करें (यदि पहले से नहीं है):
   ```bash
   npm install -g vercel
   ```
2. प्रोजेक्ट के मेन डायरेक्टरी (`dhiraj_api/`) में जाकर यह कमांड चलाएं:
   ```bash
   vercel
   ```
3. वर्सेल के सेटअप प्रॉम्प्ट्स को फॉलो करें। डिप्लॉय होने के बाद आपको एक पब्लिक URL मिल जाएगा।
4. आप अपने वर्सेल यूआरएल पर `test_client.py` का उपयोग करके टेस्ट कर सकते हैं:
   ```bash
   python test_client.py <video_id> <your-vercel-project-url>/codex
   ```

---

## API Documentation (एपीआई विवरण)

### Endpoint: `POST /codex`

**Headers:**
`Content-Type: application/json`

**Request Payload (JSON):**
```json
{
  "vdc_id": "वीडियो_आईडी_यहाँ_लिखें",
  "user_id": "यूज़र_आईडी_यहाँ_लिखें",
  "token": "एक्टिव_जेडब्ल्यूटी_टोकन",
  "mobile": "मोबाइल_नंबर_वैकल्पिक",
  "tile_id": 0,
  "quality": "720"
}
```

**Success Response (JSON):**
```json
{
  "status": true,
  "quality": "720",
  "url": "https://stream.sanskritiias.in/..."
}
```
