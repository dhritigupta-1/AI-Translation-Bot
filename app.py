from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from googletrans import Translator, LANGUAGES
import random
import hashlib
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

translator = Translator()
users = {}

# In-memory storage for simplicity, replace with database for persistence
# Example: users = {'admin': hash_password('password')}

quiz_data = [
    {"question": "apple", "options": ["manzana", "pomme", "apfel", "mela"], "correct": "manzana", "language": "Spanish"},
    {"question": "hello", "options": ["hola", "bonjour", "ciao", "hallo"], "correct": "bonjour", "language": "French"},
    {"question": "thank you", "options": ["danke", "merci", "gracias", "spasibo"], "correct": "danke", "language": "German"},
    {"question": "good morning", "options": ["buongiorno", "buenos días", "guten Morgen", "bonjour"], "correct": "buongiorno", "language": "Italian"},
    {"question": "good night", "options": ["buenas noches", "bonne nuit", "buona notte", "boa noite"], "correct": "boa noite", "language": "Portuguese"},
    {"question": "goodbye", "options": ["adieu", "adiós", "auf Wiedersehen", "arrivederci"], "correct": "adiós", "language": "Spanish"},
    {"question": "thank you", "options": ["merci", "gracias", "danke", "spasibo"], "correct": "merci", "language": "French"},
    {"question": "sorry", "options": ["danke", "entschuldigung", "excusez-moi", "pardon"], "correct": "entschuldigung", "language": "German"},
    {"question": "good evening", "options": ["buonasera", "bonne soirée", "buenas tardes", "guten abend"], "correct": "buonasera", "language": "Italian"},
    {"question": "please", "options": ["por favor", "s'il vous plaît", "bitte", "per favore"], "correct": "por favor", "language": "Portuguese"},
    # Add more questions here as needed
]

