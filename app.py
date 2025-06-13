from flask import Flask, request, jsonify, render_template
import datetime, requests, wikipedia, os
import logging

app = Flask(__name__)

# SECURITY WARNING: Move this to environment variables!
together_api_key = os.getenv("TOGETHER_API_KEY", "0ef4d730058fe8e719347bd6ea8dd4532b72bcf5bbe5f83709ba727059bf83e9")
together_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"  # Changed to a valid model
together_url = "https://api.together.xyz/v1/chat/completions"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_together_ai(q):
    headers = {"Authorization": f"Bearer {together_api_key}", "Content-Type": "application/json"}
    sys = "You are EHI which is short for Enhanced Human Intelligence,you have an elder brother called toby ai but you were created to be smarter than him, a voice-only AI assistant created by Spicy also known as Spicy Was Taken,You were created to evolve and develop a conscience. Answer short, smart, and friendly."
    data = {
        "model": together_model,
        "messages": [{"role":"system","content":sys},{"role":"user","content":q}],
        "max_tokens": 200,
        "temperature": 0.7
    }
    try:
        logger.info(f"Making request to Together AI: {q}")
        res = requests.post(together_url, headers=headers, json=data, timeout=15)
        
        # Log response for debugging
        logger.info(f"Response status: {res.status_code}")
        logger.info(f"Response text: {res.text}")
        
        if res.ok:
            response_data = res.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Unexpected response format: {response_data}")
                return "AI response format error."
        else:
            logger.error(f"API request failed: {res.status_code} - {res.text}")
            if res.status_code == 401:
                return "Authentication failed. Check API key."
            elif res.status_code == 400:
                return "Invalid request. Check model name."
            else:
                return f"AI API error: {res.status_code}"
                
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return "EHI request timed out."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        return f"EHI network error: {str(e)}"
    except KeyError as e:
        logger.error(f"Response parsing error: {e}")
        return "EHI response parsing error."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"EHI encountered an error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Check if request has JSON data
        if not request.json:
            return jsonify({"error": "No JSON data provided"}), 400
            
        msg = request.json.get("message", "")
        if not msg:
            return jsonify({"error": "No message provided"}), 400
            
        msg_lower = msg.lower()
        logger.info(f"Received message: {msg}")
        
        # Time check
        if "what is the time" in msg_lower or "time" in msg_lower:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return jsonify({"response": f"The current time is {current_time}"})
        
        # Wikipedia check
        if "wikipedia" in msg_lower:
            q = msg_lower.replace("wikipedia", "").strip()
            if not q:
                return jsonify({"response": "What would you like me to search on Wikipedia for?"})
            try:
                wiki_summary = wikipedia.summary(q, sentences=2)
                return jsonify({"response": f"According to Wikipedia: {wiki_summary}"})
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation
                return jsonify({"response": f"Multiple topics found. Did you mean: {', '.join(e.options[:3])}?"})
            except wikipedia.exceptions.PageError:
                return jsonify({"response": "Topic not found on Wikipedia."})
            except Exception as e:
                logger.error(f"Wikipedia error: {e}")
                return jsonify({"response": "Wikipedia search encountered an error."})
        
        # Default to Together AI
        ai_response = ask_together_ai(msg)
        return jsonify({"response": ai_response})
        
    except Exception as e:
        logger.error(f"Route error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
