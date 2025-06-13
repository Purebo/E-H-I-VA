from flask import Flask, request, jsonify, render_template, send_file
import datetime
import requests
import wikipedia
import tempfile
import os

app = Flask(__name__)

# API Configuration
together_api_key = "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs"
together_model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
together_url = "https://api.together.xyz/v1/chat/completions"
eleven_api_key = "sk_0943c49310f66aefe0841401ddbaef91860f0cb671aaefb7"
eleven_voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachael

def ask_together_ai(q):
    headers = {
        "Authorization": f"Bearer {together_api_key}",
        "Content-Type": "application/json"
    }
    sys = "You are EHI, a voice-only AI assistant. Spicy also known as spicy was taken created you to have a conscience and evolve with time. Answer short, smart, and friendly."
    data = {
        "model": together_model,
        "messages": [{"role": "system", "content": sys}, {"role": "user", "content": q}],
        "max_tokens": 200, 
        "temperature": 0.7
    }
    try:
        res = requests.post(together_url, headers=headers, json=data, timeout=15)
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
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation by taking the first option
                try:
                    summary = wikipedia.summary(e.options[0], sentences=2)
                    return jsonify({"response": f"According to Wikipedia (about {e.options[0]}): " + summary})
                except:
                    return jsonify({"response": "Topic not found or ambiguous."})
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
        
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=30)
        
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            try:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:  # Filter out keep-alive chunks
                        temp_file.write(chunk)
                temp_file.close()
                
                # Clean up the temp file after sending (Flask handles this automatically)
                def cleanup_file():
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                
                return send_file(temp_file.name, 
                               mimetype="audio/mpeg", 
                               as_attachment=False,
                               download_name="speech.mp3")
            except Exception as e:
                temp_file.close()
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                print(f"Error processing audio: {e}")
                return jsonify({"error": "Error processing audio"}), 500
        else:
            print(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Failed to get voice: {response.status_code}"}), 500
            
    except Exception as e:
        print(f"Error in speak route: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Clean up any leftover temp files on startup
def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        if filename.endswith('.mp3') and filename.startswith('tmp'):
            try:
                os.unlink(os.path.join(temp_dir, filename))
            except:
                pass

if __name__ == "__main__":
    cleanup_temp_files()
    app.run(debug=True, host="0.0.0.0", port=5000)