QUIZ_QUESTION_LIMIT = 10

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles login, registration, and displays the main chat/auth page."""
    if 'username' in session:
        # Pass the LANGUAGES dictionary to the template for the dropdown
        return render_template('chat.html', languages=LANGUAGES)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
             return render_template('auth.html', error='Username and password are required.')

        if 'register' in request.form:
            if username in users:
                return render_template('auth.html', error='Username already exists.')
            else:
                # Basic validation (add more as needed)
                if len(password) < 4:
                     return render_template('auth.html', error='Password must be at least 4 characters long.')
                users[username] = hash_password(password)
                session['username'] = username
                print(f"User registered: {username}") # For debugging
                print(f"Current users: {users}")    # For debugging
                return redirect(url_for('index'))

        elif 'login' in request.form:
            hashed_pw = users.get(username)
            if hashed_pw and hashed_pw == hash_password(password):
                session['username'] = username
                print(f"User logged in: {username}") # For debugging
                return redirect(url_for('index'))
            else:
                return render_template('auth.html', error='Invalid username or password.')

    # Default GET request shows the auth page if not logged in
    return render_template('auth.html')

@app.route('/translate', methods=['POST'])
def translate():
    """Handles translation requests and chatbot responses."""
    if 'username' not in session:
        return jsonify({'error': 'Authentication required.', 'translation': 'Please log in first.'}), 401

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request. Missing message.', 'translation': "<span class='error'>Invalid request.</span>"}), 400

    message = data['message'].strip().lower()
    target_lang_name = data.get('target_language') # Get target language *name* from frontend dropdown.

    # --- Translation Logic ---
    if target_lang_name and message.startswith('translate '):
        try:
            # Extract the entire text *after* "translate "
            text_to_translate = message[len('translate '):].strip()

            # Build a lookup for language name -> code (lowercase keys)
            language_codes_lower = {name.lower(): code for code, name in LANGUAGES.items()}

            # --- Robustness: Remove redundant language specification from text ---
            # Check if the *end* of the text_to_translate looks like "to <lang>" or " <lang>"
            # This prevents translating the language name itself if user typed it redundantly.
            possible_lang_in_text_match = re.search(r'\s+(?:to\s+)?([a-z\s]+)$', text_to_translate)
            potential_lang_name_in_text = ""
            if possible_lang_in_text_match:
                potential_lang_name_in_text = possible_lang_in_text_match.group(1).strip()

            # If the potential language found in text exists in our known languages, remove it
            if potential_lang_name_in_text and potential_lang_name_in_text in language_codes_lower:
                 pattern_to_remove = r'\s+(?:to\s+)?' + re.escape(potential_lang_name_in_text) + r'$'
                 text_to_translate = re.sub(pattern_to_remove, '', text_to_translate, flags=re.IGNORECASE).strip()
            # --- End of robustness section ---


            # Ensure there's still text left to translate after potential stripping
            if not text_to_translate:
                 return jsonify({'translation': "<span class='error'>Please provide text to translate after 'translate '.</span>"})

            # Validate the target_lang_name from the dropdown
            if target_lang_name.lower() in language_codes_lower:
                target_code = language_codes_lower[target_lang_name.lower()]

                # Perform the translation
                translation = translator.translate(text_to_translate, dest=target_code)
                translated_text = translation.text

                # Check if translation actually happened or if input/output are the same
                if not translated_text or translated_text.strip().lower() == text_to_translate.lower():
                     # Detect source language to give better feedback
                     try:
                         detected_src = translator.detect(text_to_translate).lang
                         if detected_src == target_code:
                              return jsonify({'translation': f"<span class='info'>The text seems to already be in {target_lang_name}. Original: '{text_to_translate}'</span>"})
                         else:
                              # Failed for other reasons (e.g., untranslatable, API issue)
                              return jsonify({'translation': f"<span class='error'>Could not translate '{text_to_translate}' to {target_lang_name}. The text might be untranslatable or already in the target language.</span>"})
                     except Exception as detect_err:
                         print(f"Language detection error: {detect_err}")
                         # Fallback if detection fails
                         return jsonify({'translation': f"<span class='error'>Could not translate '{text_to_translate}' to {target_lang_name}. Please check the text or try again.</span>"})


                # Success! Return the translation
                return jsonify({'translation': f"<span class='translation'>Translation to {target_lang_name}: '{translated_text}'</span>"})
            else:
                # Invalid target_lang from dropdown (shouldn't happen with a proper dropdown, but good to check)
                 # Create a suggestion list (limited length)
                lang_suggestions = ", ".join(list(LANGUAGES.values())[:10]) + "..."
                return jsonify({'translation': f"<span class='error'>Oops! I don't recognize the selected language '{target_lang_name}'. Valid options include: {lang_suggestions}</span>"})

        except Exception as e:
            print(f"Translation error: {e}")
            # Provide specific error if possible, otherwise generic
            error_message = str(e)
            return jsonify({'translation': f"<span class='error'>My gears seem to be grinding. Translation failed: {error_message}</span>"})

    # --- Fallback to other commands (greetings, jokes, etc.) ---
    # Only process these if it wasn't a valid "translate ..." command
    elif message in ["hi", "hello", "good morning", "good afternoon", "good evening"]:
        greetings = ["<span class='greeting'>Greetings, traveler!</span>", "<span class='greeting'>Hello there!</span>", "<span class='greeting'>Ahoy!</span>", "<span class='greeting'>Salutations!</span>", "<span class='greeting'>Howdy!</span>"]
        reply = random.choice(greetings)
        return jsonify({'translation': reply})

    elif "how are you" in message:
        responses = ["<span class='response'>As a digital entity, I'm eternally processing! Thanks for asking.</span>", "<span class='response'>My circuits are humming nicely!</span>", "<span class='response'>I'm feeling quite creative today!</span>", "<span class='response'>Just peachy!</span>"]
        reply = random.choice(responses)
        return jsonify({'translation': reply})

    elif "goodbye" in message or "bye" in message:
        farewells = ["<span class='farewell'>Farewell, and may your travels be filled with translated wonders!</span>", "<span class='farewell'>Goodbye! Come back soon.</span>", "<span class='farewell'>Until next time!</span>", "<span class='farewell'>Adieu!</span>", "<span class='farewell'>See you later!</span>"]
        reply = random.choice(farewells)
        return jsonify({'translation': reply})

    elif "tell me a joke" in message:
        jokes = [
            "<span class='joke'>Why don't scientists trust atoms? Because they make up everything!</span>",
            "<span class='joke'>What do you call a fake noodle? An impasta!</span>",
            "<span class='joke'>Why did the scarecrow win an award? Because he was outstanding in his field!</span>",
            "<span class='joke'>What do you call a fish with no eyes? Fsh!</span>"
        ]
        reply = random.choice(jokes)
        return jsonify({'translation': reply})

    elif "tell me a fact" in message:
        facts = [
            "<span class='fact'>Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.</span>",
            "<span class='fact'>Bananas are berries, but strawberries aren't.</span>",
            "<span class='fact'>The Eiffel Tower can be 15 cm taller during the summer, due to thermal expansion.</span>",
            "<span class='fact'>A group of flamingos is called a flamboyance.</span>",
            "<span class='fact'>The shortest war in history was between Britain and Zanzibar in 1896. It lasted 38 minutes.</span>"
        ]
        reply = random.choice(facts)
        return jsonify({'translation': reply})

    else:
        # Default response if no other condition matched
        reply = "<span class='default'>I don't understand that command. Try starting your message with 'translate ' and selecting a target language, ask for a joke/fact, or say hello/goodbye.</span>"
        return jsonify({'translation': reply})
    
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Ensure that there are enough questions
    num_questions = min(10, len(quiz_data))  # Take the minimum of 10 or the number of questions available
    if request.method == 'POST':
        results = []
        score = 0
        for i in range(num_questions):  # Loop through the available number of questions
            user_answer = request.form.get(f'answer_{i}')
            correct_answer = request.form.get(f'correct_{i}')
            question = request.form.get(f'question_{i}')
            language = request.form.get(f'language_{i}')

            status = "✅ Correct!" if user_answer == correct_answer else f"❌ Incorrect (Correct: {correct_answer})"
            if user_answer == correct_answer:
                score += 1
            results.append({
                "question": f'Translate "{question}" into {language}',
                "your_answer": user_answer,
                "correct_answer": correct_answer,
                "status": status
            })

        return render_template("quiz.html", quiz_over=True, results=results, score=score)

    # Randomize the quiz questions and take the sample
    quiz_questions = random.sample(quiz_data, num_questions)  # Randomize the quiz questions
    return render_template("quiz.html", quiz_over=False, questions=quiz_questions)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            if username in users and users[username] == password:
                session['username'] = username
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials'
        elif 'register' in request.form:
            # Basic registration (no actual database storage here)
            new_username = request.form['username']
            new_password = request.form['password']
            if new_username not in users:
                users[new_username] = new_password
                session['username'] = new_username
                return redirect(url_for('home'))
            else:
                error = 'Username already exists'
    return render_template('your_html_file.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('username', None)
    return redirect(url_for('index'))

# Utility function (optional, not used in current logic but potentially useful)
def strip_html(text):
    """Removes HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@app.route('/quiz/history')
def quiz_history():
    return render_template("quiz.html", quiz_over=True, results=session.get('quiz_results', []), score=0)

if __name__ == '__main__':
    # Make sure debug=False in production
    app.run(debug=True)