# import requests
# import json

# response = requests.post(
#     "http://localhost:11434/api/generate",
#     json={
#         "model": "qwen2.5:7b-instruct",
#         "prompt": "Analisis sentimen kalimat ini: 'Laba perusahaan naik 8% tapi outlook kuartal depan melambat.' Balas HANYA dengan JSON: {\"sentiment\": \"positive/negative/neutral\", \"confidence\": 0.0-1.0}",
#         "format": "json",
#         "stream": False
#     }
# )

# result = response.json()
# print("Raw response:", result["response"])

# parsed = json.loads(result["response"])
# print("Parsed JSON:", parsed)

import requests
import json

prompt = """Ticker: BBCA.JK

Data mentah:
Bank BCA melaporkan kenaikan laba bersih kuartalan sebesar 8% YoY. 
Beberapa analis menyoroti potensi perlambatan pertumbuhan kredit di 
sektor konsumer pada kuartal berikutnya.

Analisis data di atas dan hasilkan JSON dengan struktur PERSIS seperti ini:
{
  "summary": "ringkasan singkat temuan riset",
  "sentiment_score": <float antara -1.0 sampai 1.0>,
  "key_findings": ["temuan 1", "temuan 2"]
}"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:7b-instruct",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
)

result = response.json()
print("Raw response:", result["response"])

parsed = json.loads(result["response"])
print("\n--- Parsed ---")
print("Summary:", parsed["summary"])
print("Sentiment score:", parsed["sentiment_score"])
print("Key findings:", parsed["key_findings"])