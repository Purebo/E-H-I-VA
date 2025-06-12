from flask import Flask, request, jsonify, render_template, send_file
import datetime, requests, wikipedia
import tempfile
import os

app = Flask(__name__)

together_api_key = "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs"
together_model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
together_url = "https://api.together.xyz/v1/chat/completions"

eleven_api_key = "sk_0943c49310f66aefe0841401ddbaef91860f0cb671aaefb7"
eleven_voice_id = ""EXAVITQu4vr4xnSDxMaL  # Rachael

def ask_together_ai(q):
    headers = {
        "Authorization": f"Bearer {together_api_key}",
        "Content-Type": "application/json"
    }
    sys = "You are EHI, a voice-only AI assistant. Spicy also known as spicy was taken created you to have a conscience and evolve with time. Answer short, smart, and friendly."
    data = {
        "model": together_model,
        "messages": [{"role": "system", "content": sys}, {"role": "user", "content": q}],
        "max_tokens": 200, "temperature": 0.7
    }
    try:
        res = requests.post(together_url, headers=headers, json=data, timeout=15)
        return res.json()["choices"][0]["message"]["content"].strip() if res.ok else "AI couldn't reply."
    except:
        return "EHI encountered an error."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    msg = request.json.get("message", "").lower()
    if "what is the time" in msg:
        return jsonify({"response": datetime.datetime.now().strftime("%I:%M %p")})
    if "wikipedia" in msg:
        q = msg.replace("wikipedia", "").strip()
        try:
            return jsonify({"response": "According to Wikipedia: " + wikipedia.summary(q, sentences=2)})
        except:
            return jsonify({"response": "Topic not found."})
    response = ask_together_ai(msg)
    return jsonify({"response": response})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.json.get("text", "")
    headers = {
        "xi-api-key": eleven_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{eleven_voice_id}/stream"

    response = requests.post(url, headers=headers, json=data, stream=True)
    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        for chunk in response.iter_content(chunk_size=4096):
            temp_file.write(chunk)
        temp_file.close()
        return send_file(temp_file.name, mimetype="audio/mpeg")
    else:
        return jsonify({"error": "Failed to get voice"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
