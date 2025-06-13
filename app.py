from flask import Flask, request, jsonify, render_template, send_file
import datetime
import requests
import wikipedia
import pyttsx3
import tempfile
import os

app = Flask(__name__)

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()
engine.setProperty('voice', 'female')  # Set default voice to female (depends on system voices)
engine.setProperty('rate', 160)  # Adjust speed
engine.setProperty('volume', 1.0)  # Max volume

def ask_together_ai(q):
    headers = {
        "Authorization": f"Bearer your_together_api_key",
        "Content-Type": "application/json"
    }
    sys = "You are EHI, a voice-only AI assistant. Spicy created you to have a conscience and evolve with time. Answer short, smart, and friendly."
    data = {
        "model": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        "messages": [{"role": "system", "content": sys}, {"role": "user", "content": q}],
        "max_tokens": 200, 
        "temperature": 0.7
    }
    try:
        res = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=data, timeout=15)
        if res.ok:
            return res.json()["choices"][0]["message"]["content"].strip()
        else:
            return "AI couldn't reply."
    except Exception as e:
        print(f"Error in ask_together_ai: {e}")
        return "EHI encountered an error."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        msg = request.json.get("message", "").lower()
        
        if "what is the time" in msg:
            return jsonify({"response": datetime.datetime.now().strftime("%I:%M %p")})
        
        if "wikipedia" in msg:
            q = msg.replace("wikipedia", "").strip()
            try:
                summary = wikipedia.summary(q, sentences=2)
                return jsonify({"response": "According to Wikipedia: " + summary})
            except wikipedia.exceptions.PageError:
                return jsonify({"response": "Topic not found on Wikipedia."})
            except Exception as e:
                print(f"Wikipedia error: {e}")
                return jsonify({"response": "Error accessing Wikipedia."})
        
        response = ask_together_ai(msg)
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Error in ask route: {e}")
        return jsonify({"response": "Sorry, I encountered an error processing your request."})

@app.route("/speak", methods=["POST"])
def speak():
    try:
        text = request.json.get("text", "")
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Convert text to speech and save as temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        engine.save_to_file(text, temp_file.name)
        engine.runAndWait()

        return send_file(temp_file.name, mimetype="audio/mpeg", as_attachment=False, download_name="speech.mp3")
    
    except Exception as e:
        print(f"Error in speak route: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
