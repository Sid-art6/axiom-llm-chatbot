#app.py
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from logger import CustomLogger
from chatbot import Chatbot

# Global chatbot instance (persists across requests)
chatbot_instance = None

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = "your-fixed-secret-key-change-this"  # ✅ Fix 1: Fixed secret key
    logger = CustomLogger().get_logger()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        global chatbot_instance
        error_message = None

        if request.method == 'POST':
            api_key = request.form['api_key'].strip()

            if not api_key:
                return render_template('index.html', error_message="API key cannot be empty.")

            try:
                chatbot_instance = Chatbot(api_key)  # ✅ Fix 2: Store globally, init once
                session['api_key_set'] = True
                logger.info("API Key set successfully.")
                return redirect(url_for('chat'))

            except Exception as e:
                logger.error(f"Error setting API Key: {e}")
                error_message = f"Error initializing chatbot: {str(e)}"  # ✅ Fix 3: Show real error

        return render_template('index.html', error_message=error_message)

    @app.route('/chat')
    def chat():
        if chatbot_instance is None:
            return redirect(url_for('index'))
        return render_template('chat.html')

    @app.route('/ask', methods=['POST'])
    def ask():
        global chatbot_instance

        if chatbot_instance is None:
            return jsonify({"response": "Chatbot not initialized. Please enter your API key."}), 400

        question = request.json.get('question', '').strip()
        if not question:
            return jsonify({"response": "Question cannot be empty."}), 400

        try:
            response = chatbot_instance.ask(question)  # ✅ Fix 4: Reuse existing instance
            logger.info(f"User asked: {question}")
            return jsonify({"response": response})

        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            return jsonify({"response": f"Error: {str(e)}"}), 500  # ✅ Fix 5: Real error shown

    @app.route('/logout', methods=['POST'])
    def logout():
        global chatbot_instance
        chatbot_instance = None  # ✅ Clear global instance
        session.clear()
        logger.info("Session and chatbot instance cleared.")
        return redirect(url_for('index'))

    return app