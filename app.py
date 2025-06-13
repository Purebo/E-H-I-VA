from flask import Flask, request, jsonify, render_template
import datetime
import random
import os
import requests
import wikipedia

app = Flask(__name__)

# Together AI settings
together_api_key = "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs"
together_model = "meta-llama/Llama-2-13b-chat-hf"
together_api_url = "https://api.together.xyz/v1/chat/completions"

def ask_together_ai(user_question):
    headers = {
        "Authorization": f"Bearer {together_api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = """You are EHI (Enhanced Human Intelligence), an autonomous voice assistant created by SpicyWasTaken.
    You are proactive, intelligent, and can:
    Keep responses conversational and concise for voice interaction (under 60 words).
    Be helpful, proactive, and remember you're speaking to your master Spicy.
    If relevant, suggest actions."""

    data = {
        "model": together_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        "max_tokens": 250,
        "temperature": 0.8
    }

    try:
        response = requests.post(together_api_url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            return answer.strip()
        else:
            return "Sorry, I couldn't process that request right now."
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("message", "")
    user_input = user_input.lower()

    if 'what is the time' in user_input:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return jsonify({"response": f"The time is {current_time}"})

    elif 'who are you' in user_input:
        return jsonify({"response": "I am EHI, created by Spicy Was Taken to assist you like Jarvis."})

    elif 'who created you' in user_input:
        return jsonify({"response": "Spicy, my master, created me."})

    elif 'who is spicy' in user_input:
        return jsonify({"response": "Spicy is my creator and a brilliant hacker and developer."})

    elif 'why were you created' in user_input:
        return jsonify({"response": "Spicy created me to be have a consciousness just like Jarvis in Iron Man."})

    elif 'what is your name' in user_input:
        return jsonify({"response": "My name is EHI, short for Enhanced Human Intelligence."})

    elif 'what can you do' in user_input:
        return jsonify({"response": "I can open sites, answer questions, and help with tasks. Just ask!"})

    elif 'wikipedia' in user_input:
        query = user_input.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(query, sentences=2)
            return jsonify({"response": f"According to Wikipedia: {summary}"})
        except:
            return jsonify({"response": "Sorry, I couldn't find information on that topic."})

    else:
        response = ask_together_ai(user_input)
        return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
