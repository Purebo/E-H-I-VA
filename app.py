from flask import Flask, request, jsonify, render_template
import datetime, requests, wikipedia

app = Flask(__name__)

together_api_key = "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs"
together_model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
together_url = "https://api.together.xyz/v1/chat/completions"

def ask_together_ai(q):
    headers = {"Authorization": f"Bearer {together_api_key}", "Content-Type": "application/json"}
    sys = "You are EHI, a voice-only AI assistant.Spicy also known as spicywastaken created you to have a conscience and evolve with time. Answer short, smart, and friendly."
    data = {
        "model": together_model,
        "messages": [{"role":"system","content":sys},{"role":"user","content":q}],
        "max_tokens":200,"temperature":0.7
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
    return jsonify({"response": ask_together_ai(msg)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
